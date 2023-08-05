from script import bcolors, msgHeaders, AutoReload; 
from time import sleep
from os import system
import os
import os.path
import multiprocessing as mp
import threading
from selenium import webdriver
import getopt
import sys
import tldextract

def fignore(self: AutoReload, string): 
    exists = False
    res = string.split(" ")
    for file in res:
        type = "path" if os.path.isdir(file) or file[-1] == '/' else "file"; 
        file = file.removeprefix(".").removeprefix("/")
        if file == "":
            continue
        if not os.path.isfile(file) and not os.path.isdir(file):
            print(f"{msgHeaders.FAIL} {type.capitalize()} \"{file}\" does not exist!")
            continue
        for ignoring in self.ignoreArr: 
            if ignoring in file or file in ignoring: 
                print(f"{msgHeaders.WARNING} The {type} \"{file}\" is already being ignored!")
                exists = True
                break
        if exists: 
            exists = False
            continue
        self.ignoreArr.append(file)
        print(f"{msgHeaders.INFO} Ignoring {type} \"{file}\".")

def handleArg(self):
        options = "hr:s:li:"
        long_options = ["help", "root=", "start_page=", "log", "ignore-html", "ignore="]
        try: 
            arguments, values = getopt.getopt(sys.argv[1:], options, long_options)
            for currentArg, currentVal in arguments:
                if currentArg in ("-h", "--help"):
                    try: 
                        self.close()
                    except: 
                        pass
                    print(self.helpfunc())
                    exit()
                    
                elif currentArg in ("-r", "--root"):
                    if "http://" in currentVal or "https://" in currentVal:
                        self._root = currentVal
                        if self._root[-1] != '/':
                            self._root += '/'
                        continue
                    print(f"{msgHeaders.WARNING} Please enter a valid URL for root!\n{msgHeaders.INFO} Returning to default!")
                elif currentArg in ("-s", "--start_page"):
                    self._start_page = currentVal
                elif currentArg in ("-l", "--log"):
                    self.print = True
                elif currentArg in ("-i", "--ignore"):
                    fignore(self, currentVal)
                elif currentArg in ("--ignore-html"):
                    self.ignore = True
                
        except getopt.error as err:
            print( bcolors.FAIL + str(err))


def get_logs(log_path = "", row_count = 1000, hint = "", live = False):
    if os.name == "nt": 
        if log_path == "":
            log_path = "C:\\xampp\\apache\\logs\\error.log"
        system(f"powershell.exe \"Get-Content {log_path} -tail {row_count} " + ("" if not live else "-wait") + ("\"" if hint == "" else f"| Select-String '{hint}'\""))
        return 
    if log_path == "":
        log_path = "/opt/lampp/logs/error_log"
    system("tail" + ("" if not live else "-f") + f" {log_path} -n {row_count}" + ("" if hint == "" else f" | grep {hint}"))


def helpcommand():
    print("\nhelp : Prints this message. its changed") 
    print("log [keys] <values> : As default prints last 1000 lines of the apache error log file. Use -n to specify row count, -h to search a text/hint, -l to follow file changes, -p to set log path. Example usage: log -n 10 -h error -p /path/to/logFile")
    print("sys(<command>) : will use the python's system function to run commands. Be careful with this one. IT HAS DIRECT ACCESS TO YOUR SHELL AND WILL EXECUTE EVERY COMMAND EVEN IF THEY ARE DANGEROUS. DO NOT RUN THIS SCRIPT AS ROOT OR SU IF YOU WANT TO BE SAFE!")
    print("ignore <keyword(s)> : Ignores changes happened at file paths contains the keyword. Reloads the current page instead. (Use \"ignore html\" to ignore changes happened in html files. Reusing will stop ignoring.)")
    print("exit : Closes the script")
    print("driver <keyword>: Will get ChromeDriver's status and can close or start it. Keywords: start | restart | close | status")
    print("cls: Will clear terminal's output")
    print("clearfetch : will clear terminal output then execute \"neofetch\"")
    print("<file path> : If you solely enter a file path script will check for the file and if it exist it will direct you to that file. If you want to redirect a page that isn't a file in the folder use \"page <pageName>\" instead.")
    print("get <url> : Directs ChromeDriver to specified URL.")
    print("page <pageName> : Direct ChromeDriver to specified page on the specified URL.")
    print("clear ignore : Clears ignore list that's been specified by the user")




def driverStart(self: AutoReload): 
    self.driver = webdriver.Chrome(options=self.opt)
    driverT = threading.Thread(target=self.driver.get, args=(self._root + self._start_page, ))
    driverT.start()
    self.checkT = threading.Thread(target=self.continuousCheck)
    self.checkT.start()

def driver(self: AutoReload, command: str): 
    if command == "close":
        if not self.isBrowserAlive():
            print(f"{msgHeaders.FAIL} Driver is already closed!")
            return 0
        self.driver.close()
        self.checkT.join()
        return 0
    if command == "start": 
        if self.isBrowserAlive() :
            print(f"{msgHeaders.FAIL} A driver instance is already open! Please run \"close driver\" first then execute this command. Or try \"restart driver\"")
            return 0
        driverStart(self)
        print(f"{msgHeaders.INFO} Driver started!")
        return 0
    if command == "restart":
        if self.isBrowserAlive():
            self.driver.close()
            self.checkT.join()
        driverStart(self)
        print(f"{msgHeaders.INFO} Driver restarted!")
        return 0
    if "status" == command:
        print(f"{msgHeaders.INFO} Driver Status: " + (f"{bcolors.OKGREEN}Alive{bcolors.ENDC}" if self.isBrowserAlive() else f"{bcolors.FAIL}Died{bcolors.ENDC}"))
        return 0
    return 1

@staticmethod
def commandHandler(self: AutoReload, command: str):
    if "get" in command: 
        command = command.lstrip().removeprefix("get ").rstrip()
        if not "http" in command: 
            command = "http://" + command
        self.driver.get(command)
        self._root = command
        return 
    if "page" in command: 
        command = command.lstrip().removeprefix("page ").rstrip()
        if command[0] != '/':
            command = "/" + command
        if tldextract.extract(command).suffix != "": 
            print(f"{msgHeaders.FAIL} Please use get command to open a web site! Page command works for pages for the provided root! {tldextract.extract(command)} ")
            return
        self.driver.get(self._root + command)
        return
    
    if "driver" in command:
        command = command.lstrip().removeprefix("driver ").rstrip()
        if not driver(self, command): 
            return
        print(f"{msgHeaders.FAIL} Invalid usage of command!")
        print(f"{msgHeaders.INFO} Usage: \"driver <keyword>\"\n       Keywords: close, start, restart and status")
        return

    if "clearfetch" == command:
        if os.name == "nt": 
            system("cls")
            system("neofetch")
            system("echo AutoReloader"),
            return
        system("clear && neofetch && echo AutoReloader")
        return

    if "log" in command:
        res = command.removeprefix("log ").split()
        i = 0
        rowcount = "1000"
        hint = ""
        live = False 
        path = ""
        for arg in res:
            if(arg == "-n"):
                if((i + 1) < len(res) and not "-" in res[i + 1]):
                    rowcount = res[i + 1]
            if(arg == "-h"):
                if((i + 1) < len(res) and not "-" in res[i + 1]):
                    hint = res[i + 1]
            if(arg == "-l"): 
                live = True
            if(arg == "-p"):
                if((i + 1) < len(res) and not "-" in res[i + 1]):
                    path = res[i + 1]
            i += 1

        get_logs(row_count=int(rowcount), hint=hint, live=live, log_path=path)
        return
    if "sys(" in command and command[len(command) - 1]:
        system(f"{command.removeprefix('sys(').removesuffix(')')}")
        return 
    
    if command == "cls":
        if os.name == "nt": 
            system("cls")
            return
        system("clear")
        return
   
    if command == "help": 
        helpcommand()
        return
    
    if command == "exit":
        if self.isBrowserAlive():
            self.driver.close()
        self.checkT.join()
        self.close()

    if command == "ignore html" or command == "i-html":
        self.ignore = not self.ignore
        print(f"{msgHeaders.INFO} HTML Ignore Status: {self.ignore}\n")
        return
    
    if command == "clear ignore":
        self.ignoreArr.clear()
        print(f"{msgHeaders.WARNING}{msgHeaders.INFO} Ignore list cleared.\n")
        return
    
    if "ignore" in command:
        fignore(self,command.removeprefix("ignore "))
        return
    if "clear cache" in command: 
        self.driver.execute_script("location.reload(true);")
        return
    if command != "":
        clear = command.split("?")
        if not os.path.isfile(clear[0]): 
            print(f"{msgHeaders.FAIL} File or command \"{command}\" does not exists!")
            return
        self.driver.get(self._root + command)
        self.lastEVENT = command
        return
        
