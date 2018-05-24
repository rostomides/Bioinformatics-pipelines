#!/usr/bin/python3


#Author : Larbi Bedrani
#Date : 19 june 2016
#Version: 1.6


#This script allows to batch process single-end fastq files (with no barcodes) using qiime 1.9. The script assumes qiime 1.9 is installed in the linux system. This scrpit assumes that all fastq files are stored in the same folder.

import os
import sys

raw_files = sys.argv[1]
output_bioms = sys.argv[2]


#Create 2 log files, one for processed samples and the second for the unprocessed samples
unprocessed = open("Unanalyzed_samples.txt", "w")
processed = open("Analyzed_samples.txt", "w")


#Change to the folder containing the raw fastq files
os.chdir(raw_files) 

for i in os.listdir() and ".fasq" in i:
	#Dimupltiplexing
	com = ["split_libraries_fastq.py -i ", i , "--sample_ids", i.split(".fastq")[0], "-o slout/ -q 19 --barcode_type 'not-barcoded' --phred_offset 33"]
	os.system(com); com=[]
	
	#OTU Picking		
	os.system("pick_closed_reference_otus.py -i $PWD/slout/seqs.fna -o $PWD/slout/otus_w_tax/ -f") 

	#Checking if the otu table has been generated : otu_table.biom has been created?
	
	try:
		files = os.listdir("slout/otus_w_tax/")
	except:
		files=[]
	

	if "otu_table.biom" in files:

		#Moving the biom file to output biom folder	
		com = ["mv slout/otus_w_tax/otu_table.biom", output_bioms + "/" + i.split(".fastq")[0] + "biom"]
		os.system(com); com=[]

		#Updating the log file
		processed.write(i + "\t")
	
		#Remove the intermediary folder created by qiime	
		os.system("rm slout -r")		

	else:
		os.system("rm slout/otus_w_tax/ -r")
		#Reverse complement the seqs.fna: this is necessary in some cases
		os.system("adjust_seq_orientation.py -i slout/seqs.fna -o slout/rc_seqs.fna")
							
		#OTU Picking
		os.system("pick_closed_reference_otus.py -i $PWD/slout/rc_seqs.fna -o $PWD/slout/otus_w_tax/ -f") 

		try:
			files = os.listdir("slout/otus_w_tax/")
		except:
			files=[]
			
		if "otu_table.biom" in files:
			#Moving the biom file to output biom folder
			com = ["mv slout/otus_w_tax/otu_table.biom", output_bioms + "/" + i.split(".fastq")[0] + "biom"]
			os.system(com); com=[]			

			#Updating log file
			processed.write(i + " reversed \t")
			#Remove the intermediary folder created by qiime
			os.system("rm slout -r")
		else:
			#The file could not be processed, Add its name to log file
			unprocessed.write(i + "\n")
			#Remove the intermediary folder created by qiime
			os.system("rm slout -r")
	
unprocessed.close()
processed.close()


print ("End of the script")
	
	


