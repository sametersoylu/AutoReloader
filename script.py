import os
if os.name == "nt":
    print("WINDOWS DETECTED! PLEASE DO NOT USE THIS SCRIPT ON WINDOWS! IT'S TOO BUGGY!")
    from pyreadline3 import Readline
    #exit()
else: 
    import readline
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import os.path
import threading
from classes import *


class AutoReload: 
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
        self.ignore = False
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

    def browserCheck(self, alive = True):
        while alive: 
            if not self.isBrowserAlive(): 
                print(f"\n{msgHeaders.WARNING} Driver closed!")
                alive = False
            sleep(1)
