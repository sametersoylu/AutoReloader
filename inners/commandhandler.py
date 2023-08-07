from inners.classes import *
from inners.script import AutoReload
from time import sleep
from os import system
import os
import os.path
import threading
from selenium import webdriver
import tldextract
import argparse
import inners.phpserver as phpserver
import sys
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


def handleArgs(self: AutoReload):
    parser = argparse.ArgumentParser(description="Auto Reloader")
    parser.add_argument("--Server", action="store_true", help="Sets a PHP Sever. Default is localhost:80/")
    
    reloader_group = parser.add_argument_group("Reloader Starting Arguments")
    reloader_group.add_argument("-r", "--root", help="sets the url (this argument can't be used while Server is set)")
    reloader_group.add_argument("-s", "--start_page", help="sets the start page")

    reloader_util_group = parser.add_argument_group("Reloader Utility Arguments")
    reloader_util_group.add_argument("-i", "--ignore", help="ignores provided files or paths. instead reloads the current page")
    reloader_util_group.add_argument("--ignore_html",action="store_true", help="ignores changes happened in html files. instead reloads the current page.")
    reloader_util_group.add_argument("-l", "--log", action="store_true", help="prints log to stdout")

    server_group = parser.add_argument_group("PHP Server Arguments")
    server_group.add_argument("-a", "--address", help="sets server address")
    server_group.add_argument("-p", "--port", help="sets server port")
    server_group.add_argument("-P", "--php_path", help="sets php executable path")
    server_group.add_argument("-t", "--target", help="sets php server target directory")

    args = parser.parse_args()


    if not args.Server:
        if args.address or args.target:
            parser.error("--allow flag is required to use restricted arguments")
        if args.root: 
            self._root = args.root
        if args.ignore_html: 
            self.ignore = True
        if args.log: 
            self.print = True
        if args.ignore: 
            fignore(self, args.ignore)
        
    else:
        address, target, php_path, port = "", "", "", ""
        if args.root: 
            parser.error("This argument can not be used while Server is set!")
        if args.address:
            address = args.address
            self._root = args.address
        if args.target: 
            target = args.target
        if args.php_path: 
            php_path = args.php_path
        if args.port: 
            port = args.port

        self._Server = phpserver.Server()
        self._Server.startServer(_root=target, ip_addr=address, port=port, php_path=php_path)
        
        
        

    if args.root:
        if not "http://" in args.root or not "https://" in args.root:
            parser.error("Please enter a valid URL! ie: https://localhost:80")
        self._root = args.root
    if args.start_page: 
        self._start_page = args.start_page
    if args.log: 
        self.print = True
    
    
    
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

def server(self: AutoReload, command: str):
    if command[0] == "status": 
        if not hasattr(self, "_Server") or not self._Server.isAlive():
            print(f"{msgHeaders.INFO} Server is dead!")
            return 0
        print(f"{msgHeaders.INFO} Server alive!")
        return 0
    if command[0] == "start":
        for i,arg in enumerate(command): 
            if (i+1) < len(command) and (arg == "-t" or arg == "-target"):
                target = command[i + 1]
                continue
            if (i+1) < len(command) and (arg == "-a" or arg == "-address"):
                address = command[i + 1]
                continue
            if (i+1) < len(command) and (arg == "-p" or arg == "-port"):
                port = command[i + 1]
                continue
            if (i+1) < len(command) and (arg == "-P" or arg == "-php_address"):
                php_path = command[i + 1]
                continue
        if hasattr(self, "_Server") and self._Server.isAlive():
            print(f"{msgHeaders.WARNING} A server is already running!")
            print(f"{msgHeaders.FAIL} Can't open server!")
            return 0
        if not hasattr(self, "_Server"): 
            self._Server = phpserver.Server()
        self._Server.startServer(_root= target if "target" in locals() else "",
                                 ip_addr= address if "address" in locals() else "",
                                 port= port if "port" in locals() else "",
                                 php_path= php_path if "php_path" in locals() else "")
        print(f"{msgHeaders.INFO} Server started!")
        return 0
    if command[0] == "stop": 
        if not hasattr(self, "_Server") or not self._Server.isAlive(): 
            print(f"{msgHeaders.FAIL} Server already closed!")
            return 0
        self._Server.stopServer()
        return 0
    if command[0] == "log":
        if hasattr(self, "_Server") and self._Server.isAlive():
            if not hasattr(self, "ServerLog"): 
                self.ServerLog = True
            print(f"{msgHeaders.INFO} Server logging " + ("enabled!" if self.ServerLog else "disabled!"))
            self._Server.setLogDestination(sys.stdout) if self.ServerLog else self._Server.setLogDestination(open(os.devnull, "w"))
            self.ServerLog = not self.ServerLog
        return 0
    return 1
            

        
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

def log(self: AutoReload, res): 
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
    return 0

@staticmethod
def commandHandler(self: AutoReload, command: str):
    if command.startswith("server"):
        if len(command) == len("server") or command[len("server")] == " ":
            command = command.lstrip().removeprefix("server ").rstrip().split()
            if not server(self, command):
                return
            print(f"{msgHeaders.FAIL} Invalid usage of command!")
            print(f"{msgHeaders.INFO} Usage: \"server <keyword>\"\n       Keywords: stop, start, log and status")
            return
    
    if command.startswith("get"):
        if not len(command) == len("get") or command[len("get")] == " ":
            command = command.lstrip().removeprefix("get ").rstrip()
            if not "http" in command: 
                command = "http://" + command
            self.driver.get(command)
            self._root = command
            return 
    
    if command.startswith("page"):
        if len(command) == len("page") or command[len("page")] == " ":
            command = command.lstrip().removeprefix("page ").rstrip()
            if command[0] != '/':
                command = "/" + command
            if tldextract.extract(command).suffix != "": 
                print(f"{msgHeaders.FAIL} Please use get command to open a web site! Page command works for pages for the provided root! {tldextract.extract(command)} ")
                return
            self.driver.get(self._root + command)
            return
    
    if command.startswith("driver"):
        if not len(command) > len("driver") or command[len("driver")] == " ":
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

    if command.startswith("log"):
        if len(command) == len("log") or command[len("log")] == " ": 
            res = command.removeprefix("log ").split()
            log(self, res) 
            return
    
    if command.startswith("sys(") and command.endswith(")"):
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
        
        if hasattr(self, "_Server"): 
            self._Server.stopServer()
        self.close()

    if command == "ignore html" or command == "i-html":
        self.ignore = not self.ignore
        print(f"{msgHeaders.INFO} HTML Ignore Status: {self.ignore}\n")
        return
    
    if command == "clear ignore":
        self.ignoreArr.clear()
        print(f"{msgHeaders.WARNING}{msgHeaders.INFO} Ignore list cleared.\n")
        return
    if command.startswith("ignore"):
        if len(command) == len("ignore") or command[len("ignore")] == " ":
            fignore(self,command.removeprefix("ignore "))
            return
    if "clear cache" == command: 
        self.driver.execute_script("location.reload(true);")
        return
    if command != "":
        clear = command.split("?")
        if not os.path.isfile(clear[0]): 
            print(f"{msgHeaders.FAIL} File \"{command}\" does not exists in this directory! Also no command found with this alias! If you meant a page that isn't in directory, try \"page <target>\"")
            return
        self.driver.get(self._root + command)
        self.lastEVENT = command
        return
        
