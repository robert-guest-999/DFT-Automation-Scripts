from vasp_pz_elastic import summary_maker
import os
import shutil

Path = os.getcwd()
Parent = os.path.dirname(Path) + "\\"


DFT_files = os.listdir(Parent + "Calculation_Files")


os.mkdir(Path + "\\" + "Results")
os.mkdir(Path + "\\" + "Results" + "\\" + "Flagged_Crystals")


for folder in DFT_files:

    # Print the crystal name
    print(folder)

    # Define the inputs for Pierre's Code
    Elastic_Path = Parent + "Calculation_Files" + "\\" + folder + "\\" + "Elastic\OUTCAR"
    Piezo_Path = Parent + "Calculation_Files" + "\\" + folder + "\\" + "Piezo\OUTCAR"
    Output_Path = Path + "\\" + "Results" + "\\" + folder + "_output.txt"
    Flagged_Path = Path + "\\" + "Results" + "\\" + "Flagged_Crystals" + "\\" + folder + "_output.txt"

    # Run Pierre's code under the function name summary_maker
    summary_maker(Elastic_Path, Piezo_Path, Output_Path)

    # Open the newly made summary file and save it's content to a string
    Results_File = open(Output_Path)
    Results_Text = Results_File.readlines()  
    Results_File.close()

    # Save the relavent tensors to individual variables to be parsed later
    DET_row_1 = Results_Text[56].split()
    DET_row_2 = Results_Text[57].split()
    DET_row_3 = Results_Text[58].split()

    ET_row_1 = Results_Text[20].split()
    ET_row_2 = Results_Text[21].split()
    ET_row_3 = Results_Text[22].split()
    ET_row_4 = Results_Text[23].split()
    ET_row_5 = Results_Text[24].split()
    ET_row_6 = Results_Text[25].split()

    # Pull the diagonal out of the tensors
    Dielectric_Diagonal = [DET_row_1[1], DET_row_2[2], DET_row_3[3]]
    Elastic_Diagonal = [ET_row_1[1], ET_row_2[2], ET_row_3[3], ET_row_4[4], ET_row_5[5], ET_row_6[6]]

    # Iterate through the Dielectric Diagonal and move the file to flagged if needed
    flag = 0

    for i in Dielectric_Diagonal:
        if float(i) < 5:
            print("Dielectric Diagonal: " + str(i) + " < 5, move to flagged")
            shutil.move(Output_Path, Flagged_Path)
            flag = 1
            break


    # Iterate through the Elastic Diagonal and move the file to flagged if needed
    if flag > 0:
        
        for i in Elastic_Diagonal:
            if float(i) < 1:
                print("Elastic Diagonal: " + str(i) + " < 1, move to flagged")
                shutil.move(Output_Path, Flagged_Path)
                break
