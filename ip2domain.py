import sys
import socket
from tld import get_tld
import threading

inputFile="ip.txt"#"90_25.txt"
outputFile="domain.txt"
ipList=[]
threads = []
content = ""
lock = threading.Lock()
c = threading.Condition()
event = threading.Event()
counter = 0
domain = ""

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
		#threads.append(t)	
		#domain = str(socket.gethostbyaddr(ip)[0])
		t.start()
		success = event.wait(5.0)
		print "{%s}  -  [%s]" % (ip, domain)
		if domain == "":
			content = content + "\n"
		else:
			content = content + get_tld("http://"+domain) + "\n"
		#lock.acquire()
		#writeFile(ip+","+get_tld("http://"+domain) + "\n", outputFile, True)
		#c.acquire()
		#print ip+","+get_tld("http://"+domain) + "\n"
		#content = content + ip+",,,,,,,,,,,," + get_tld("http://"+domain) + "\n"
		#lock.release()
		#return get_tld("http://"+domain)
	except Exception:
		#lock.acquire()
		#writeFile("\n", outputFile, True)
		#content = content + "\n"
		print ":::ERROR::: Thread {"+str(counter)+"} failed to create. IP:" + ip + "\n"
		#lock.release()
		#return ""
	#print counter


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

#writeFile("", outputFile)
for ip in ipList:
	getDomainTLD(ip)
	#t = threading.Thread(target=getDomainTLD, args=(ip,))
	#threads.append(t)
	#t.start()

# for t in threads:
#     t.join()
	#t.join()
	
writeFile(content, outputFile)
	#domaintld = getDomainTLD(ip)
	#print domaintld
	#content = content + domaintld + "\n"

print ":::INFO::: successfully completed!!!"