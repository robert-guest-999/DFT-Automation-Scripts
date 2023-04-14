# DFT-Automation-Scripts
Includes three scripts used to create for automated DFT material characterisation calculations. Note that these files have been uploaded as a demonstration of the methods and architectures used for the purpose of assessment of an undergraduate final year project, and will not function as they are (several files above the github upload limit are required). If you would like a working copy of the relavant files please contact robert.guest999@gmail.com. 

1) Submission_File_Preparer.py takes a set of cif files as an input and uses them to create a submission folder which has the individual files required for each crystal.

2) Job_Re-submission.sh is a shell script which is run initially by Submission_File_Preparer.py to initiate each calculation, and then is run after each job finishes using Slurm dependencies.

3) Output_Analyser.py takes the OUTCAR files from the PIEZO and ELASTIC calculations and creates a set of summary text files which contain the key tensors.
