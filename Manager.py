import stem
from stem.control import Controller
import subprocess
import os
import platform
import config
import time

class MultiTORManager():
    def __init__(self,connections=1):
        self.os = platform.system()
        assert connections > 0
        self.num_of_connections = connections
        self.CONNECTIONS = []
        
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
                    f.write(f"SocksPort {port} IsolateClientAddr IsolateDestAddr\n")
                    CONN = TORConnection(port)
                    self.CONNECTIONS.append(CONN)
                #MORE OPTIONS 
        #restart subprocess...
        if self.os == "Windows":
        	subprocess.run(['sc', 'stop', 'tor'], check=True)
        	subprocess.run(['sc', 'start', 'tor'], check=True)
        elif self.os == "Linux":
        	subprocess.run(['systemctl', 'restart', 'tor'], check=True)
        print("TOR service restarted")
        
    def request_new_identity(self):
    	with Controller.from_port(port=config.Torrc.CONTROL_PORT) as c:
    		c.authenticate()
    		c.signal(stem.Signal.NEWNYM)
    		print(f"Requesting new identities!")
    		
    @staticmethod
    def display_relay_info():#we will use this later for ip
    	with Controller.from_port(port=config.Torrc.CONTROL_PORT) as c:
    		c.authenticate()
    		circuits = c.get_circuits()
    		for circuit in circuits:
    			print(f"Circuit ID: {circuit.id} Status: {circuit.status} PATH: {circuit.path}")
    			for path in circuit.path:
    				print(f"	Relay: {path}")
    				relay_info = False#c.get_info(f"router/{path[0]}")
    				if relay_info:
    					print(f"	-Relay INFO: {relay_info}")
    					ip = relay_info.split()[0]
    				
    def return_addrs():
    	pass
		
class TORConnection:
	def __init__(self,PORT):
		self.PORT = PORT
		self.created = int(time.time())
		self.IP = 'UNKNOWN'
		self.usage = 0 #probably wont use this
		
if __name__ == "__main__":
	#TESTING TIME
	MultiTORManager.display_relay_info()
	MTM = MultiTORManager(3)
	time.sleep(11)
	MTM.request_new_identity()
	time.sleep(11)
	for CONN in MTM.CONNECTIONS:
		print(CONN.PORT, CONN.created, CONN.IP, CONN.usage)
	MTM.display_relay_info()
		
