#!/bin/bash

# Run this script using bash analyze_gmx_rdf.sh [repetition#]

REPETITION=$1

BASE_PATH=${HOME}/Tutorials/1_CG_WaterBox # Submit inside the scripts directory.

WORKING_DIR=${BASE_PATH}/WaterBox

rep=${WORKING_DIR}/rep_$REPETITION

cp -rv ${BASE_PATH}/scripts/analyze_gmx_rdf.sh ${rep}/ # Copy bash script

ref=("W")
sel=("W")
gmx rdf -f ${rep}/md/md.xtc \
        -s ${rep}/md/md.tpr \
        -o ${rep}/md/rdf_"${ref[@]}"-"${sel[@]}".xvg \
        -rmax 4 \
        -bin 0.02 \
        -b 0 << INPUTS
name ${ref[@]}
name ${sel[@]}
INPUTS

ref=("NA CL")
sel=("W")
gmx rdf -f ${rep}/md/md.xtc \
        -s ${rep}/md/md.tpr \
        -o ${rep}/md/rdf_"${ref[@]}"-"${sel[@]}".xvg \
        -rmax 4 \
        -bin 0.02 \
        -b 0 << INPUTS
name ${ref[@]}
name ${sel[@]}
INPUTS

ref=("NA")
sel=("NA")
gmx rdf -f ${rep}/md/md.xtc \
        -s ${rep}/md/md.tpr \
        -o ${rep}/md/rdf_"${ref[@]}"-"${sel[@]}".xvg \
        -rmax 4 \
        -bin 0.02 \
        -b 0 << INPUTS
name ${ref[@]}
name ${sel[@]}
INPUTS

ref=("NA")
sel=("CL")
gmx rdf -f ${rep}/md/md.xtc \
        -s ${rep}/md/md.tpr \
        -o ${rep}/md/rdf_"${ref[@]}"-"${sel[@]}".xvg \
        -rmax 4 \
        -bin 0.02 \
        -b 0 << INPUTS
name ${ref[@]}
name ${sel[@]}
INPUTS


