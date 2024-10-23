import stem
import subprocess
import os
import platform
import config

class MultiTORManager():
    def __init__(self,connections=1):
        self.os = platform.system()
        assert connections > 0
        self.num_of_connections = connections
        
        if self.check_for_TOR():
        	self.write_torrc()
        else:
        	print("No TOR service running, is it installed?")

    def check_for_TOR(self):
        if self.os == "Windows":
            try:
                output = subprocess.run(['sc', 'query', 'tor'], capture_output=True, text=True)
                return "RUNNING" in output.stdout or "STOPPED" in output.stdout
            except Exception as e:
                print(f"Error checking for TOR service: {e}")
                return False
        elif self.os == "Linux":
            try:
                output = subprocess.run(['systemctl', 'is-active', 'tor'], capture_output=True, text=True)
                return "active" in output.stdout.strip()
            except Exception as e:
                print(f"Error checking for TOR service")
                return False

    def write_torrc(self):
        if self.os == "Windows":
            PATH = config.Other.WINDOWS_PATH
        elif self.os == "Linux":
            PATH = config.Other.LINUX_PATH
        if os.path.exists(PATH):#breaks if no path
            with open(PATH, "w") as f:
                if config.Torrc.LOG_NOTICE_STD:
                    f.write("Log notice syslog\n")
                f.write("CookieAuthentication 1\n")
                f.write(f"ControlPort {config.Torrc.CONTROL_PORT}\n")
                for port in range(config.Torrc.START_PORT, config.Torrc.START_PORT + self.num_of_connections):
                    f.write(f"SocksPort {port}\n")
                #MORE OPTIONS 
            #restart subprocess...
        if self.os == "Windows":
        	subprocess.run(['sc', 'stop', 'tor'], check=True)
        	subprocess.run(['sc', 'start', 'tor'], check=True)
        elif self.os == "Linux":
        	subprocess.run(['systemctl', 'restart', 'tor'], check=True)
        print("TOR service restarted")

