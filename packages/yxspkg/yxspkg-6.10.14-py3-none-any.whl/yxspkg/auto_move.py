from email.policy import default
import time,os 
import subprocess
from pathlib import Path
import click
import ftplib

global_info = [0,0]
global_setting = {'rsync_type':'rsync','ftp_server':None}
def makedirs_ftp(ftp_server,dirs):
    rr = []
    for _ in range(10):
        try:
            ftp_server.cwd(str(dirs))
            break 
        except Exception as e:
            rr.append(str(dirs))
            dirs = dirs.parent
    rr.reverse()
    for i in rr:
        ftp_server.mkd(i)
def get_ftp_server(username,host,password):
   
    ftp_server = global_setting['ftp_server']
    try:
        ftp_server.pwd()
    except:
        ftp_server = ftplib.FTP()
        ftp_server.encoding = 'utf-8'
        ftp_server.connect(host)
        ftp_server.login(username,password)
        global_setting['ftp_server'] = ftp_server
    return global_setting['ftp_server'] 
def rsync_file(filename,target_file,username,ip):
    if global_setting['rsync_type'] == 'rsync':
        cmd = f'rsync --protect-args -avPh "{filename}" "{username}@{ip}:{target_file}"'
        print("##",cmd)
        a = subprocess.call(cmd,shell=True)
        if a != 0:
            rsync_dir(global_info[0],global_info[1],username,ip)
            print("##",cmd)
            a = subprocess.call(cmd,shell=True) 
        return a
    elif global_setting['rsync_type'] == 'ftp':
        ftp_server = get_ftp_server(username,ip,global_setting['password'])
        tpath = Path(target_file)
        tdir = tpath.parent
        try:
            ftp_server.cwd(str(tdir))
        except:
            makedirs_ftp(ftp_server,tdir)
            ftp_server.cwd(str(tdir))
        bufsize = 8192
        fp = open(filename,'rb')
        # fsize = Path(filename).stat().st_size
        tname = tpath.name
        try:
            a = ftp_server.storbinary(f'STOR {tname}',fp,bufsize)
            result = 0
        except Exception as e:
            print(e)
            result = -1
        fp.close()
        ftp_server.quit()

        return result


def rsync_dir(dirname,target_dir,username,ip):
    cmd = f'rsync --protect-args -av --include="*/" --exclude="*" "{dirname}"  "{username}@{ip}:{target_dir}"'
    print("##",cmd)
    return subprocess.call(cmd,shell=True)

def auto_move(dirname,target_dir,username,ip,temp_suffix=['.js','.tail'],interval=600):

    info = dict()
    pdir = Path(target_dir)
    length_dirname = len(dirname)
    if dirname[-1] == '/':
        length_dirname -= 1
        dirname = dirname[:-1]

    global_info[0] = dirname+'/'
    if target_dir[-1] != '/':
        target_dir += '/'
    global_info[1] = target_dir
    wait_max = min(interval*5,300)
    while True:
        tt = time.time()
        for root,ds,fs in os.walk(dirname):
            pr = Path(root)
            for i in fs:
                suffix = Path(i).suffix
                if suffix in temp_suffix:
                    continue
                iname = i 
                fname = pr/iname
                size = fname.stat().st_size
                sname = str(fname)

                if sname in info:
                    info[sname]['size_old'] = info[sname]['size']
                    info[sname]['size'] = size 
                    info[sname]['time'] = tt
                    if size != info[sname]['size_old']:
                        info[sname]['time_old'] = tt
                else:
                    info[sname] = {'size':size,'time':tt,'time_old':tt,'size_old':size}
                    
        for filename in list(info.keys()):
            if temp_suffix:
                temp_exist = False 
                for its in temp_suffix:
                    temp_file = Path(filename+its)
                    t2 = temp_file.with_name('.'+temp_file.name)
                    if temp_file.is_file() or t2.is_file():
                        temp_exist = True
                if temp_exist:
                    continue
                pf = Path(filename)
                df = info[filename]
                if df['size']>1:
                    if not pf.is_file():
                        info.pop(filename)
                        continue
                else:
                    continue

                if pf.is_file() and pf.stat().st_size>1 and tt-df['time_old']>wait_max and df['size']==df['size_old']:
                    print('move file:',filename)
                    pure_name = filename[length_dirname+1:]
                    tfname = pdir/pure_name
                    a = rsync_file(filename,tfname,username,ip)
                    if a==0:
                        print('received file:',filename)
                        fp = open(filename,'w')
                        fp.close()
                    else:
                        print('rsync file error')
            else:
                raise Exception('temp_suffix error')
        print('wait ...')
        time.sleep(interval)
        if Path('stop').is_file():
            break

@click.command()
@click.option('--input_dir','-i',help='输入文件夹名称')
@click.option('--output_dir','-o',help='输出文件夹名称')
@click.option('--username','-u',default='',help='用户名')
@click.option('--host','-h',default='',help='节点')
@click.option('--suffix_temp','-s',default='.js,.tail',help='临时文件后缀')
@click.option('--time_wait','-t',default=600,help='时间间隔')
@click.option('--password','-p',default='',help='ftp所用密码')
@click.option('--ftp',default=False,help='是否使用ftp',is_flag=True)
def main(input_dir,output_dir,username,host,suffix_temp,time_wait,password,ftp):
    global_setting['password'] = password
    temp_suffix = suffix_temp
    if temp_suffix.find(',') != -1:
        temp_suffix = [i.strip() for i in temp_suffix.split(',')]
    else:
        temp_suffix = temp_suffix.split()
    ipos = output_dir.find('@')

    if ipos !=-1:
        username = output_dir[:ipos]
        host,output_dir = output_dir[ipos+1:].split(':')

    if ftp:
        global_setting['rsync_type'] = 'ftp'
    print(f'in: {input_dir}\nout: {output_dir}\nusername: {username}\nhost: {host}\ntime_wait: {time_wait}\nsuffix_temp: {temp_suffix}')
    auto_move(input_dir,output_dir,username,host,temp_suffix,time_wait)
if __name__=='__main__':
    main()
