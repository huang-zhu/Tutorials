# Coarse-grained water box

In this tutorial, we will perform a coarse-grained simulation of a 0.4 M solution of NaCl. We will be using the MARTINI coarse-grained force field and its refined polarizable water model.

The purpose of this tutorial is to perform  inexpensive simulations that do not require high-performance computing resources (i.e., you can run this on almost any Windows laptop). If your laptop/desktop has a dedicated NVIDIA graphics processing unit (GPU), then you will be able to complete this tutorial much faster. GROMACS must be installed with the correct settings depending on the availability of an NVIDIA GPU (you should have completed this before starting this tutorial).

## SET UP YOUR DIRECTORIES
```
### DEFINE TUTORIAL AND ITS DIRECTORY
TUTORIAL=CG_WaterBox
TUTORIAL_PATH=${HOME}/Tutorials/${TUTORIAL}
PYTHON_SCRIPTS_PATH=${TUTORIAL_PATH}/python_scripts

### DEFINE CONTAINER 
CONTAINER_IMAGE="huangzhu/github:Tutorials_2.0"

### GENERATE THE DIRECTORY AND GO INTO IT
mkdir -p ${TUTORIAL_PATH}

### RUN CONTAINER INTERACTIVELY 
docker run -v ${TUTORIAL_PATH}:${TUTORIAL_PATH} \
           -w ${TUTORIAL_PATH} \
           -e TUTORIAL=${TUTORIAL} \
           -e TUTORIAL_PATH=${HOME}/Tutorials/${TUTORIAL} \
           -e PYTHON_SCRIPTS_PATH=${TUTORIAL_PATH}/python_scripts \
           --gpus all \
           -it \
           --rm \
           ${CONTAINER_IMAGE} 

### CLONE THE TUTORIAL FROM THIS GITHUB
git clone -b ${TUTORIAL} https://github.com/huang-zhu/Tutorials.git \
           ./

## PREPARE FILES
bash bash_scripts/prep_files.sh
cd WaterBox
This will create WaterBox dir with input_files/ and SH scripts (em,npt,prod)

## ENERGY MINIMIZATION
bash run_em.sh
This will create em/ dir with energy minimzed box of 0.4 M NaCl in Water

## NPT EQUILIBRATION
bash run_npt.sh
cd npt/
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd ../

## PRODUCTION RUN
bash run_prod.sh
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd rdf
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_rdf.py --datafile_path ./
cd ../../

## ANALYSIS (OPTIONAL)
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/analyze_python_rdf.py --datafile_path ./
```

