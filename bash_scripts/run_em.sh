#!/bin/bash

### DEFINE BINARIES
GMX="$(type -P gmx)"

### PREPARE EM DIRECTORY
CURRENT=em
mkdir -p ${CURRENT} 

### GENERATE TPR
${GMX} grompp -f input_files/em.mdp \
              -c input_files/init.gro \
              -p input_files/topology.top \
              -po ${CURRENT}/mdout_${CURRENT}.mdp \
              -o ${CURRENT}/${CURRENT}.tpr \
              -maxwarn 1 

### RUN EM
${GMX} mdrun -v -deffnm ${CURRENT}/${CURRENT} -ntmpi 1

### ANALYZE
${GMX} energy -f ${CURRENT}/${CURRENT}.edr \
              -o ${CURRENT}/energy.xvg <<< $'Potential'  

### CLEAN-UP
rm ${CURRENT}/#*