How to use software:

1) Fill in the fields in the user_inputs text file. THE CODE WILL NOT WORK IF YOU DO THIS INCORRECTLY!!!

2) Upload the crystal files that you want to characterise in CIF format to the "CIF_Files" folder

3) Run the python code "DFT_Automate". This will create a master folder called "Calculation_Files"

4) The python code will prompt you to upload the "Calculation_Files" to the Supercomputer directory that you specified in the user_inputs file.

5) Once you have uploaded the folder, respond yes in the python terminal. It will then initiatite the calculations.

6) Sit back and relax as the computer does the work!


Troubleshooting:

The user_inputs file is used to specify file locations and supercomputer login details. The purpose is to minimise the need for needless repetition of steps each time a calculation is performed. You just have to input the correct details once. If you mis-spell your inputs, the code will not be able to function.

It is very important that the orginial files do not get deleted or moved around. This will mean that python cannot find them later on. The only thing that should be changed is the content of the user_inputs file and the contents of the CIF_files folder. 

 