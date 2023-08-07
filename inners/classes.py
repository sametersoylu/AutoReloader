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

import threading
class Thread(threading.Thread): 
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        
    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            pass
