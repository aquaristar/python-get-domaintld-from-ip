import sys
import socket
from tld import get_tld
import threading

inputFile="ip.txt"#"90_25.txt"
outputFile="results.txt"
ipList=[]
content = ""
event = threading.Event()
counter = 0
domain = ""
timeout = 5.0

def writeFile(content, file, append=False):
    if(append is True):
        fout = open(file, 'ab')
    else:
        fout = open(file, 'wb')
    fout.write(content)
    fout.close()

def readFile(file):
	try:
		f = open(file, 'r+')
		lines = f.readlines()

		if(len(lines)<1):
			print (":::ERROR::: empty file.")
			return False
		if(len(lines[0].split('.'))>4):
			print (":::ERROR::: ip address format error in input file.")
			return False

		print ":::INFO::: Number of IP address - " + str(len(lines))
		for line in lines:
			ipList.append(line.rstrip('\n'))
		f.closed
		return True
	except Exception:
		print ":::ERROR::: input file name or path"	
    	return False	

def runGetDNSByIP(ip="0.0.0.0"):
    global domain
    try:
    	domain = str(socket.gethostbyaddr(ip)[0])
    except Exception:
    	domain = ""
    event.set()

def getDomainTLD(ip="0.0.0.0"):
	if ip == "0.0.0.0" or ip == "" or ip == "\n":
		return

	global content
	global counter
	counter = counter +1
	print str(counter) + ":"

	try:
		t = threading.Thread(target=runGetDNSByIP, args=(ip,))
		t.start()
		success = event.wait(timeout)
		print "{%s}  -  [%s]" % (ip, domain)
		if domain == "":
			content = content + "\n"
		else:
			content = content + get_tld("http://"+domain) + "\n"
	except Exception:
		print ":::ERROR::: Thread {"+str(counter)+"} failed to create. IP:" + ip + "\n"





#===================== Start Program ======================#
#set arguments
if (len(sys.argv) > 1):
    for index in range(len(sys.argv)):
	    if(sys.argv[index] == '-i'):
	        inputFile = sys.argv[index+1]
	    elif(sys.argv[index] == '-o'):
	        outputFile = sys.argv[index+1]

if(readFile(inputFile)==False):
	exit()

if(len(ipList)<1):
	print ":::ERROR::: Empty input file error"
	exit()

for ip in ipList:
	getDomainTLD(ip)

writeFile(content, outputFile)


print ":::INFO::: successfully completed!!!"