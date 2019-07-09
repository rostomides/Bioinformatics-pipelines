#!/usr/bin/python3


import os
import sys

raw_files = sys.argv[1]
#output_bioms = sys.argv[2]


#Change to the raw files folder
os.chdir(raw_files)

#Create a log file that contains the name of the unprocessed fastq files (in case of errors)
unprocessed = open("log_file.txt", "w")
unprocessed.close()

print("-------------------Processing ongoing-------------------------")


#Collecting the list of folders containing the fastq pairs
reads = os.listdir("fastq") 
reads.sort()

samples = {}

for i in reads:
	sample = i.split("_")[0]
	if not sample in samples:
		if "_1" in i: 
			samples[sample] = {"f": i}
		else: 
			samples[sample] = {"r": i}

	else:
		if "_1" in i: 
			samples[sample]["f"] = i
		else: 
			samples[sample]["r"] = i

#Change the working directory to the sample's directory
os.chdir("fastq")
os.system('mkdir tmp')
count = 0
for i in samples:
	#Test if there are both R1 and R2
	if len(samples[i]) < 2:
		continue

	#Joining the paired-end reads
	#os.system("join_paired_ends.py -f $PWD/" + samples[i]["f"] + " -r $PWD/" + samples[i]["r"] + " -o $PWD/fastq-join_joined")
	
	#Dimupltiplexing
	#os.system("split_libraries_fastq.py -i fastq-join_joined/fastqjoin.join.fastq --sample_ids " + i + " -o fastq-join_joined/slout/ -q 19 --barcode_type 'not-barcoded' --phred_offset 33")
	
	os.system("cat " +  samples[i]["f"] + " " + samples[i]["r"] + " >tmp/" + i + ".fastq.gz")

	

	os.system("split_libraries_fastq.py -i " +  "tmp/" + i + ".fastq.gz" + " --sample_ids " + i + " -o fastq-join_joined/slout/ -q 19 --barcode_type 'not-barcoded' --phred_offset 33")



	with open('fastq-join_joined/slout/seqs.fna', 'r') as file:
    		data = file.read().replace('>._[12]', '>' + i)

	OUT = open('fastq-join_joined/slout/seqs.fna', 'w')
	OUT.write(data)
	OUT.close()

	#OTU Picking
	os.system("pick_closed_reference_otus.py -i $PWD/fastq-join_joined/slout/seqs.fna -o $PWD/fastq-join_joined/slout/otus_w_tax/") 

	#Checking if otu_table.biom has been created (defaut OTU file create by qiime)
	files = os.listdir("fastq-join_joined/slout/otus_w_tax/")

	if "otu_table.biom" in files:

		#Moving the biom file to the output bioms folder
		os.system("cp fastq-join_joined/slout/otus_w_tax/otu_table.biom ../bioms/" + i + ".biom")
		
		unprocessed = open("../log_file.txt", "a")
		unprocessed.write(i + "\tProcessed successfully\n")
		unprocessed.close()

		os.system("mv " + samples[i]["f"] + " ../processed")
		os.system("mv " + samples[i]["r"] + " ../processed")

		#Removing the fastq-join_joined directory	
		os.system("rm fastq-join_joined -r")

	else:
		os.system("rm fastq-join_joined/slout/otus_w_tax/ -r")
		#Reverse complement the seqs.fna: this is necessary for files from old sequencing technologies
		os.system("adjust_seq_orientation.py -i fastq-join_joined/slout/seqs.fna -o fastq-join_joined/slout/rc_seqs.fna")
							
		#OTU Picking
		os.system("pick_closed_reference_otus.py -i $PWD/fastq-join_joined/slout/rc_seqs.fna -o $PWD/fastq-join_joined/slout/otus_w_tax/ -f") 

		files = os.listdir("fastq-join_joined/slout/otus_w_tax/")
			
		if "otu_table.biom" in files:
			#Moving the biom file to the output bioms folder
			os.system("cp fastq-join_joined/slout/otus_w_tax/otu_table.biom ../bioms/" + i + ".biom")

			unprocessed = open("../log_file.txt", "a")
			unprocessed.write(i + "\tProcessed successfully\n")
			unprocessed.close()

			os.system("mv " + samples[i]["f"] + " ../processed")
			os.system("mv " + samples[i]["r"] + " ../processed")

			#Removing the fastq-join_joined directory	
			os.system("rm fastq-join_joined -r")
			

		else:
			#The sample could not be processed. Add its name to the log file.
			
			unprocessed = open("../log_file.txt", "a")
			unprocessed.write(i + "\tProcessing Failed\n")
			unprocessed.close()
		
			#Removing the fastq-join_joined directory
			os.system("rm fastq-join_joined -r")
			
			#Go back to main folder
	
			


#merge bioms
print "\n\nMerging bioms\n\n"
os.chdir("../bioms")

bioms = os.listdir("./")

print("merge_otu_tables.py -i " + ",".join(bioms) + " -o ../../00_study_bioms/" + raw_files[:-1] + ".biom")
os.system("merge_otu_tables.py -i " + ",".join(bioms) + " -o ../../00_study_bioms/" + raw_files[:-1] + ".biom")
	
print ("-------------------End of the script-------------------")	
	



	





















