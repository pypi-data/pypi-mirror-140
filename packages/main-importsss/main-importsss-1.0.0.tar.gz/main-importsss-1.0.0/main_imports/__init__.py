import time
import threading
import warnings
from queue import Empty
from pathlib import *
from urllib3 import disable_warnings
from .Extensions import  *
disable_warnings()
from threading import Thread,Event,Lock
from os import system as terminal
import requests
import socket
import traceback
import requests
import os
import sys
import bs4
from bs4 import BeautifulSoup
import random
from threading import active_count
from requests.exceptions import *
from glob import glob
from .file1 import *
from .validtors import *

class Local(threading.local):
    def __init__(self):
        super(Local, self).__init__()
        self.color=''
        self.counter=0


local_storage=Local()



# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
import sys,os
sys.path.append(os.getcwd())
from threading import Lock
import requests, uuid, time, os
from colorama import init
from termcolor import colored
import urllib3, re, oauth2, json, tweepy, string, sys
from random import choice, randint
import urllib.parse
import threading
from time import sleep

lock=threading.RLock()

# quote_plus=urllib.parse.quote_plus

init()


def random_char(y=8):
    return ('').join(choice(string.ascii_letters) for x in range(y))




def red(*args):
    text = ''
    for arg in args:
        text += colored(arg, 'red') + ' '

    return text


def yellow(*args):
    text = ''
    for arg in args:
        text += colored(arg, 'yellow') + ' '

    return text


def green(*args):
    text = ''
    for arg in args:
        text += colored(arg, 'green') + ' '

    return text


def cyan(*args):
    text = ''
    for arg in args:
        text += colored(arg, 'cyan') + ' '

    return text


def magenta(*args):
    text = ''
    for arg in args:
        text += colored(arg, 'magenta') + ' '

    return text


must_re_settings = False
save_settings = 'y'
loadsettings = ''
def get_setting(json_object=None, setting_name='', prompt='', default=None, block=False,globals={}):
    global save_settings
    var_name = setting_name
    if 'file' in setting_name:
        file = True
    else:
        file = False
    setting_name = setting_name.replace('_', '-')
    if json_object is None:
        json_object = json_object
    if loadsettings == 'n' or must_re_settings:
        globals[var_name] = get_input(prompt or setting_name, file=file, default=default,
                                        block=block if block else False)
        return globals[var_name]
    try:
        varibal = json_object[setting_name.upper()]
    except Exception as e:
        print(f'setting {setting_name.upper()} not found Enter It')
        varibal = get_input(prompt or setting_name, default=default, file=file, block=block if block else False)
        save_settings = 'y'
    return varibal


def load(settings_container=[],globals={},file='settings.json',base_path=None):
    if not base_path:
        warnings.warn('You Should Enter PAth')
        sys.exit('bye')
    if base_path:
        settings_file=Path(base_path).joinpath(file)
    else:
        settings_file=Path(file)
    settings_file.touch(exist_ok=True)
    global must_re_settings, loadsettings, save_settings
    print('must_re-settings', must_re_settings)
    json_obj = {}
    try:
        with open(settings_file, 'r') as f:
            if not f.read():
                print('Empty File')
            f.seek(0)
            json_obj = json.load(f)
            debug('#' * 30)
            debug(Fore.GREEN + f'prev settings.......')
            for key_, val in json_obj.items():
                debug(f'{key_.upper()}=={val}')
            debug('#' * 30)
            if not json_obj:
                raise ValueError('No Settings')
    except json.JSONDecodeError:
        with settings_file.open('w') as setting_f :
            data={}
            json.dump(data, setting_f, ensure_ascii=False, indent=4)
        return load()
    except ValueError as e :
        print(f'Erorr {e}')
        must_re_settings = True
    except Exception as e:
        debug(Fore.RED + f'No Prevoius Settings Detected  choose [n]: \n Error--{e.__class__}')
        traceback.print_exc()
        must_re_settings = True
        pass
    if not must_re_settings:
        loadsettings = input(Fore.BLUE + '[--]Want to load prev settings [y/n] :  ') or 'y'
    else:
        loadsettings = 'n'
    try:
        for setting_name, default_val, blocking, type_ in settings_container:
            globals[setting_name] = type_(
                get_setting(json_object=json_obj, setting_name=setting_name, default=default_val, block=blocking,globals=globals))
            print(f'{setting_name} Now {globals[setting_name]}')
            print('*' * 50)

    except Exception as e:
        debug('Error load again', e)
        traceback.print_exc()
        load()
    save_settings = input(' [--] save settings [y/n]') or 'y'
    if loadsettings == 'n' or must_re_settings:
        pass
    if save_settings == 'y':
        with open(settings_file, 'w', encoding='utf-8') as setting:
            data = {}
            for setting_name, default_val, blocking, type_ in settings_container:
                data[setting_name.replace('_', '-').upper()] = type_(globals[setting_name])
            json.dump(data, setting, ensure_ascii=False, indent=4)
            
            

def create_and_open(file,ext='.txt',base_path=None):
    if not file.endswith(ext):
        file+=ext
    if base_path:
        file=Path(base_path).joinpath(file)

    # print(f'file {file.as_posix()}')
    file=Path(file)
    file.touch(exist_ok=True)
    return file
    