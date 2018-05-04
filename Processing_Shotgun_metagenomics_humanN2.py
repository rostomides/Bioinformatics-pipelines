#Author: Larbi Bedrani
#Date: September 3, 2017
#Version: 2.6

##################################################################################################################################
#I use This script to process shotgun metagnomics reads using the popular HumanN2 pipeline. This Script assumes that HumanN2 is installed and setup in your path.
##################################################################################################################################

import sys
import os

#Getting the folder in which the raw fastq are
wd = sys.argv[1] 

#Create two arrays to store the L001 and the L002 files (This script suppose that you have 2 L001 and 2 L002 files)
L001 = []
L002 = []

#Getting file names from the working directory
files = os.listdir(wd)

#Unzip the files
for i in range(0,4):
	#First unzip the files
	com = ["gunzip", wd + "/" + files[i]]	
	os.system(" ".join(com))
	#Append the file name to either L001 or L002 array accordingly
	if "_L001_" in files[i]:
		L001.append(wd + "/" + files[i].split(".gz")[0])
	if "_L002_" in files[i]:
		L002.append(wd + "/" + files[i].split(".gz")[0])
	com = []

##################################################################################################################################
#Trimming the reads using Trimommatic (http://www.usadellab.org/cms/?page=trimmomatic). 
#The jar file is suppose to be in the same folder as the present script
##################################################################################################################################

com = ["java -jar trimmomatic-0.36.jar PE -phred33", " ".join(sorted(L001)), " ".join([wd + "/R1_L001_trimmed.fastq", "R1_L001_Junk.fastq", wd + "/R2_L001_trimmed.fastq", "R2_L001_Junk.fastq"]), "ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36"]
os.system(" ".join(com))
com = []

#Free space
os.system("rm *_L001_Junk.fastq")

com = ["java -jar trimmomatic-0.36.jar PE -phred33", " ".join(sorted(L002)), " ".join([wd + "/R1_L002_trimmed.fastq", "R1_L002_Junk.fastq", wd + "/R2_L002_trimmed.fastq", "R2_L002_Junk.fastq"]), "ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36"]

os.system(" ".join(com))
com = []

#Free space
os.system("rm *_L002_Junk.fastq")

##################################################################################################################################
#Align reads the human genome (hg19) using bowtie2. hg19/ the folder contaning the genome index files is spposed to be in the same location as the present script. I am using 8 cores for this task. Keep the non aligned reads for further processing
##################################################################################################################################

com = ["bowtie2 -x hg19/hg19 -p 8 --un-conc", wd + "/L001_unaligned.fastq -1", wd + "/R1_L001_trimmed.fastq -2",  wd + "/R2_L001_trimmed.fastq"]    
os.system(" ".join(com))
com=[]

#Free space
os.system("rm " + wd + "/*_L001_trimmed.fastq")

com = ["bowtie2 -x hg19/hg19 -p 8 --un-conc", wd + "/L002_unaligned.fastq -1", wd + "/R1_L002_trimmed.fastq -2",  wd + "/R2_L002_trimmed.fastq"]    
os.system(" ".join(com))
com=[]

#Free space
os.system("rm " + wd + "/*_L002_trimmed.fastq")

##################################################################################################################################
#Join the R1 and R2 resulting files for L001 and L002. I am using bbmerge (https://jgi.doe.gov/data-and-tools/bbtools/bb-tools-user-guide/bbmerge-guide/)
##################################################################################################################################

com =["./bbmap/bbmerge.sh in1=" + wd + "/L001_unaligned.1.fastq", "in2="+ wd + "/L001_unaligned.2.fastq", "out=" + wd + "/L001_merged.fastq", "outu=" + wd + "/L001_unmerged.fastq",  "ihist=" + wd + "/L001_ihist.txt"]

os.system(" ".join(com))
com=[]
#Free space
os.system("rm " + wd + "/L001_unaligned*.*")

com =["./bbmap/bbmerge.sh in1=" + wd + "/L002_unaligned.1.fastq", "in2="+ wd + "/L002_unaligned.2.fastq", "out=" + wd + "/L002_merged.fastq", "outu=" + wd + "/L002_unmerged.fastq",  "ihist=" + wd + "/L002_ihist.txt"]

os.system(" ".join(com))
com=[]
#Free space
os.system("rm " + wd + "/L002_unaligned*.*")

##################################################################################################################################
#Concatenate the clean aligned files from L001 and L002
##################################################################################################################################

com = ["cat", wd + "/L001_merged.fastq",  wd + "/L002_merged.fastq", ">" + wd + "/clean_sequences_humanN2.fastq"]
os.system(" ".join(com))
com=[]

#Free space
os.system("rm " + wd + "/L00*.*")


##################################################################################################################################
#Perform HumanN2 pipeline
##################################################################################################################################

com = ["humann2", "--threads 8 --input", wd + "/clean_sequences_humanN2.fastq", "--output", wd + 
"/HumanN2_output"]
os.system(" ".join(com))






