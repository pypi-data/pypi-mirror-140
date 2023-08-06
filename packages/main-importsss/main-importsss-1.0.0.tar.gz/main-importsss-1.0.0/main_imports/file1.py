import pathlib
import threading,time,signal
import sys,os,types
from functools import *
from  colorama import *

init(autoreset=True)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    p=os.path.join(base_path, relative_path)
    print(f'file path {p}')
    return p

my_open=partial(open,encoding='utf-8')
from colorama import init,Fore
init(autoreset=True)
from queue import Queue

ENCODING='utf-8'
class Job(threading.Thread):
    threads=[]
    def __init__(self,auto=True,target=None):
        threading.Thread.__init__(self,target=target if target else None)
        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()
        self.target=target

        # ... Other thread setup code here ...
        if auto:
            self.start()
        Job.threads.append(self)
    def run(self):
        print('Thread #%s started' % self.ident)
 
        while not self.shutdown_flag.is_set():
            print('doing work',self.ident)
            # ... Job code here ...
            time.sleep(1)
 
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)

    def stop(self):
        self.shutdown_flag.set()
       

    @staticmethod
    def stop_all():
        for t in Job.threads:
            t.stop()
        for t in Job.threads:
            t.join(1)
        Job.threads=[]
class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass
 
 
def service_shutdown(signum, frame):
    print('Caught signal number  %d' % signum)
    raise ServiceExit

# signal.signal(signal.SIGTERM, service_shutdown)
# signal.signal(signal.SIGINT, service_shutdown)





container_list=Queue()

class SavePrinter:
    def __init__(self) -> None:
        self.lock=threading.Lock()
        pass

    def __call__(self, *args,**kwds) :
        txts=[str(e) for e in args]
        txt=''.join(txts)
        container=kwds.get('container')
        all_=kwds.get('msg')
        with self.lock:
            print(txt,flush=True)

        if not container:
            container_list.put(txt)
        else:
            if all_:
                container.put(txt)
            else:
                for t in txt:
                    if not t.isascii():
                        pass
                    else:
                       return
                container.put(txt)




save_print=SavePrinter()
import shlex
from subprocess import Popen, PIPE

def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, out, err

# cmd = "..."  # arbitrary external command, e.g. "python mytest.py"
# exitcode, out, err = get_exitcode_stdout_stderr(cmd)



# main()
from typing import Any
from random import choice
from glob import glob
colors=[
    Fore.GREEN,Fore.LIGHTYELLOW_EX,Fore.CYAN,Fore.LIGHTBLUE_EX,Fore.YELLOW,Fore.LIGHTGREEN_EX,Fore.LIGHTBLUE_EX
]
def get_input(prompt, default: Any = '', block: Any = True, validators=None, fa_msg='',file=False,base_path=None):
    if validators is None:
        validators = []
    color=choice(colors)
    while True:
        try:
            v = input(color + '[-] ' + prompt.upper() +f' {"blocking " if block else  ""}' + str(
                f'[ defualt {default} ]' if default or default==0 else '[do-default-value]') +  ': '.upper())
            if not v:
                if default or default==0:
                    v = default
                else:
                    if not block:
                        return v
                    else:
                        continue
            else:
                pass
            passed = 0
            print(f'Your Input {v}')
            if validators and v:
                # print('checking your input', str(v))
                for validator in validators:
                    try:
                        if validator(str(v)):
                            passed += 1
                    except Exception:
                        continue
                if passed == len(validators):
                    pass
                else:
                    print('Failed input ' + (f"must be {fa_msg}" if fa_msg else ''))
                    continue
            if v and '.txt' in str(v) or file:
                try:
                    if base_path:
                        file_path=os.path.join(base_path,v)
                    else:
                        print('no base path')
                        file_path=v
                    print(f'File path {file_path}')
                    v=file_path
                    open(file_path)
                except FileNotFoundError:
                    print('File not Found')
                    continue
            # print(f'Your Input {v}')
            return v
        except KeyboardInterrupt:
            sys.exit('bye')

        except Exception as e:
            print('Error',e)
            continue


def get_as_bytes(text):
    text=bytes(text.strip(),'utf-8')
    return text
def start_new_thread(func,*args,**kwargs):
    def inner():
            func(*args,**kwargs)

    t=threading.Thread(target=inner)
    t.start()

    return t
old_open=open
open=partial(open,encoding='utf-8')
get_file_input=partial(get_input,file=True)



from colorama import Fore,init
init(autoreset=True)

def red(*args):
    text = ''
    for arg in args:
        text +=str(arg)+ ' '
    # print(text)
    text=Fore.RED+text
    return text



def yellow(*args):
    text = ''
    for arg in args:
        text += Fore.YELLOW+str(arg)+ ' '
    # print(text)
    text = Fore.YELLOW + text
    return text


def green(*args):
    text = ''
    for arg in args:
        text += str(arg) +' '
    # print(text)
    text = Fore.GREEN + text
    return text


def cyan(*args):
    text = ''
    for arg in args:
        text += str(arg)+ ' '
    # print(text,end='')
    text = Fore.CYAN + text
    return text

def info(*args):
    text = 'Info: '
    for arg in args:
        text += Fore.CYAN+str(arg) +' '
    # print(text)
    text = Fore.CYAN + text
    return text


lock=threading.RLock()

def debug(*args,**kwargs):
    color=kwargs.get('color')
    with lock:
        txt=' '.join([str(a) for a in args])
        txt=f'[{threading.current_thread().name}]--'+txt
        if color:
            print(color+txt)
        else:
            print(txt)
        time.sleep(.2)

def red_debug(*args):
    debug(*args,color=Fore.RED)

def yellow_debug(*args):
    debug(*args,color=Fore.YELLOW)

def cyan_debug(*args):
    debug(*args, color=Fore.CYAN)
def green_debug(*args):
    debug(*args, color=Fore.GREEN)


def magneta_debug(*args):
    debug(*args,color=Fore.MAGENTA)

def blue_debug(*args):
    debug(*args,color=Fore.BLUE)


class Mylocal(threading.local):
    def __init__(self):
        super(Mylocal, self).__init__()
        self.color=''
        self.accounts=[]
        self.counter=0


def create_files(files,folder='',base_path=''):
    # save_path=f'/{folder}'
    new_files=[]
    if folder:
        print(f'folder {folder}')

        folder=os.path.join(base_path,folder)
        if not os.path.exists(folder):
            os.makedirs(folder)
    if isinstance(files,str):
        files=[files]
    if isinstance(files,list):
        for file in files:
            # print(file)
            assert isinstance(file,str)
            if not file.endswith('.txt'):
                file=file+'.txt'
            if folder:
                file_path=pathlib.Path(folder).joinpath(f'{file}')
            else:
                file_path=pathlib.Path(file)
            file_path.touch(exist_ok=True)
            new_files.append(file_path)
        return new_files
    else:
        if folder:
            file_path = pathlib.Path(folder).joinpath(f'{file}')
        else:
            file_path = pathlib.Path(file)
        f = pathlib.Path(file_path)
        f.touch(exist_ok=True)
        return f


local_storage=Mylocal()
not_load_event=threading.Event()
