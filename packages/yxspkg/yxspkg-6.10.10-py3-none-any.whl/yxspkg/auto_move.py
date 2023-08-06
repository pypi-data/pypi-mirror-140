import time,os 
import subprocess
from pathlib import Path
import click

global_info = [0,0]

def rsync_file(filename,target_file,username,ip):
    cmd = f'rsync --protect-args -avPh "{filename}" "{username}@{ip}:{target_file}"'
    a = subprocess.call(cmd,shell=True)
    if a != 0:
        rsync_dir(global_info[0],global_info[1],username,ip)
        a = subprocess.call(cmd,shell=True) 
    return a

def rsync_dir(dirname,target_dir,username,ip):
    sd = str(dirname)
    if sd[-1] != '/':
        sd += '/'
    cmd = f'rsync --protect-args -av --include="*/" --exclude="*" "{sd}"  "{username}@{ip}:{target_dir}"'
    return subprocess.call(cmd,shell=True)

def auto_move(dirname,target_dir,username,ip,temp_suffix=['.js','.tail'],interval=600):

    info = dict()
    ii = 0
    pdir = Path(target_dir)
    length_dirname = len(dirname)
    if dirname[-1] == '/':
        length_dirname -= 1
        dirname = dirname[:-1]
    global_info[0] = dirname
    global_info[1] = target_dir
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
        
        for filename in info:
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
                if pf.is_file() and pf.stat().st_size>1 and tt-df['time_old']>interval*4 and df['size']==df['size_old']:
                    print('move file:',filename)
                    pure_name = filename[length_dirname+1:]
                    tfname = str((pdir/pure_name).parent)
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
@click.option('--username',help='用户名')
@click.option('--host',help='节点')
@click.option('--temp_suffix',default='.js,.tail',help='临时文件后缀')
@click.option('--interval',default=600,help='时间间隔')
def main(input_dir,output_dir,username,host,temp_suffix,interval):
    if temp_suffix.find(',') != -1:
        temp_suffix = [i.strip() for i in temp_suffix.split(',')]
    else:
        temp_suffix = temp_suffix.split()
    auto_move(input_dir,output_dir,username,host,temp_suffix,interval)
if __name__=='__main__':
    # q = auto_move('test1','~/test1','yxs','f0')
    # print(q)
    main()