#!/bin/bash

### Submit from github/Tutorials/CG_WaterBox/bash_scripts: bash prep_files.sh

### DEFINE DIRECTORIES AND GENERATE
MAIN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../ && pwd )"
WORKING_DIR=WaterBox
INPUT_FILES_DIR=input_files
INPUT_FILES_PATH=${MAIN_PATH}/${WORKING_DIR}/${INPUT_FILES_DIR}
mkdir -p ${INPUT_FILES_PATH}

echo -e "\n========================================================"
echo -e "== COPYING FILES FROM:                                  "
echo -e "== ${MAIN_PATH}                                         "
echo -e "========================================================"
echo -e "== TO:                                                  "
echo -e "== ${INPUT_FILES_PATH}                                  "
echo -e "========================================================\n"

### TRANSFER FILES
cp -rv ${MAIN_PATH}/inputs/ff/*        ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/inputs/mdp/*       ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/inputs/molecules/* ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/bash_scripts/*     ${INPUT_FILES_PATH}/../

### DEFINE BINARIES
GMX="$(which gmx)"

### DEFINE SYSTEM PARAMETERS
NUM_PW=485
NUM_CATION=16
NUM_ANION=16
BOX_ARRAY=(5 5 5)

echo -e "\n========================================================"
echo -e "== WILL GENERATE A BOX WITH:                            "
echo -e "==   PW     ${NUM_PW}                                   "
echo -e "==   CATION ${NUM_CATION}                               "
echo -e "==   ANION  ${NUM_ANION}                                "
echo -e "========================================================\n"

### INSERT PW
${GMX} insert-molecules -ci ${INPUT_FILES_PATH}/PW.gro \
                        -nmol ${NUM_PW} \
                        -try 100 \
                        -box ${BOX_ARRAY[@]} \
                        -o ${INPUT_FILES_PATH}/init.gro

### INSERT CATIONS
${GMX} insert-molecules -f ${INPUT_FILES_PATH}/init.gro \
                        -ci ${INPUT_FILES_PATH}/NA.gro \
                        -nmol ${NUM_CATION} \
                        -try 100 \
                        -o ${INPUT_FILES_PATH}/init.gro
### INSERT ANIONS
${GMX} insert-molecules -f ${INPUT_FILES_PATH}/init.gro \
                        -ci ${INPUT_FILES_PATH}/CL.gro \
                        -nmol ${NUM_ANION} \
                        -try 100 \
                        -o ${INPUT_FILES_PATH}/init.gro

### GENERATE NDX
${GMX} make_ndx -f ${INPUT_FILES_PATH}/init.gro \
                -o ${INPUT_FILES_PATH}/index.ndx << INPUTS
r PW ION 
name 4 PW_ION
q
INPUTS

### GENERATE TOP
> ${INPUT_FILES_PATH}/topology.top
tee -a ${INPUT_FILES_PATH}/topology.top << EOF
#include "martini_v2.3refP_PEO.itp" 
#include "ions.itp" 
[ system ]
; name
Polarizable Water Box

[ molecules ]
; name  number
PW ${NUM_PW}
NA ${NUM_CATION}
CL ${NUM_ANION}
EOF

### CLEAN-UP
rm ${INPUT_FILES_PATH}/#*