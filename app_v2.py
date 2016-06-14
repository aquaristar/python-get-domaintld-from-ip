import sys
import os
import cmd
import socket
import threading
import pickle
import time

from sys import stdout
from struct import pack, unpack

from tld import get_tld

VERSION = "0x200"
CODENAME = "Aquarius"
DEFAULT_CONFIG = dict()
CONFIG = dict()
FILES = dict()
FOLDERS = dict()

#============DEFAULT_CONFIG============#
DEFAULT_CONFIG['scan_range'] = "192.168.0.*"
DEFAULT_CONFIG['scan_port'] = "1448"
DEFAULT_CONFIG['scan_timeout'] = "5"
DEFAULT_CONFIG['scan_threads'] = "1000"
DEFAULT_CONFIG['auto_save'] = "true"
#============DEFAULT_CONFIG============#

#============FILES============#
FILES['results'] = {"folder": "output", "name":"results.txt"}
FILES['ips'] = {"folder": "output", "name":"ips.txt"}
FILES['config'] = {"folder": "nbin", "name":"config.conf"}
FILES['ips.tmp'] = {"folder": "nbin", "name":"ips.tmp"}
#============FILES============#

#============FOLDERS============#
FOLDERS['output'] = "output"
FOLDERS['input'] = "input"
FOLDERS['nbin'] = "bin"
#============FOLDERS============#

class MiscFunctions:

	def is_int(self, string):
		try:
			int(string)
			return True
		except ValueError:
			return False

	def is_float(self, string):
		try:
			float(string)
			return True
		except ValueError:
			return False

	def is_bool(self, string):
		if string.lower() in ("true", "false"):
			return True
		else:
			return False

	def save_config(self):
		Files.file_write(FILES['config'], pickle.dumps(CONFIG))

class FilesHandler:

	def __init__(self):
		self.sep = os.sep
		self.root_path = os.getcwd() + self.sep

	def file_get_contents(self, location):
		if self.file_exists(location):
			return open(location).read()
		else:
			return False

	def file_write(self, location, data="", mode="w"):
		if mode=="i":
			oldf = open(location).read()
			f = open(location, 'w')
			f.write(data.rstrip() + '\n' + oldf.rstrip())
			f.close()
		else:
			f = open(location, mode)
			f.write(data)
			f.close()

	def file_empty(self, location):
		try:
			if os.path.getsize(location) > 0:
				return False
			else:
				return True
		except OSError:
			return True

	def file_exists(self, file_path):
		return os.path.isfile(file_path)

	def dir_exists(self, dir_path):
		if os.path.exists(dir_path) and (not os.path.isfile(dir_path)):
			return True
		else:
			return False

	def dirname(self, path):
		return os.path.dirname(path)

	def mkdir(self, path):
		try:
			os.makedirs(path)
		except OSError:
			passlist

class Deploy:
	def __init__(self):
		self.deploy_folders()
		self.deploy_files()

	def deploy_folders(self):
		for (key, folder) in FOLDERS.items():
			folder = Files.root_path + folder + Files.sep
			FOLDERS[key] = folder
			if not Files.dir_exists(folder):
				Files.mkdir(folder)

	def deploy_files(self):
		for (key, file) in FILES.items():
			file = FOLDERS[file['folder']] + file['name']
			FILES[key] = file
			if not Files.file_exists(file):
				Files.file_write(file)

		if Files.file_empty(FILES['config']):
			Files.file_write(FILES['config'], pickle.dumps(DEFAULT_CONFIG))

class NetTools:

	def convert_ip(self, string):
		if self.is_ip(string.strip()):
			return [self.ip2int(string.strip())]
		else:
			return False

	def convert_range(self, string):
		if string.count('-') == 1:
			string = string.strip().split('-')
			if self.is_ip(string[0]) and self.is_ip(string[1]):
				string = [self.ip2int(x) for x in string]
				string.sort()
				return string

		elif string.count('*') in (1,2,3):
			if self.is_ip(string.replace('*', '0')):
				return [self.ip2int(string.replace('*', '0')), self.ip2int(string.replace('*', '255'))]
		else:

			return False

	def is_range(self, string):
		if string.count('-') == 1:
			string = string.strip().split('-')
			if self.is_ip(string[0]) and self.is_ip(string[1]):
				return True

		elif string.count('*') in (1,2,3):
			if self.is_ip(string.replace('*', '0')):
				return True
		else:
			return False

	def is_ip(self, address='0.0.0.0'):
		try:
			octets = address.split('.')
			if len(octets) == 4:
				ipAddr = "".join(octets)
				if ipAddr.isdigit():
					if (int(octets[0]) >= 0) and (int(octets[0]) <= 255):
						if (int(octets[1]) >= 0) and (int(octets[1]) <= 255):
							if (int(octets[2]) >= 0) and (int(octets[2]) <= 255):
								if (int(octets[3]) >= 0) and (int(octets[3]) <= 255):
									return True
		except IndexError:
			pass
		except ValueError:
			pass
		return False

	def ip2int(self, ip):
		ip = ip.split(".")
		return int("%02x%02x%02x%02x" % (int(ip[0]),int(ip[1]),int(ip[2]),int(ip[3])),16)

	def int2ip(self, integer):
		integer = "%08x" % (integer)
	   	return "%i.%i.%i.%i" % (int(integer[0:2],16),int(integer[2:4],16),int(integer[4:6],16),int(integer[6:8],16))

	def domain2tld(self, domain):
		if domain == "":
			content = content + "\n"
		else:
			content = content + get_tld("http://"+domain) + "\n"


class ScanEngine:
	def __init__(self):
		pass

	def init(self):
		global lock, semaphore
		lock = threading.Lock()
		semaphore = threading.Semaphore(int(CONFIG['scan_threads']))
		self.ips_file = open(FILES['ips'], 'a', 0)
		self.results_file = open(FILES['results'], 'a', 0)
		self.current = 0
		self.found = 0
		self.range = NetTools.convert_range(CONFIG['scan_range'])
		self.total = int(self.range[1]) - int(self.range[0])

	def Start(self):
		self.init()

		output_thread = threading.Thread(target=self.output_thread, args=())
		output_thread.daemon = True
		output_thread.start()

		try:
			integer = self.range[0]
			while integer <= self.range[1]:
				semaphore.acquire()
				thread = threading.Thread(target=self.scan_thread, args=(integer,))
				thread.daemon=True
				thread.start()
				integer += 1
				self.current += 1
		except:
			stdout.flush()
			stdout.write("\n\tSome thread related error occured, try lowering the threads amount.\n")

		while threading.active_count() > 1:
			pass

		self.ips_file.close()
		self.results_file.close()

		stdout.write("\n\nDONE! Check \"output/ips.txt\"")


	def scan_thread(self, integer):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(float(CONFIG['scan_timeout']))
			sock.connect((NetTools.int2ip(integer), int(CONFIG['scan_port'])))
			lock.acquire()
			self.found += 1
			self.ips_file.write("%s:%i\n" % (NetTools.int2ip(integer), int(CONFIG['scan_port'])))
			lock.release()
			domain=""
			try:
				domain = str(socket.gethostbyaddr(NetTools.int2ip(integer))[0])
				print domain
			except Exception:
				domain = ""
			lock.acquire()
			self.results_file.write("%s -> %s\n" % (NetTools.int2ip(integer), domain))
			lock.release()

		except:
			pass
		semaphore.release()


	def output_thread(self):
		try:
			while self.total >= self.current:
				time.sleep(0.5)
				stdout.flush()
				stdout.write("\r Current [%i/%i] Found: %i   " % (self.current, self.total, self.found))
		except:
			pass


class Interface:

	def Start(self):
		self.do_scan()

	#==========SCAN COMMAND===========#
	def do_scan(self):
		stdout.write("start scan\n")
		ScanEngine.Start()
	#==========SCAN COMMAND===========#


class MainEngine:

	def __init__(self):
		global Files, NetTools, Deploy, Interface, ScanEngine, Misc
		Files = FilesHandler()
		NetTools = NetTools()
		Deploy = Deploy()
		Misc = MiscFunctions()
		ScanEngine = ScanEngine()
		Interface = Interface()

	def Start(self):
		self.load_config()
		Interface.Start()

	def load_config(self):
		global CONFIG
		CONFIG = pickle.load(open(FILES['config']))

if __name__ == "__main__":
	try:
		MainEngine = MainEngine()
		MainEngine.Start()
	except KeyboardInterrupt:
		if CONFIG['auto_save'] == "true":
			Misc.save_config()
		sys.exit("\n\n\t...Exiting...\n")