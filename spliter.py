import sys

inputFile="90_25.txt"#"90_25.txt"
outputFile="part_%d.ip"

try:
	infile = open(inputFile, 'r+')
	lines = infile.readlines()
	total_lines=len(lines)
	flag=False
	counter=0

	if(total_lines<1):
		print (":::ERROR::: empty file.")
		exit()

	if(len(lines[0].split('.'))>4):
		print (":::ERROR::: ip address format error in input file.")
		exit()

	print ":::INFO::: Number of IP address - " + str(len(lines))
	
	afile_lines=int(total_lines/100) + (total_lines%100>0)

	for idx in range(100):
		outfile=open(outputFile%idx, 'wb')
		for line in lines[counter:afile_lines*(idx+1)]:
			outfile.writelines(line)
			counter=counter+1
		outfile.closed

	infile.closed	
except Exception:
	print ":::ERROR::: input file name or path"
