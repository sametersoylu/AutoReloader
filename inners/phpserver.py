import subprocess, os, pexpect
from time import sleep
from inners.classes import *
import sys
import threading
if os.name == "nt": 
    import multiprocess as mp
else: 
    import multiprocessing as mp

class Server:
    def serverCheck(self, alive = True): 
        while alive: 
            if not self.isAlive(): 
                print(f"\n{msgHeaders.WARNING} Server stopped!")
                alive = False
            sleep(1)

    def isAlive(self):
        try: 
            return self.serverProc.isalive()
        except: 
            return self.elevator.is_alive()

    def elevatedProc(self, cmd, passw):
        self.serverProc = pexpect.spawn(cmd, encoding='utf8', timeout=None, env=os.environ.copy())
        try: 
            self.serverProc.expect("sudo", 1)
            self.serverProc.sendline(passw)
        except: 
            pass
        self.serverProc.expect(pexpect.EOF)

    def setLogDestination(self,stream): 
        self.serverProc.logfile = stream

    def startServer(self, _root: str = "",php_path: str =  "", ip_addr: str = "127.0.0.1", port: str = "80"): 
        if os.name == "nt": 
            if php_path == "": 
                php_path = "C:\\xampp\\php\\php.exe"  
        else: 
            if php_path == "":
                php_path = "./inners/phpFiles/php -c ./inners/phpFiles/php.ini"
        args = [_root, php_path, ip_addr, port]
        defaults = ["", "", "127.0.0.1", "80"]

        for i, arg in enumerate(args):
            if arg == "": 
                args[i] = defaults[i]

        echo = subprocess.Popen([f"echo {_root}"], shell=True, stdout=subprocess.PIPE)
        _root = echo.communicate()[0].decode().replace('\n', "")
        try: 
            cmd = f"sudo {php_path} -S {args[2]}:{args[3]}" + (" -t " if not _root == "" else "") + (f"{_root}" if not _root == "" else "")
            passw = input("[sudo] password: ")
            self.elevator = Thread(target=self.elevatedProc, args=(cmd, passw))
            self.elevator.start()
        except Exception as e: 
            print(e)
            pass
        return
    
    def stopServer(self): 
        self.serverProc.terminate()
    
    def getError(self): 
        return
        

if __name__ == "__main__":
    server = Server()
    server.startServer()
    sleep(5)
    server.stopServer()


