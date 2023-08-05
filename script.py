import os
if os.name == "nt":
    print("WINDOWS DETECTED! PLEASE DO NOT USE THIS SCRIPT ON WINDOWS! IT'S TOO BUGGY!")
    from pyreadline3 import Readline
    #exit()
else: 
    import readline
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

import threading
import multiprocessing as mp 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class msgHeaders: 
    WARNING = f"[{bcolors.WARNING}{bcolors.BOLD}WARNING{bcolors.ENDC}]"
    INFO = f"[{bcolors.OKBLUE}{bcolors.BOLD}INFO{bcolors.ENDC}]"
    FAIL = f"[{bcolors.FAIL}{bcolors.BOLD}FAIL{bcolors.ENDC}]"
    RELOADER = f"[{bcolors.BOLD}{bcolors.OKBLUE}RELOADER{bcolors.ENDC}]"
    INPUT = f"[{bcolors.OKGREEN}{bcolors.BOLD}INPUT{bcolors.ENDC}]"

class DevNull:
    def write(self, msg):
        pass

class AutoReload: 
    def test(): 
        return "TEST WORKS!"
    def default_root(self):
        self._root = "http://127.0.0.1:80/Test/"
    def default_spage(self):
        self._start_page = "./login.php"

    def __init__(self, root:str = "", start_page: str = "", print: bool = False, handle_arg: bool = False, su: bool = False, new = True):
        if not new: 
            return
        self._root = root
        self._start_page = start_page
        self.print = print
        self.file_name = sys.argv[0]
        self.print = False
        self.ignore = False;
        self.ignoreArr = []

        self.opt = webdriver.ChromeOptions()
        if su: 
            self.opt.add_argument("--no-sandbox")
            self.opt.add_argument("--headless")
        
        if os.name == "nt": 
            self.opt.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=self.opt)
        self.observer = Observer()
        if self._root == "":
            self.default_root()
        if self._start_page == "":
            self.default_spage()
        self.lastEVENT = self._start_page
        
            
    def helpfunc(self):
        str = "Default arguments for this script is:\n"
        str += f"root: {self._root} \n"
        str += f"start_page: {self._start_page} \n\n"
        str += f"Usage: '{self.file_name} -r <root_address> -s <start_page>'\n"
        str += "-r/--root: sets the url \n-s/--start_page: sets the start page\n"
        str += "-l/--log: prints the file name if a file is changed\n"
        str += "-h/--help: prints this help message\n"
        str += "--ignore-html: won't load html files if they are changed, instead will reload the current page"
        str += "-i/--ignore \"<file(s)/path(s)>\" : won't load ignored files if they are changed, instead will reload the current page"
        return str

    class Handler(FileSystemEventHandler):
        def __init__(self, outer_instance):
            self.outer = outer_instance
        
        def on_modified(self, event):
            if self.outer.print: 
                print(f"[{bcolors.OKBLUE}{bcolors.BOLD}INFO{bcolors.ENDC}] File changed: {event.src_path}")
            for item in self.outer.ignoreArr:
                if item in event.src_path:
                    self.outer.driver.get(self.outer._root + self.outer.lastEVENT)
                    return
            if ".php" in event.src_path or (".htm" in event.src_path and self.outer.ignore == False): 
                 self.outer.driver.get(self.outer._root + event.src_path)
                 self.outer.lastEVENT = event.src_path
                 return
            if ".css" in event.src_path or ".js" in event.src_path or ".htm" in event.src_path:
                 self.outer.driver.get(self.outer._root + self.outer.lastEVENT)
                 return

    def close(self,msg = ""):
        if msg != "":
            print(msg)
        self.driver.close()
        self.observer.stop()
        self.observer.join()

    def isBrowserAlive(self):
        try:
            self.driver.current_url
            return True
        except:
            return False

    def continuousCheck(self, alive = True):
        while alive: 
            if not self.isBrowserAlive(): 
                print(f"\n{msgHeaders.WARNING} Driver closed!")
                alive = False
            sleep(1)
        
        
    def runCLI(self):
         if self._root[-1] != '/':
            self._root += '/'
         self.observer.schedule(self.Handler(self), ".", recursive=True)
         try: 
            self.observer.start()
            driverT = threading.Thread(target=self.driver.get, args=(self._root + self._start_page,))
            driverT.start()
            self.checkT = threading.Thread(target=self.continuousCheck)
            self.checkT.start()
            while True: 
                print(f"\n{msgHeaders.RELOADER} {bcolors.OKCYAN}Enter the file name to switch pages (or enter {bcolors.FAIL}{bcolors.BOLD}exit{bcolors.ENDC}{bcolors.OKCYAN} for closing script){bcolors.ENDC}")
                commandinp = input(f"{msgHeaders.INPUT} ")
                commands = commandinp.split(' & ')
                for command in commands:
                    self.commandHandler(command.rstrip())
         except KeyboardInterrupt:
             self.checkT.close()
             exit()
         except WebDriverException or NoSuchWindowException: 
             sys.stderr = DevNull()
             self.close(f"{bcolors.WARNING}Driver already closed! Nothing to do! Exiting!")
             exit()
    
    def run():
        return


        

if __name__ == "__main__":
    su = False
    if os.geteuid() == 0: 
        print(f"{bcolors.FAIL}THIS SCRIPT SHOULD NOT RUN AS SUDO (SUPER USER/ROOT). SCRIPT DOESN'T REQUIRE ANY ROOT PRIVILEGE! PRESS ANY KEY TO EXIT OR IF YOU KNOW WHAT YOU ARE DOING TYPE \"iamcautious\"!")
        inp = input("")
        if inp != "iamcautious":
            exit()
        su = True
        
    obj = AutoReload(root="http://127.0.0.1:80/Test",handle_arg=True, su=su)
    obj.runCLI()
    