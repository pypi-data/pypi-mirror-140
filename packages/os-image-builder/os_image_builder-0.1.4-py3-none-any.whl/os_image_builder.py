#!/usr/bin/env python
#coding=utf-8

import os
import sys
import gzip
import json
import glob
import hashlib
import shlex
import shutil
import tempfile
import logging
import subprocess
from contextlib import contextmanager, ExitStack
from typing import List

import ruamel.yaml
import click
import requests

# run bash in the new os: sudo systemd-nspawn --bind /usr/bin/qemu-arm-static --bind /etc/resolv.conf  -D mnt /bin/bash
# boot into the new os: sudo systemd-nspawn --bind /usr/bin/qemu-arm-static --bind /etc/resolv.conf -D mnt -b
# run command directly in running container: nsenter --target=$(machinectl show --property Leader <name of container> | sed "s/^Leader=//") \ --mount --uts --ipc --net --pid <command>
# to add a virtual ethernet pass -n to systemd-nspawn, on guest the interface will be host0 on the host it will be ve-<name of container>, you can work with this like a 

# also export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

ROOTFS = 'rootfs'

dirname = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

def run_cmd(cmd,logpath=None,input=None,mode='ab',logfile=None,capture=False,check=False):
    print('**** Starting {} with input {}'.format(' '.join(cmd),input))
    captured = []
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    opened = False
    if logfile is None:
        if logpath is not None:
            try:
                logfile = open(logpath,mode)
                opened = True
            except:
                click.echo('Failed opening logpath %s with mode %s'%(logpath,mode))
    if logfile:
        logfile.write('**** Starting {} with inupt {}\n'.format(' '.join(cmd),input).encode('utf-8'))
    try:
        if input:
            proc.stdin.write(input.encode('utf-8'))
            proc.stdin.close()
        while proc.poll() is None:
            for line in iter(proc.stdout.readline,b''):
                logger.debug(line,file=sys.stdout)
                if logfile:
                    logfile.write(line)
                if capture:
                    captured.append(line.decode('utf-8'))
            for line in iter(proc.stderr.readline,b''):
                logger.debug(line,file=sys.stderr)
                if logfile:
                    logfile.write(line)
    finally:
        if logfile and opened:
            logfile.close()
    if check and proc.returncode != 0:
        raise Exception('Process finnished with non zero exit code')
    if capture:
        return captured

class Store(object):
    def __init__(self,path):
        self.path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)
        self.load_hashes()
        self.update_hashes()
    
    def load_hashes(self):
        try:
            with open(os.path.join(self.path,'.hashes'),'r') as f:
                self.hashes = json.loads(f.read())
        except:
            self.hashes = {}
            self.update_hashes()

    def update_hashes(self):
        for name in os.listdir(self.path):
            path = os.path.join(self.path,name)
            if not os.path.isdir(path) and not name.endswith('.log'):
                if name != '.hashes' and name not in self.hashes:
                    self.hashes[name] = self.hash(path)
        self.persist_hashes()

    def hash(self,path):
        with open(path,'rb') as inf:
            return hashlib.md5(inf.read()).hexdigest()

    def persist_hashes(self):
        with open(os.path.join(self.path,'.hashes'),'w') as f:
            f.write(json.dumps(self.hashes,indent=4))

    def add(self,path):
        name = os.path.basename(path)
        self.hashes[name] = self.hash(path)
        self.persist_hashes()

    def __contains__(self,key):
        return key in self.hashes 

def depends_on(command,option_map):
    def wrapper(f):
        def decorated(ctx,*args,**kwargs):
            defaults = ctx.parent.default_map.get(command.name)
            for key,this_key in option_map.items():
                val = kwargs.get(this_key)
                if val is not None:
                    defaults[key] = val
            ctx.invoke(command,**defaults)
            return f(ctx,*args,**kwargs)
        return decorated
    return wrapper

@click.group(chain=False)
@click.option('-c','--config-path')
@click.pass_context
def cli(ctx,config_path):
    """This script creates linux images using virtualization containers.
    """
    yaml = ruamel.yaml.YAML()
    if config_path is not None:
        basename = os.path.basename(config_path).rsplit('.')[0]
        ctx.default_map = {}
        with open(config_path,'r') as f:
            for key,value in yaml.load(f.read(),Loader=yaml.FullLoader).items():
               ctx.default_map[key.replace('_','-')] = value
        ctx.default_map[ctx.invoked_subcommand]['tag'] = basename
    if os.path.isdir('artefacts'):
        ctx.obj['STORE'] = Store('artefacts')

@cli.command()
@click.argument('path')
@click.argument('tarpath')
@click.option('--sudo',is_flag=True)
def tar_directory(path, tarpath,sudo=False,**kwargs):
    # advanced options such as numeric-owner are not supported by
    # python tarfile library - therefore we use the tar command line tool
    cmd = []
    if sudo:
        cmd.append('sudo')
    cmd.append("tar")
    cmd.append("--numeric-owner")
    cmd.extend(["-C", path])
    cmd.extend(["-acf", tarpath])
    cmd.extend(os.listdir(path))
    return run_cmd(cmd,**kwargs)

@cli.command()
@click.argument('tarpath')
@click.argument('path')
@click.option('--sudo',is_flag=True)
def untar_directory(tarpath, path,sudo=False,**kwargs):
    os.makedirs(path, exist_ok=True)
    cmd = []
    if sudo:
        cmd.append('sudo')
    cmd.append("tar")
    cmd.append("--numeric-owner")
    cmd.extend(["-C", path])
    cmd.extend(["-axf", tarpath])
    return run_cmd(cmd,**kwargs)

def download_deb_package(repo,package,key_url):
    pass

@cli.command()
@click.option('-t','--tag')
@click.option('-a','--architecture')
@click.option('-u','--key-url')
@click.option('-s','--suite')
@click.option('-k','--keep',is_flag=True)
@click.option('-m','--mirror')
@click.option('-o','--output')
@click.option('-q','--qemu-exe-path')
@click.option('--additional-keys')
@click.option('--skip-first-stage',is_flag=True)
@click.option('--skip-second-stage',is_flag=True)
@click.pass_context
def bootstrap(ctx,tag,architecture,skip_first_stage,skip_second_stage,**kwargs):
    from pretty_bad_protocol import gnupg
    workdir = ctx.obj['STORE'].path
    logfile = os.path.join(workdir,tag+'-bootstrap.log')
    tempdir = tempfile.mkdtemp(dir=workdir)
    output = kwargs.get('output') or os.path.join(workdir,tag+'-bootstrap.tar')
    with open(logfile,'wb') as log:
        try:
            rootfspath = os.path.join(tempdir,ROOTFS)
            key_data = requests.get(kwargs['key_url']).text
            keyring_file_path = os.path.join(tempdir, 'temp_keyring.gpg')
            gpg = gnupg.GPG(homedir=tempdir, keyring=keyring_file_path)
            gpg.encoding = 'utf-8'
            gpg.import_keys(key_data)
            host_architecture = subprocess.check_output(['dpkg','--print-architecture'])
            cmd = [
                'sudo',
                'debootstrap',
                '--arch=%s'%architecture,
                '--variant=minbase',
                '--include=netbase,python,sudo,systemd,gpgv,python-apt',
                '--components=main',
                '--force-check-gpg',
                '--keyring=%s'%keyring_file_path,
            ]
            if architecture != host_architecture:
                cmd.append('--foreign')
            cmd.extend([kwargs['suite'],rootfspath,kwargs['mirror']])
            if not skip_first_stage:
                # if subprocess.run(cmd).returncode != 0:
                 run_cmd(cmd,logfile=log,check=True)
            ## second stage
            # not possible to use gpg, needs package gpgv 
            # keyring_file_path_rootfs = os.path.join(rootfspath,'tmp/temp_keyring.gpg')
            # run_cmd(['sudo','cp',keyring_file_path,keyring_file_path_rootfs])
            if architecture != host_architecture and not skip_second_stage:
                qemu_target_path = os.path.join(rootfspath,'usr/bin')
                subprocess.call(['sudo','cp',kwargs['qemu_exe_path'],qemu_target_path])
                cmd = [
                    'sudo',
                    'chroot',
                    rootfspath,
                    '/debootstrap/debootstrap',
                    '--second-stage',
                    # '--keyring=%s'%keyring_file_path_rootfs,
                ]
                run_cmd(cmd,logfile=log,check=True)
            ## import keys  
            keypath = os.path.join(tempdir,ROOTFS,'tmp/public.key')
            with open(keypath,'w') as f:
                f.write(key_data)
            log.write('Adding key from {}'.format(kwargs['key_url']).encode('utf-8'))
            run_cmd(['sudo','chroot',rootfspath,'apt-key','add','/tmp/public.key'],logfile=log,check=True)
            for url in kwargs.get('additional_keys',[]):
                key_data = requests.get(url).text
                with open(keypath,'w') as f:
                    f.write(key_data)
                log.write('Adding key from {}'.format(url).encode('utf-8'))
                run_cmd(['sudo','chroot',rootfspath,'apt-key','add','/tmp/public.key'],logfile=log,check=True)
            ## delete the cache
            run_cmd(['sudo','chroot',rootfspath,'apt-get','clean'],logfile=log,check=True)
            ## tar up
            log.write('Tar rootfs to {}'.format(output).encode('utf-8'))
            tar_directory.callback(rootfspath,output,sudo=True,logfile=log)
            ctx.obj['STORE'].add(output)
        finally:
            if not kwargs.get('keep'):
                subprocess.run(['sudo','rm','-r',tempdir])


@cli.command('virtualize')
@click.option('-t','--tag')
@click.option('-i','--root-fs')
@click.option('--for-lxc')
@click.pass_context
# @depends_on(bootstrap,option_map={'name':'root_fs'})
def virtualize(ctx,tag,root_fs,for_lxc):
    if for_lxc is None:
        for_lxc = os.path.join(dirname,'for_lxc')
    workdir = ctx.obj['STORE'].path
    if root_fs is None:
        root_fs = os.path.join(workdir,tag+'-'+ROOTFS+'.tar')
    rootfs_lxc_path = os.path.join(workdir,tag+'-'+ROOTFS+'-lxc.tar')
    tempdir = tempfile.mkdtemp(dir=workdir)
    logpath = os.path.join(workdir,'virtualize %s'%tag+'.log')
    with open(logpath,'wb') as log:
        try:
            rootfs_temp_path = os.path.join(tempdir,'rootfs')
            untar_directory.callback(root_fs,rootfs_temp_path,sudo=True,check=True)
            # for dns resolution in chroot
            resolve_path = os.path.join(rootfs_temp_path,'run/systemd/resolve')
            run_cmd(['sudo','mkdir','-p',resolve_path],logfile=log,check=True)
            resolve_conf = os.path.join(rootfs_temp_path,'run/systemd/resolve/resolv.conf')
            run_cmd(['sudo','cp','/etc/resolv.conf',resolve_conf],logfile=log,check=False)
            run_cmd(['sudo','chroot',os.path.join(tempdir,'rootfs'),'apt-get','--assume-yes','install','systemd-sysv','isc-dhcp-client'])
            for path in os.listdir(for_lxc):
                if os.path.isdir(os.path.join(for_lxc,path)):
                    shutil.copytree(os.path.join(for_lxc,path),os.path.join(tempdir,path))
                else:
                    shutil.copy(os.path.join(for_lxc,path),os.path.join(tempdir,path))
            tar_directory.callback(tempdir,rootfs_lxc_path,sudo=True,check=True)
            # with tarfile.open(rootfs_lxc_path,'a') as archive:
                # archive.add('for_lxc/metadata.yaml',arcname='metadata.yaml')
                # archive.add('for_lxc/templates/hostname.tpl',arcname='templates/hostname.tpl')
                # archive.add('for_lxc/templates/hosts.tpl',arcname='templates/hosts.tpl')
            cmd = ['lxc','image','import',rootfs_lxc_path,'local:','--alias',tag]
            run_cmd(cmd,logpath=os.path.join(workdir,tag+'-virtualize.log'),mode='wb')
        finally:
            run_cmd(['sudo','rm','-r',tempdir])


@cli.command('provision',context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-t','--tag')
@click.option('-k','--keep',is_flag=True)
@click.option('-i','--input-path')
@click.option('-p','--playbook')
@click.option('-n','--name')
@click.option('--ansible-cmd')
@click.option('--ansible',default='ansible')
@click.option('--cmd')
@click.option('-g','--group',default='all')
@click.option('-w','--workdir',default='artefacts')
@click.option('--ansible-extra-vars')
@click.argument('extra-args',nargs=-1, type=click.UNPROCESSED)
def provision(workdir,name,tag,input_path,playbook,group,keep=False,**kwargs):
    if tag is None:
        tag = os.path.basename(os.path.splitext(playbook)[0])
    else:
        tag = '-'.join((tag,os.path.basename(os.path.splitext(playbook)[0])))
    if input_path is None:
        input_path = os.path.join(workdir,tag+'-bootstrap.tar')
    name = name or '-'.join((tag,group,'provision'))
    logpath = os.path.join(workdir,name+'.log')
    print('Logging goes to %s'%logpath)
    with open(logpath,'wb') as log:
        log.write('Using {:} as input\n'.format(input_path).encode('utf-8'))
        res_path = os.path.join(workdir,name+'.tar')
        tempdir = tempfile.mkdtemp(dir=workdir)
        try:
            rootfs_temp_path = os.path.join(tempdir,'rootfs')
            os.makedirs(rootfs_temp_path)
            untar_directory.callback(input_path,rootfs_temp_path,sudo=True,check=True)
            inventory_path = os.path.join(tempdir,'inventory.ini')
            with open(inventory_path,'w') as f:
                f.write('[%s]\n'%group)
                f.write(rootfs_temp_path)
                f.write(' ansible_connection=chroot')
            # apt proxy
            apt_proxy = os.path.join(rootfs_temp_path,'etc/apt/apt.conf.d/01proxy')
            run_cmd(['sudo','cp','/etc/apt/apt.conf.d/01proxy',apt_proxy],logfile=log,check=False)
            # for dns resolution in chroot (copy to both locations)
            resolve_conf = os.path.join(rootfs_temp_path,'etc/resolv.conf')
            run_cmd(['sudo','cp','/etc/resolv.conf',resolve_conf],logfile=log,check=False)
            resolve_path = os.path.join(rootfs_temp_path,'run/systemd/resolve')
            run_cmd(['sudo','mkdir','-p',resolve_path],logfile=log,check=True)
            resolve_conf = os.path.join(rootfs_temp_path,'run/systemd/resolve/resolv.conf')
            run_cmd(['sudo','cp','/etc/resolv.conf',resolve_conf],logfile=log,check=False)
            # run ansible
            if kwargs.get('ansible_cmd'):
                acmd = kwargs.get('ansible')
                cmd = ['sudo',acmd,'-i',inventory_path,'-v'] + kwargs.get('ansible_cmd').split()
            else:
                cmd = ['sudo','ansible-playbook','-i',inventory_path,playbook,'-vv'] 
            extra_args = kwargs.get('extra_args',[])
            cmd += extra_args
            extra_vars = kwargs.get('ansible_extra_vars')
            if extra_vars is not None:
                extra_vars_path = os.path.join(tempdir,'extra_vars.json')
                with open(extra_vars_path,'w') as f:
                    f.write(json.dumps(extra_vars))
                cmd.append('--extra-vars')
                cmd.append('@{0}'.format(extra_vars_path))
            try:
                run_cmd(cmd,logfile=log,check=True)
            except:
                print('Fail to run the playbook %s'%log)
                return
            # clean up
            run_cmd(['sudo','rm','-r',os.path.join(rootfs_temp_path,'run/systemd')],logfile=log,check=True)
            run_cmd(['sudo','rm','-r','-f',apt_proxy],logfile=log,check=True) # -f to supress error, if folder does not exist
            # clean apt cache
            # run_cmd(['sudo','rm','-r',os.path.join(rootfs_temp_path,'var/lib/apt/lists/*')],logfile=log,check=True)
            # run_cmd(['sudo','rm','-r',os.path.join(rootfs_temp_path,'var/cache/apt/*')],logfile=log,check=True)
            tar_directory.callback(rootfs_temp_path,res_path,sudo=True,check=True)
        finally:
            if not keep:
                run_cmd(['sudo','rm','-r',tempdir])

@cli.command('ansible-console')
@click.option('-p','--path')
@click.option('-w','--workdir',default='artefacts')
def ansible_console(path,workdir):
    tempdir = tempfile.mkdtemp(dir=workdir)
    try:
        inventory_path = os.path.join(tempdir,'inventory.ini')
        rootfs_temp_path = os.path.join(tempdir,'rootfs')
        untar_directory.callback(path,rootfs_temp_path,sudo=True,check=True)
        with open(inventory_path,'w') as f:
            f.write('[all]\n')
            f.write(rootfs_temp_path)
            f.write(' ansible_connection=chroot')
        p = subprocess.Popen(['sudo','ansible-console','-i',inventory_path],stdin=sys.stdin,stdout=sys.stdout)
        p.wait()

    finally:
        run_cmd(['sudo','rm','-r',tempdir])


@cli.command('rootfs2img')
@click.option('-t','--tag')
@click.option('-k','--keep',is_flag=True)
@click.option('--firmware-path',default='boot')
@click.option('-i','--input-path')
@click.option('-o','--output-path')
@click.option('-h','--host',default='dev')
@click.pass_context
# @depends_on(bootstrap,option_map={'name':'root_fs'})
def rootfs2img(ctx,tag,input_path,output_path,firmware_path,host='',keep=False):
    workdir = ctx.obj['STORE'].path
    if input_path is None:
        input_path = os.path.join(workdir,tag+'-'+host+'-provision.tar')
        image_file =  os.path.join(workdir,tag+'-'+host+'-provision.img')
    else:
        image_basename = os.path.splitext(input_path)[0] 
        if tag is not None:
            image_basename += '-' + tag
        image_file = image_basename + '.img'
    if output_path is not None:
        image_file = output_path
    exclude = ['var/cache/apt/archives','var/lib/apt/lists','tmp', 'root/.ansible'] # must take out 'var/cache' for lighty
    logpath = os.path.splitext(input_path)[0] + '-rootfs2img.log'
    tempdir = tempfile.mkdtemp(dir=workdir)
    with open(logpath,'wb') as log:
        try:
            rootfs_temp_path = os.path.join(tempdir,'rootfs')
            os.makedirs(rootfs_temp_path)
            untar_directory.callback(input_path,rootfs_temp_path,sudo=True,check=True)

            # add all var/cache folders to be excluded expect for lighty
            exclude.extend([os.path.join('var/cache',dir) for dir in os.listdir(os.path.join(rootfs_temp_path,'var/cache')) if dir not in ('lighttpd',)])
            exclude_path = os.path.join(tempdir,'exclude.txt')
            with open(exclude_path,'w') as exclude_f:
                for x in exclude:
                    exclude_f.write(os.path.join(os.path.relpath(rootfs_temp_path),x))
                    exclude_f.write('\n')
           
            cmd = ['sudo','du','--apparent-size','-s',rootfs_temp_path,'--block-size=1','--exclude-from',exclude_path]
            proc = subprocess.run(cmd,stdout=subprocess.PIPE)
            rootfs_size = float(proc.stdout.split()[0])
            print('size',image_file,rootfs_size)

            # calc sizes
            table_sector_size = 1
            firmware_sector_size = 128
            losetup_root_offset = table_sector_size + firmware_sector_size
            table_sectors = table_sector_size * 1024 * 1024 / 512
            firmware_sectors = firmware_sector_size * 1024 * 1024 / 512
            root_offset = table_sectors + firmware_sectors

            # The root partition is ext4.
            # This means more space than the actual used space of the chroot is used.
            # As overhead for journaling and reserved blocks 25% are added.
            root_sectors = (rootfs_size * 1.25) / 512

            image_sectors = table_sectors + firmware_sectors + root_sectors

            run_cmd(['dd','if=/dev/zero','of=%s'%image_file,'bs=512','count=%.0f'%table_sectors],logfile=log)
            run_cmd(['dd','if=/dev/zero','of=%s'%image_file,'bs=512','count=0','seek=%.0f'%image_sectors],logfile=log)
            
            inp = '%.0f,%.0f,c\n%.0f,%.0f,83\n'%(table_sectors,firmware_sectors,root_offset,root_sectors)
            run_cmd(['sfdisk','-q','-uS','-f',image_file],input=inp,logfile=log,check=True)
            losetuped = []
            mounted = []
            try:
                cmd = ['sudo','losetup','-o','%.0fM'%table_sector_size,'--sizelimit','%.0fM'%firmware_sector_size,'-f','--show',image_file]
                captured = run_cmd(cmd,capture=True,logfile=log)
                firmware_ld = ''.join(captured).strip()
                losetuped.append(firmware_ld)
                cmd = ['sudo','losetup','-o','%.0fM'%losetup_root_offset,'-f','--show',image_file]
                captured = run_cmd(cmd,capture=True,logfile=log)
                root_ld = ''.join(captured).strip()
                losetuped.append(root_ld)
                run_cmd(['sudo','mkfs.vfat','-F32',firmware_ld],logfile=log,check=True)
                run_cmd(['sudo','mkfs.ext4',root_ld],logfile=log,check=True)
                root_mnt = os.path.join(tempdir,'loop_mnt')
                os.makedirs(root_mnt)

                exclude_path = os.path.join(tempdir,'exclude.txt')
                with open(exclude_path,'w') as exclude_f:
                    for x in exclude:
                        exclude_f.write(os.path.sep+x)
                        exclude_f.write('\n')
                run_cmd(['sudo','mount',root_ld,root_mnt,'-t','ext4','-o','x-gvfs-hide'],logfile=log,check=True) 
                mounted.append(root_mnt)
                firmware_mnt = os.path.join(root_mnt,firmware_path)
                subprocess.run(['sudo','mkdir','-p',firmware_mnt])
                run_cmd(['sudo','mount','-o','x-gvfs-hide',firmware_ld,firmware_mnt],logfile=log,check=True)
                mounted.append(firmware_mnt)
                # sync
                run_cmd(['sudo','rsync','-aHAXx','--exclude-from',exclude_path,rootfs_temp_path+'/',root_mnt+'/'],logfile=log)
                # get partuuid of image partitions
                proc = subprocess.run(['dd','if=%s'%image_file,'skip=440','bs=1','count=4'],stdout=subprocess.PIPE)
                partuuid = ''.join(['%02x'%x for x in reversed(proc.stdout)])
                fstab_path = os.path.join(tempdir,'fstab') 
                with open(fstab_path,'w') as fstab:
                    fstab.write('PARTUUID=%s-02 / ext4 rw 0 1\n'%partuuid)
                    fstab.write('PARTUUID=%s-01 /%s vfat rw 0 2\n'%(partuuid,firmware_path))
                run_cmd(['sudo','cp',fstab_path,os.path.join(root_mnt,'etc/fstab')],logfile=log)
                run_cmd(['sudo','sed','-i','s/ROOTDEV/PARTUUID=%s-02/'%partuuid,os.path.join(root_mnt,firmware_path,'cmdline.txt')],logfile=log)
            finally:
                run_cmd(['sync'])
                for path in reversed(mounted):
                    run_cmd(['sudo','umount',path])
                for path in losetuped:
                    run_cmd(['sudo','losetup','-d',path])
        finally:
            if not keep:
                run_cmd(['sudo','rm','-r',tempdir])
        print('Image %s is ready'%image_file)

@contextmanager
def temp_copy(path):
    if path.endswith('.gz'):
        openfunc = gzip.open
    else:
        openfunc = open
    with tempfile.NamedTemporaryFile(mode='w+b') as temp:
        print(f'copy {path} to {temp.name}')
        with openfunc(path,'rb') as inp:
            shutil.copyfileobj(inp,temp)
        print('done')
        yield temp.name

def read_iso_offsets(path):
    out = subprocess.check_output(['sudo','fdisk','-l',path])
    pos = None
    offsets = []
    for line in out.splitlines():
        if line.startswith(b'Device'):
            pos = line.find(b'Boot') + 4, line.find(b'Start') + 5
            continue
        # print(line)
        if pos is not None:
            value = line[pos[0]:pos[1]].strip()
            if value:
                # print(value)
                offsets.append(int(value)*512)
    return offsets

@contextmanager
def loop_mounted(input_path,mountpath,offset=0):
    print(f'mount {input_path}:{offset} to {mountpath}')
    try:
        print(f'losetup {input_path}:{offset}')
        cmd = ['sudo','losetup','-o','%s'%offset,'-f','--show',input_path]
        captured = run_cmd(cmd,capture=True)
        ld = ''.join(captured).strip()
        print(f'mount {ld}:{mountpath}')
        run_cmd(['sudo','mount','-o','ro,x-gvfs-hide',ld,mountpath])
        try:
            yield 
        finally:
            run_cmd(['sudo','umount',mountpath])
    finally:
        run_cmd(['sudo','losetup','-d',ld])


@contextmanager
def mounted_image(imagepath,mountpath,firmware_path:str='boot'):
    # use temp copy to avoid direct image manipulation
    with temp_copy(imagepath) as input_path:
        # get offsets
        offsets = read_iso_offsets(input_path)
        losetuped = []
        mounted = []
        with ExitStack() as stack:
            stack.enter_context(loop_mounted(input_path,mountpath,offset=offsets[1]))
            firmware_mount_path = os.path.join(mountpath,firmware_path)
            # ensure firmware path
            if not os.path.exists(firmware_mount_path): 
                print(f'create {firmware_mount_path}')
                subprocess.call(['mkdir',firmware_mount_path])
            stack.enter_context(loop_mounted(input_path,firmware_mount_path,offset=offsets[0]))
            yield

@cli.command()
@click.argument('imagepath')
@click.argument('mountpath')
@click.option('--firmware-path',default='boot')
@click.option('--not-interactive',is_flag=True)
@click.pass_context
def mount_image(ctx,imagepath,mountpath,firmware_path,not_interactive):
    """ interactively mount an iso image """
    # create mount path if not existing
    if not os.path.isdir(mountpath):
        os.makedirs(mountpath)
    with mounted_image(imagepath,mountpath,firmware_path):
        input('Press ^C when you are done, waiting solong ...')

@cli.command()
@click.argument('imagepath')
@click.option('-n','--image-name')
@click.option('-p','--platform',help='the docker image architecture/platform')
@click.option('-h','--hooks',multiple=True,help='specify hooks before taring up the iso filesystem, the hook will get root fs path as argument')
def iso_to_docker(imagepath,image_name:str=None,platform:str=None,hooks:List[str]=[]):
    if not image_name:
        image_name = os.path.basename(imagepath).split('.',1)[0]
    with tempfile.TemporaryDirectory() as outdir:
        with tempfile.TemporaryDirectory() as tempdir:
            print(f'mounting iso to {tempdir}')
            with mounted_image(imagepath,tempdir):
                tar_path = os.path.join(outdir,'image.tar')
                for hook in hooks:
                    cmd =
                    if os.path.isfile(hook):
                        cmd = [hook,tempdir]
                    else:
                        cmd = shlex.split(hook) + tempdir
                    subprocess.run(cmd)
                print(f'tar the tempdir: {tempdir}')
                tar_directory.callback(tempdir,tar_path,sudo=True)
        print(f'import the {tar_path} to docker')
        cmd = ['docker','import',tar_path,image_name]
        if platform is not None:
            cmd.append('--platform')
            cmd.append(platform)
        subprocess.run(cmd)
    click.echo(f'Docker image {image_name} sucessfully created')


@cli.command()
@click.pass_context
def mount_image_cleanup(ctx):
    with open('.mount_image.temp.json','r') as _f:
        data = json.loads(_f.read())
    for path in reversed(data['mounted']):
        run_cmd(['sudo','umount',path])
    for path in data['losetuped']:
        run_cmd(['sudo','losetup','-d',path])

@cli.command()
@click.argument('path')
def read_partition_uuid(path):
    proc = subprocess.run(['sudo','dd','if=%s'%path,'skip=440','bs=1','count=4'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    partuuid = ''.join(['%02x'%x for x in reversed(proc.stdout)])
    print(partuuid)

@cli.command()
@click.argument('imagepath')
@click.argument('device')
@click.option('--use-dd',is_flag=True)
def write(imagepath,device,use_dd):
    if click.confirm('Overwrite {}'.format(device)):
        if use_dd:
            cmd = ['sudo','dd','if=%s'%imagepath,'of=%s'%device,'bs=4M','conv=fsync']
            run_cmd(cmd)
        else:
            bmap_path = os.path.splitext(imagepath)[0] + '.bmap'
            # create bmap file
            cmd = ['sudo','bmaptool','create','-o',bmap_path,imagepath]
            run_cmd(cmd)
            # copy bmap file
            cmd = ['sudo','bmaptool','copy','--bmap',bmap_path,imagepath,device]
            run_cmd(cmd)


@cli.command()
@click.argument('container_name')
@click.argument('command')
@click.option('-i','--interactive',is_flag=True)
def run_command(container_name,command,interactive):
    stdout = run_cmd(['machinectl','show','--property','Leader',container_name],capture=True)
    proc = None
    for line in stdout:
        if line.startswith('Leader='):
            proc = line.strip().split('=')[1]
    cmd = ['sudo','nsenter','--target=%s'%proc,'--mount','--uts','--ipc','--net','--pid',command]
    if interactive:
        p = subprocess.Popen(cmd,stdin=sys.stdin)
        p.wait()
    else:
        run_cmd(cmd)

@cli.command()
@click.argument('rootfs_path')
def boot_container(rootfs_path):
    run_cmd(['sudo','systemd-nspawn','--bind','/usr/bin/qemu-arm-static','--bind','/etc/resolv.conf','-D',rootfs_path,'-b'])

@cli.command()
@click.argument('rootfs_tar_path')
@click.argument('tag')
def dockerize(rootfs_tar_path,tag):
    subprocess.call('cat %s | docker import - %s'%(rootfs_tar_path,tag),shell=True)


def main():
    cli(obj={})

if __name__ == '__main__':
    main()
