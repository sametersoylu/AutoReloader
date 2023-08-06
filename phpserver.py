import subprocess
import os
import sys
import select 
import fcntl
import pexpect
if os.name == "nt": 
    import multiprocess as mp
else: 
    import multiprocessing as mp

class Server:
    def isAlive(self): 
        return self.serverProc.isalive()

    def elevatedProc(self, cmd, passw):
        self.serverProc = pexpect.spawn(cmd, encoding='utf8', timeout=None)
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
                php_path = "php"
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
            self.elevator = mp.Process(target=self.elevatedProc, args=(cmd, passw))
            self.elevator.start()
        except Exception as e: 
            print(e)
            pass
        return
    
    def stopServer(self): 
        self.elevator.terminate()
    
    def getError(self): 
        return
        

if __name__ == "__main__":
    server = Server()
    server.startServer()
    server.stopServer()


