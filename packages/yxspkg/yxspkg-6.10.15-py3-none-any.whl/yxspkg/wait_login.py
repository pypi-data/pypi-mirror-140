import os
import time
import socket
import click 
def getip(ip8 = 'www.baidu.com',timeout=900):
    afi = socket.AF_INET
    for i in range(int(timeout)):
        try:
            s=socket.socket(afi,socket.SOCK_DGRAM)
            s.connect((ip8,22))
            ip=s.getsockname()[0]
        except Exception as e:
            time.sleep(1)
            continue
        s.close()
        return True
    return False
def wait_login():
    while True:
        t = os.popen('who').read().strip()
        if len(t)<2:
            time.sleep(1)
        else:
            break
    t = t.split()
    return t

@click.command()
@click.option('--ip',default='',help="是否等待网络连接")
def main(ip):
    s = wait_login()
    if ip:
        t = getip(ip)
if __name__=='__main__':
    main()