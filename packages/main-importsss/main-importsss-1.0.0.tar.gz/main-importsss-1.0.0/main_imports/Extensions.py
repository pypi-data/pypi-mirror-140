import requests
import functools
import html,string
from .file1 import debug
def make_soap( res: requests.Response):
    return BeautifulSoup(html.unescape(res.text), 'html.parser')




def password_generator(size=8, chars=string.digits, word=False, addon=''):
    n = ''.join(random.choice(chars) for _ in range(size))
    if addon:
        n = addon + n
    if word:
        # debug(Back.BLUE+'word genrated', n)
        return n
    return n


def bad_key(method):
    @functools.wraps(method)
    def wrapper(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except ErrorsModel as e:
            if 'BAD_KEY' in e.args:
                debug('wrong api key')
                raise SystemExit("exiting")
    return wrapper
def NOCONNECTON_ERROR_SPECKER(fn):
    @functools.wraps(fn)
    @speaker
    def wrapper(*args,**kwargs):
        while True:
            try:
                return fn(*args,**kwargs)
            except requests.RequestException as e:
                debug('CONNECTION ERROR Retrying',e)

                # time.sleep(2)
                pass
    return wrapper




import sys

import requests.exceptions

import threading,time
import traceback
from functools import wraps
from colorama import Fore,init
init(autoreset=True)


class RequestException(Exception):
    pass
def no_connection_error(f):
    name=f.__qualname__
    @logger
    @wraps(f)
    def wrapper(*args,**kwargs):
        tries = 0
        while True:
            tries+=1
            if tries >5:
                break
            try:
                r=f(*args,**kwargs)
                return r
            # except requests
            except requests.exceptions.RequestException as e :
                debug(f"request error  {name}",e,f'Retry{tries}')
                # time.sleep(1)
            except RequestException as e:
                debug(f'Sim Request error {name} {f}',e)
                time.sleep(3)
            except TimeoutError:
                debug('opertaion timed out')
                return
            except Exception as e:
                if 'TRY_AGAIN_LATER' in e.args:
                    debug(f'sleeping for 20 seconds and retry again...... {name}')
                    time.sleep(20)
                elif 'ERROR_NO_OPERATIONS' in e.args:
                    return
                elif 'BANNED' in  e.args:
                    debug('User Banned Sleep 60 Seconds')
                    time.sleep(60)
                elif 'EXCEEDED_CONCURRENT_OPERATIONS' in e.args:
                    debug('many mnubers')
                    time.sleep(60)
                    return
                elif 'NO_COMPLETE_TZID' in e.args:
                    debug('NO_COMPLETE_TZID')
                    time.sleep(20)
                    return
                elif 'ERROR_WRONG_TZID' in e.args:
                    return
                elif 'WARNING_LOW_BALANCE' in e.args:
                    debug(Fore.YELLOW+'No balance')
                    sys.exit('bye')
                elif 'NO_NUMBER' in e.args:
                    debug('NO_NUMBER')
                    time.sleep(1)
                elif 'NO_BALANCE' in e.args:
                    debug('NO_BALANCE'.upper())
                    # time.sleep(4)
                    sys.exit(debug('exit thread '))
                else:
                    debug(f'unknown error on {f}   ', e)
                    traceback.print_exc()
    return wrapper
def logger(func):
    name=func.__qualname__
    @speaker
    @wraps(func)
    def wrapper(*args,**kwargs):
            result=func(*args,**kwargs)
            if result:
                # val=type(result)
                if isinstance(result,(str,int)):
                    val=result
                else:
                    val=type(result)

            else:
                val='NoneVAl'
            debug(f'{name} return {val}')
            return result
    return wrapper


def speaker(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        debug(Fore.CYAN+f'-Calling Function ',func.__qualname__)
        while True:
            try:
                 r=func(*args,**kwargs)
                 return r
            except requests.exceptions.RequestException as e:
                debug('connection error',e)
                time.sleep(1)
                continue
                # return func(*args,**kwargs)
    return wrapper

# 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