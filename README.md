# Coarse-grained water box

In this tutorial, we will perform a coarse-grained simulation of a 0.4 M solution of NaCl. We will be using the MARTINI coarse-grained force field and its refined polarizable water model. 

The purpose of this tutorial is to perform  inexpensive simulations that do not require high-performance computing resources (i.e., you can run this on almost any Windows laptop). If your laptop/desktop has a dedicated NVIDIA graphics processing unit (GPU), then you will be able to complete this tutorial much faster. GROMACS must be installed with the correct settings depending on the availability of an NVIDIA GPU (you should have completed this before starting this tutorial). 

## SET UP YOUR DIRECTORIES
```
### DEFINE TUTORIAL AND ITS DIRECTORY
TUTORIAL=CG_WaterBox
TUTORIAL_DIR=github/Tutorials/${TUTORIAL}

### GENERATE THE DIRECTORY AND GO INTO IT
mkdir -p ${TUTORIAL_DIR}
cd ${TUTORIAL_DIR}

### CLONE THE TUTORIAL FROM THIS GITHUB
git clone -b ${TUTORIAL} https://github.com/huang-zhu/Tutorials
```
## PREPARE FILES

## ENERGY MINIMIZATION

## NPT EQUILIBRATION

## PRODUCTION RUN

## ANALYSIS
