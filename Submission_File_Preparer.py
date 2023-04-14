# import all needed modules
# open command prompt and use: py -m pip install example_module
import shutil
from pathlib import Path
from ase import io
import pandas as pd
import os
import paramiko
import pyinputplus as pyip

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module=r'ase\.io\.cif')

#------------------------------------------------------------------------------#

#INPUT DEFINITIONS
# Defines the cwd as the folder that the python code is in
Python_Parent_Path = os.getcwd()

BaseDir = str(Path(Python_Parent_Path).parent) + "\\" 

# Make a list of all of the files in the CIF folder
CIF_files = os.listdir(BaseDir + "CIF_files")

# Make a master folder for all of the crystal folders to go into
#os.makedirs(BaseDir + "Calculation_Files")

# open user_inputs file and writes to inputs_list
user_inputs = open(Python_Parent_Path + r"\user_inputs.txt")  
inputs_list = user_inputs.readlines() 
user_inputs.close()

#------------------------------------------------------------------------------#

for cif_file in CIF_files:


    # CREATE FOLDERS FOR CRYSTAL
    # specify where to look for the CIF file
    cif_path = BaseDir + "CIF_files\\" + cif_file

    # isolate crystal name
    crystal_name = os.path.basename(cif_path).removesuffix('.cif')

    # create a new folder
    os.makedirs(BaseDir + "Calculation_Files\\" + crystal_name) 

    # create a variable that points to the crystal folder
    crystal_dir = BaseDir + "Calculation_Files\\" + crystal_name + r"\\"

    # create subfolders
    relaxation1_path = crystal_dir + "Relaxation_1\\"
    elastic_path = crystal_dir + "Elastic\\"
    piezo_path = crystal_dir + "Piezo\\"

    os.makedirs(relaxation1_path)
    os.makedirs(elastic_path)
    os.makedirs(piezo_path)

#------------------------------------------------------------------------------#

    # INCAR CODE
    # copies the different INCAR files to the folders
    shutil.copy(BaseDir + "INPUTS\DO_NOT_TOUCH\INCAR_Relaxation", relaxation1_path + "INCAR")
    shutil.copy(BaseDir + "INPUTS\DO_NOT_TOUCH\INCAR_elastic", elastic_path + "INCAR")
    shutil.copy(BaseDir + "INPUTS\DO_NOT_TOUCH\INCAR_piezo", piezo_path + "INCAR")

#------------------------------------------------------------------------------#

    # POSCAR CODE
    bec = io.read(cif_path)
    bec_new = io.write(relaxation1_path + "ASE_POSCAR", bec, format="vasp")

#------------------------------------------------------------------------------#

    # FORMAT ASE POSCAR
    # Open the ASE POSCAR file
    ASE_POSCAR = open(relaxation1_path + 'ASE_POSCAR')  

    # read the text file line by line into a list
    ASE_POSCAR_Content = ASE_POSCAR.readlines()  
    ASE_POSCAR.close()

    # split line 5&6 into lists
    All_Elements = ASE_POSCAR_Content[5].split()  
    el_num = ASE_POSCAR_Content[6].split() 

    # remove duplicates and sort in alphabetical order
    Elements = sorted(list(dict.fromkeys(All_Elements)))  
    sequential_elements = []

    for count, element in enumerate(All_Elements):  
        sequential_elements.extend([element]*int(el_num[count]))
        
    # create pandas dataframe containing the elemental coordinates
    df = pd.DataFrame({  
        'Element': sequential_elements,
        'Coordinate': ASE_POSCAR_Content[8:] })

    # create alphabetically sorted database 
    sorted_df = df.sort_values(by=['Element'])  
    line6 = []

    # count the number of atoms of the stated element
    for count, element in enumerate(Elements):  
        line6.append(str(df.isin([element]).sum(axis=0)[0])) 

    # define text for lines 5&6 of the POSCAR file
    line5 = " ".join(Elements) 
    line6 = " ".join(line6) 

    # write the first line of the POSCAR string
    POSCAR_text = "System Description\n"  

    # write the next few lines of the ASE POSCAR file to a string
    for line in ASE_POSCAR_Content[1:5]:  
        POSCAR_text += line.strip() + "\n"

    # write the format (cartesian vs direct)
    POSCAR_text += line5 + "\n" + line6 + "\n" + ASE_POSCAR_Content[7]  

    for line in sorted_df["Coordinate"]:
        POSCAR_text += line.strip() + "\n"

    # create an empty file called POSCAR and fill with text
    POSCAR_file = Path(relaxation1_path + "POSCAR") 
    POSCAR_file.write_text(POSCAR_text) 

    os.remove(relaxation1_path + 'ASE_POSCAR')

#------------------------------------------------------------------------------#

    # POTCAR CODE
    # Opens the POSCAR file
    POSCAR = open(relaxation1_path + 'POSCAR')  

    # reads the text file line by line into a list
    POSCAR_Content = POSCAR.readlines()  
    POSCAR.close()

    # splits line 5 into a list
    Elements = POSCAR_Content[5].split()  

    # creates new list with the prefix "POTCAR_"
    POTCAR_files = ["POTCAR_" + sub for sub in Elements]  

    # concatenates the POTCAR files to form one large file based on order in POSCAR
    with open(relaxation1_path + 'POTCAR','wb') as newf:  
        for filename in POTCAR_files:
            with open(BaseDir + "INPUTS\DO_NOT_TOUCH\POTCAR_MASTER\\" + filename,'rb') as hf:
                newf.write(hf.read())

    # copy POTCAR file to other folders
    shutil.copy(relaxation1_path + "POTCAR", elastic_path)
    shutil.copy(relaxation1_path + "POTCAR", piezo_path)

#------------------------------------------------------------------------------#

    # KPOINTS CODE
    # defines the number of subdivisions in k space, 4 is the default
    k_div = str(4)

    # Writes the KPOINTS text to a string
    KPOINTS_Text = "Automatic\n0\nG\n" + k_div+2*(" "+k_div) +"\n0 0 0" 

    # creates an empty file called KPOINTS
    KPOINTS_file = Path(relaxation1_path + "KPOINTS")  

    # Fills KPOINTS file with text
    KPOINTS_file.write_text(KPOINTS_Text) 

    # copy kpoints file to other folders
    shutil.copy(relaxation1_path + "KPOINTS", elastic_path)
    shutil.copy(relaxation1_path + "KPOINTS", piezo_path)

#------------------------------------------------------------------------------#

    # SUB.SH CODE
    email_address = inputs_list[14].strip()
    project_group = inputs_list[17].strip()

    # open and edit files to add email address
    sub = open(BaseDir + "INPUTS\DO_NOT_TOUCH\\blank_sub.sh")
    
    # create three strings to be modified
    str1 = str2 = str3 = sub.read().replace("EMAIL_ADDRESS", email_address).replace("PROJECT_GROUP", project_group).replace("SUPER_COMPUTER_PATH", inputs_list[11].strip())   
    sub.close()

    # create three versions
    string_r = str1.replace("JOB_NAME", crystal_name + "_Relaxation")
    sub_file = Path(relaxation1_path + "sub.sh") 
    sub_file.write_text(string_r)

    string_e = str2.replace("JOB_NAME", crystal_name + "_Elastic")
    sub_file = Path(elastic_path + "sub.sh") 
    sub_file.write_text(string_e)

    string_p = str3.replace("JOB_NAME", crystal_name + "_Piezo")
    sub_file = Path(piezo_path + "sub.sh") 
    sub_file.write_text(string_p)

#------------------------------------------------------------------------------#

# Automation Shell code creation
# open and edit files to add email address
automate = open(BaseDir + "INPUTS\DO_NOT_TOUCH\Automate_Blank.sh")
    
# create string to be modified
shelltext = automate.read().replace("SUPER_COMPUTER_PATH", inputs_list[11].strip()).replace("SUPER_COMPUTER_USER_NAME", inputs_list[5].strip())
automate.close()

# create new file
automate_file = Path(BaseDir + "Calculation_Files\Automate.sh")
    
# fill file with modified text
automate_file.write_text(shelltext)

#------------------------------------------------------------------------------#

# CHECK IF FOLDER HAS BEEN UPLOADED TO KAY
answer = pyip.inputYesNo(prompt="Have you uploaded the generated folder to Kay? [Y/N]\n")

#------------------------------------------------------------------------------#

# LOG INTO KAY AND RUN COMMAND
hostname = "kay.ichec.ie"
username = inputs_list[5].strip()
password = inputs_list[8].strip()


# define the Shell command to be used
command = "cd " + inputs_list[11].strip() + "/Calculation_Files && dos2unix Automate.sh && sh Automate.sh"


# initialize the SSH client
client = paramiko.SSHClient()
# add to known hosts
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(hostname=hostname, username=username, password=password)
except:
    print("[!] Cannot connect to the SSH Server")
    exit()  
    
# execute the command
print("="*50, command, "="*50)
stdin, stdout, stderr = client.exec_command(command)
SSH_Output = stdout.read().decode() 
print(stdout.read().decode())
err = stderr.read().decode()
if err:
        print(err)
        
client.close()

