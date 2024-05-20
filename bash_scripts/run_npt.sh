#!/bin/bash

### IDENTIFY CUDA DEVICES
CUDA=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

### DEFINE BINARIES
GMX="$(type -P gmx)"

### DEFINE ARGUMENTS
NSTEPS=1000
CURRENT=npt
GMX_MDRUN_FLAGS="-v -ntmpi 1 "
if [ "$CUDA" -gt 0 ]; then GMX_MDRUN_FLAGS+="-update gpu "; fi

### PREPARE NPT DIRECTORY
mkdir -p ${CURRENT} 

### WARMUP EQUILIBRATION TO SOFTLY RELEASE SYSTEM
for ((i=1; i<=20; i++)); do #echo $(awk "BEGIN {print $i / 1000}" | awk '{ printf("%.3f\n", $1) }');done

    ### DEFINE TIMESTEP
    dt=$(awk "BEGIN {print $i / 1000}" | awk '{ printf("%.3f\n", $1) }')
    
    ### GENERATE WARMUP MDP, MODIFY ACCORDING TO TIMESTEP, AND GENERATE TPR
    if [ "$i" -eq 1 ]; then
        PREV=em
        echo -e "\n=== TIMESTEP $dt PS/STEP ===\n"
        sed -s /'dt '/s/[0-9,.][0-9,.]*/$dt/g input_files/${CURRENT}.mdp > input_files/${CURRENT}_warmup.mdp
        sed -i /'nsteps '/s/[0-9,.][0-9,.]*/$NSTEPS/g input_files/${CURRENT}_warmup.mdp
        sed -i /'gen-vel '/s/no/yes/g input_files/${CURRENT}_warmup.mdp
        sed -i /'continuation '/s/yes/no/g input_files/${CURRENT}_warmup.mdp

        ${GMX} grompp -f input_files/${CURRENT}_warmup.mdp \
                      -c ${PREV}/${PREV}.gro \
                      -p input_files/topology.top \
                      -n input_files/index.ndx \
                      -po ${CURRENT}/mdout_${CURRENT}_warmup_$dt.mdp \
                      -o ${CURRENT}/${CURRENT}_warmup_$dt.tpr \
                      -maxwarn 1
    elif [ "$i" -gt 1 ]; then
        PREV_dt=$(awk "BEGIN {print $(($i-1)) / 1000}" | awk '{ printf("%.3f\n", $1) }')
        PREV=${CURRENT}_warmup_$PREV_dt
        echo -e "\n=== TIMESTEP $PREV_dt --> $dt PS/STEP ===\n"
        sed -i /'dt '/s/[0-9,.][0-9,.]*/$dt/g input_files/${CURRENT}_warmup.mdp
        sed -i /'nsteps '/s/[0-9,.][0-9,.]*/$NSTEPS/g input_files/${CURRENT}_warmup.mdp
        sed -i /'gen-vel '/s/yes/no/g input_files/${CURRENT}_warmup.mdp
        sed -i /'continuation '/s/no/yes/g input_files/${CURRENT}_warmup.mdp

        ${GMX} grompp -f input_files/${CURRENT}_warmup.mdp \
                      -c ${CURRENT}/${PREV}.gro \
                      -p input_files/topology.top \
                      -n input_files/index.ndx \
                      -po ${CURRENT}/mdout_${CURRENT}_warmup_$dt.mdp \
                      -o ${CURRENT}/${CURRENT}_warmup_$dt.tpr \
                      -maxwarn 1
    fi

    ### RUN WARMUP EQUIL
    ${GMX} mdrun ${GMX_MDRUN_FLAGS} -deffnm ${CURRENT}/${CURRENT}_warmup_$dt
    
    ### CLEAN-UP
    rm -rv ${CURRENT}/*.tpr ${CURRENT}/*.xtc ${CURRENT}/*.cpt ${CURRENT}/*.edr ${CURRENT}/*.mdp
done

### FULL EQUILIBRATION AT REGULAR TIMESTEP
PREV=${CURRENT}_warmup_$dt 
echo -e "\n=== FULL EQUIL ===\n"

### GENERATE TPR
${GMX} grompp -f input_files/${CURRENT}.mdp \
              -c ${CURRENT}/${PREV}.gro \
              -p input_files/topology.top \
              -n input_files/index.ndx \
              -po ${CURRENT}/mdout_${CURRENT}.mdp \
              -o ${CURRENT}/${CURRENT}.tpr \
              -maxwarn 1

### RUN FULL EQUIL
${GMX} mdrun ${GMX_MDRUN_FLAGS} -deffnm ${CURRENT}/${CURRENT} 

### CENTER TRAJECTORIES
${GMX} trjconv -f ${CURRENT}/${CURRENT}.gro \
               -s ${CURRENT}/${CURRENT}.tpr \
               -o ${CURRENT}/${CURRENT}.gro \
               -pbc mol \
               -conect <<< $'System' 

${GMX} trjconv -f ${CURRENT}/${CURRENT}.xtc \
               -s ${CURRENT}/${CURRENT}.tpr \
               -o ${CURRENT}/${CURRENT}.xtc \
               -pbc mol \
               -conect <<< $'System' 

### ANALYZE
${GMX} energy -f ${CURRENT}/${CURRENT}.edr \
              -o ${CURRENT}/energy.xvg <<< $'Temperature\nPressure\nDensity\nPotential'  

### CLEAN-UP
rm -rv ${CURRENT}/#* ${CURRENT}/*.cpt ${CURRENT}/*.mdp