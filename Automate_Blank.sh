#!/bin/sh

# make an array of every crystal name
cd SUPER_COMPUTER_PATH/Calculation_Files
crystal_array=($( ls -d * ))


# very quick fix for automate being included in the list
for i in "${!crystal_array[@]}"; do
        if [[ ${crystal_array[i]} = "Automate.sh" ]]; then
                unset 'crystal_array[i]'
        fi
done
    

# define the initial relaxation number
relax_num=1



for crystal in "${crystal_array[@]}"
do


        # define directory
        crystal_dir="SUPER_COMPUTER_PATH/Calculation_Files/$crystal/"

        # define crystal name
        crystal_name="($crystal)--->"


        echo
        echo                        


        # Saving the job queue to a variable
        string=$(squeue -u SUPER_COMPUTER_USER_NAME --format=%j)


        # checks if queue is contains the crystals name
        if ! [[ $string =~ $crystal ]]; then

                echo "$crystal_name Queue doesn't contain this crystal!"




                # if relaxation didn't converge
                if [ -f "${crystal_dir}Relaxation_${relax_num}/vasp.log" ] && ! grep -q 'reached required accuracy' "${crystal_dir}Relaxation_${relax_num}/vasp.log"; then  

                        echo "$crystal_name Need to create another relaxation!"

                        #increment the relaxation number by one, then make a new directory of that name
                        relax_num=`expr $relax_num + 1`
                        relax_dir="$crystal_dir"Relaxation_"$relax_num"
                        mkdir $relax_dir
                        echo "Relaxation_$relax_num folder created at $relax_dir"


                        # copy all of the necessary files to resubmit the relaxation
                        cp "${crystal_dir}Relaxation_`expr $relax_num - 1`/CONTCAR" "${relax_dir}/POSCAR"
                        cp "${crystal_dir}Relaxation_1/INCAR" "${relax_dir}"	
                        cp "${crystal_dir}Relaxation_1/KPOINTS" "${relax_dir}"
                        cp "${crystal_dir}Relaxation_1/POTCAR" "${relax_dir}"
                        cp "${crystal_dir}Relaxation_1/sub.sh" "${relax_dir}"

                        # submit new relaxation 
                        echo "$crystal_name Submitting Relaxation_${relax_num}" 
                        cd "${relax_dir}"
                        sbatch "${relax_dir}/sub.sh"




                # else if relaxation has converged
                elif [ -f "${crystal_dir}Relaxation_1/vasp.log" ] && grep -q 'reached required accuracy' "${crystal_dir}Relaxation_${relax_num}/vasp.log"; then

                        echo "$crystal_name relaxation has converged!"



                        # look for vasp.log files to if Piezo and Elastic have been submitted
                        if [ -f "${crystal_dir}Piezo/vasp.log" ] && [ -f "${crystal_dir}Elastic/OUTCAR" ]; then

                                echo "$crystal_name Piezo and Elastic Calculations have been previously submitted"



                                # if Piezo and Elastic have converged, process is finished!
                                if $(grep -q 'TOTAL ELASTIC MODULI' "${crystal_dir}Elastic/OUTCAR") && $(grep -q 'Linear response finished' "${crystal_dir}Piezo/vasp.log"); then

                                        echo "$crystal_name All Calculations Completed!! Relax/Piezo/Elastic"


                                        # if the calculations are completed, delete this crystal from the list
                                        for i in "${!crystal_array[@]}"; do
                                          if [[ ${crystal_array[i]} = $crystal ]]; then
                                            unset 'crystal_array[i]'
                                          fi
                                        done



                                else
                                        echo "$crystal_name EP Calculations not converged!"
                                fi




                        else

                                echo "$crystal_name No EP Calculations previously submitted!"

                                cp "${crystal_dir}Relaxation_${relax_num}/CONTCAR" "${crystal_dir}Elastic/POSCAR"
                                cp "${crystal_dir}Relaxation_${relax_num}/CONTCAR" "${crystal_dir}Piezo/POSCAR"

                                tr -d '\r' < "${crystal_dir}Elastic/sub.sh" > "${crystal_dir}Elastic/sub_unix.sh"
                                mv "${crystal_dir}Elastic/sub_unix.sh" "${crystal_dir}Elastic/sub.sh"

                                tr -d '\r' < "${crystal_dir}Piezo/sub.sh" > "${crystal_dir}Piezo/sub_unix.sh"
                                mv "${crystal_dir}Piezo/sub_unix.sh" "${crystal_dir}Piezo/sub.sh"

                                cd "${crystal_dir}Elastic"
                                sbatch "${crystal_dir}Elastic/sub.sh"
                                cd "${crystal_dir}Piezo"
                                sbatch "${crystal_dir}Piezo/sub.sh"

                                echo "$crystal_name Just submitted elastic and piezo"

                        fi



                else
                        echo "$crystal_name Initial relaxation not submitted, submitting now"
                        cd "${crystal_dir}Relaxation_1"
                        tr -d '\r' < "${crystal_dir}Relaxation_1/sub.sh" > "${crystal_dir}Relaxation_1/sub_unix.sh"
                        mv "${crystal_dir}Relaxation_1/sub_unix.sh" "${crystal_dir}Relaxation_1/sub.sh"
                        sbatch "${crystal_dir}Relaxation_1/sub.sh"
                fi



        elif [[ $crystal =~ $string ]]; then
            echo "$crystal_name Queue contains a job with this crystal, skip!"
        fi              

sleep 1
done