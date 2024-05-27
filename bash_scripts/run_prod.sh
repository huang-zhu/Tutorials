#!/bin/bash

### IDENTIFY CUDA DEVICES
CUDA=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

### DEFINE BINARIES
GMX="$(type -P gmx)"

### DEFINE ARGUMENTS
PREV=npt
CURRENT=prod
GMX_MDRUN_FLAGS="-v -ntmpi 1 "
if [ "$CUDA" -gt 0 ]; then GMX_MDRUN_FLAGS+="-update gpu "; fi

### PREPARE PROD DIRECTORY
mkdir -p ${CURRENT} 

### GENERATE TPR
${GMX} grompp -f input_files/${CURRENT}.mdp \
              -c ${PREV}/${PREV}.gro \
              -p input_files/topology.top \
              -n input_files/index.ndx \
              -po ${CURRENT}/mdout_${CURRENT}.mdp \
              -o ${CURRENT}/${CURRENT}.tpr \
              -maxwarn 1

### RUN PRODUCTION
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
              -o ${CURRENT}/energy.xvg <<< $'Temperature\nPressure\nDensity\nPotential\n0'  

RDF_DIR=${CURRENT}/rdf
mkdir -p ${RDF_DIR}

XTC=${CURRENT}/${CURRENT}.xtc
TPR=${CURRENT}/${CURRENT}.tpr

RMAX=4 # nm
BIN_SIZE=0.01 # nm

XVG=${RDF_DIR}/W-W.xvg
${GMX} rdf -f ${XTC} \
           -s ${TPR} \
           -rmax ${RMAX} \
           -bin ${BIN_SIZE} \
           -o ${XVG} << INPUTS
name W
name W
INPUTS
           
XVG=${RDF_DIR}/NACL-W.xvg
${GMX} rdf -f ${XTC} \
           -s ${TPR} \
           -rmax ${RMAX} \
           -bin ${BIN_SIZE} \
           -o ${XVG} << INPUTS
name NA CL
name W
INPUTS

XVG=${RDF_DIR}/NA-NA.xvg
${GMX} rdf -f ${XTC} \
           -s ${TPR} \
           -rmax ${RMAX} \
           -bin ${BIN_SIZE} \
           -o ${XVG} << INPUTS
name NA 
name NA
INPUTS

XVG=${RDF_DIR}/NA-CL.xvg
${GMX} rdf -f ${XTC} \
           -s ${TPR} \
           -rmax ${RMAX} \
           -bin ${BIN_SIZE} \
           -o ${XVG} << INPUTS
name NA 
name CL
INPUTS

### CLEAN-UP
rm -rv ${CURRENT}/#* ${CURRENT}/*.cpt ${CURRENT}/*.mdp
