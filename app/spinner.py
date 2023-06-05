#!/usr/bin/python
import os
from pathlib import Path
import time
import argparse
import subprocess
import tempfile
import sys
import logging
import signal

def handler(signum, frame):
    exit()
    # res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    # if res == 'y':
        # exit(1)
 

def get_files(path):
    res = []
    for file in os.listdir(path):
        filepath=os.path.join(path, file)
        if os.path.isfile(filepath):
            if Path(file).suffix == '.py':
                res.append(filepath)
    return res

def main(paths):
    my_env = os.environ
    my_env["PYTHONUNBUFFERED"] = "1"
    # dir_paths =[Path(path).absolute() for path in paths]
    dir_paths =[Path(path) for path in paths]

    processes = []
    i=0
    while(True):
        if(i%20==0):
            filenames=list()
            for dir_path in dir_paths:
                filenames.extend(get_files(dir_path))
            tobe_open=set(filenames)-set([n for _,n,_ in processes])
            for file in list(tobe_open):
                f = tempfile.TemporaryFile()
                logger.info(f"starting : {file}")
                dir, filename = os.path.split(file)
                p = subprocess.Popen(['python3',filename],cwd=dir,stdout=f, stderr=f, env=my_env)
                processes.append((p,file,f))
            processes_old=processes.copy()
        i += 1

        for i,(p,n,f) in enumerate(processes_old):
            # p.wait()
            poll = p.poll()
            if poll is None:
                f.seek(0)
                msgs=f.readlines()
                for msg in msgs:
                    logger.debug(f"msg from {n} : {msg.decode().rstrip()}")
                f.truncate(0)
            else:
                logger.info(f"process {n} has ended")
                processes[i]=None
                f.close()
            if n not in filenames:
                logger.warning(f"kill {n} : removed file")
                p.kill()
        processes= [i for i in processes if i is not None]
        time.sleep(0.2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'spinner',
                    description = 'keep runing python files in folder',
                    epilog = 'example:python spinner appcode')
    parser.add_argument('path',metavar='N',nargs='+') 
    args = parser.parse_args()
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('spinner_log_info.log')
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    signal.signal(signal.SIGINT, handler)
    main(args.path)
