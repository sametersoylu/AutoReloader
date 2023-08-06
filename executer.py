import os
if os.name == "nt": 
    from pyreadline3 import Readline
    import multiprocess as mp
else: 
    import multiprocessing as mp 
    import readline
from six import PY3 
from time import sleep
import asyncio
from os import system, name
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import os.path
import getopt
import threading
import argparse

class Thread(threading.Thread): 
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
    def run(self): 
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            pass

if PY3: 
    from importlib import import_module, reload 
else: 
    from importlib import import_module 
 
if __name__ == '__main__': 
    script = import_module("script")
    commandhandler = import_module("commandhandler")
    reloader = script.AutoReload(root="http://localhost", start_page=" ")
    if(len(sys.argv) > 1):
        commandhandler.handleArgs(reloader)
    reloader.observer.schedule(reloader.Handler(reloader), ".", recursive=True)
    try: 
            reloader.observer.start()
            driverT = Thread(target=reloader.driver.get, args=(reloader._root + reloader._start_page,))
            driverT.start()
            reloader.checkT = Thread(target=reloader.continuousCheck)
            reloader.checkT.start()
            while True: 
                print(f"\n{script.msgHeaders.RELOADER} {script.bcolors.OKCYAN}Enter the file name to switch pages (or enter {script.bcolors.FAIL}{script.bcolors.BOLD}exit{script.bcolors.ENDC}{script.bcolors.OKCYAN} for closing script){script.bcolors.ENDC}")
                commandinp = input(f"{script.msgHeaders.INPUT} ")
                if("exit" == commandinp): 
                    commandhandler.commandHandler(reloader, "exit")
                    exit()
                commandhandler = reload(commandhandler)
                commands = commandinp.split(' & ')
                for command in commands:
                    try: 
                        commandhandler.commandHandler(reloader, command.rstrip())
                    except Exception as e:
                        print(f"An exception occured. Message: {e}")
                        pass
    except KeyboardInterrupt:
             exit()
    except WebDriverException or NoSuchWindowException: 
             sys.stderr = script.DevNull()
             reloader.close(f"{script.bcolors.WARNING}Driver already closed! Nothing to do! Exiting!")
             exit()
    except: 
        print("other except")


    
