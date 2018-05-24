#!/usr/bin/python3

#Author : Larbi Bedrani
#Date : 02 September 2016
#Version: 1.2


#This script allows to batch process paired-end fastq files (with no barcodes) using qiime 1.9. The script assumes that fastq-join and qiime 1.9 are installed and added to the path. The script assumes that every pair of fastq files is in a separate folder.

import os
import sys

raw_files = sys.argv[1]
output_bioms = sys.argv[2]

#Create a log file that contains the name of the unprocessed fastq files (in case of errors)
unprocessed = open("Unanalyzed_samples", "a")

#Change to the raw files folder
os.chdir(raw_files)

#Collecting the list of folders containing the fastq pairs
reads = os.listdir() 
reads.sort()

for i in reads:
	#Change the working directory to the sample's directory
	os.chdir(i)
	#Getting the file names
	files = os.listdir()
	
	#Joining the paired-end reads
	os.system("join_paired_ends.py -f $PWD/" + files[0] + " -r $PWD/" + files[1] + " -o $PWD/fastq-join_joined")
	
	#Dimupltiplexing
	os.system("split_libraries_fastq.py -i fastq-join_joined/fastqjoin.join.fastq --sample_ids " + i + " -o fastq-join_joined/slout/ -q 19 --barcode_type 'not-barcoded' --phred_offset 33")
	
	#OTU Picking
	os.system("pick_closed_reference_otus.py -i $PWD/fastq-join_joined/slout/seqs.fna -o $PWD/fastq-join_joined/slout/otus_w_tax/") 

	#Checking if otu_table.biom has been created (defaut OTU file create by qiime)
	files = os.listdir("fastq-join_joined/slout/otus_w_tax/")

	if "otu_table.biom" in files:

		#Moving the biom file to the output bioms folder
		os.system("cp fastq-join_joined/slout/otus_w_tax/otu_table.biom " + output_bioms + "/" + i + ".biom")

		#Removing the fastq-join_joined directory	
		os.system("rm fastq-join_joined -r")

		#Go back to main folder
		os.chdir("../")

	else:
		os.system("rm fastq-join_joined/slout/otus_w_tax/ -r")
		#Reverse complement the seqs.fna: this is necessary for files from old sequencing technologies
		os.system("adjust_seq_orientation.py -i fastq-join_joined/slout/seqs.fna -o fastq-join_joined/slout/rc_seqs.fna")
							
		#OTU Picking
		os.system("pick_closed_reference_otus.py -i $PWD/fastq-join_joined/slout/rc_seqs.fna -o $PWD/fastq-join_joined/slout/otus_w_tax/ -f") 

		files = os.listdir("fastq-join_joined/slout/otus_w_tax/")
			
		if "otu_table.biom" in files:
			#Moving the biom file to the output bioms folder
			os.system("cp fastq-join_joined/slout/otus_w_tax/otu_table.biom " + output_bioms + "/" + i + ".biom")

			#Removing the fastq-join_joined directory	
			os.system("rm fastq-join_joined -r")

			#Go back to main folder
			os.chdir("../")

		else:
			#The sample could not be processed. Add its name to the log file.
			unprocessed.write(i + "\n")

			#Removing the fastq-join_joined directory
			os.system("rm fastq-join_joined -r")
			
			#Go back to main folder
			os.chdir("../")
			
unprocessed.close()
	
print ("End of the script")	
	


