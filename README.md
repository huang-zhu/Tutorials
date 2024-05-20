# Coarse-grained water box

In this tutorial, we will perform a coarse-grained simulation of a 0.4 M solution of NaCl. We will be using the MARTINI coarse-grained force field and its refined polarizable water model.

The purpose of this tutorial is to perform inexpensive simulations that do not require high-performance computing resources (i.e., you can run this on almost any Windows laptop). If your laptop/desktop has a dedicated NVIDIA graphics processing unit (GPU), then you will be able to complete this tutorial much faster (the scripts will detect the GPU and run accordingly). GROMACS must be installed with the correct settings depending on the availability of an NVIDIA GPU (you should have completed this before starting this tutorial).

## SET UP YOUR DIRECTORIES
We will first define the tutorial that we are running, some paths of interest, and the container image that we will use throughout the tutorial.  
```
### DEFINE TUTORIAL AND ITS DIRECTORY
TUTORIAL=CG_WaterBox
TUTORIAL_PATH=${HOME}/github/Tutorials/${TUTORIAL}
PYTHON_SCRIPTS_PATH=${TUTORIAL_PATH}/python_scripts

### DEFINE CONTAINER 
CONTAINER_IMAGE="huangzhu/github:Tutorials_2.0"

### GENERATE THE DIRECTORY AND GO INTO IT
mkdir -p ${TUTORIAL_PATH}
```

## RUN CONTAINER INTERACTIVELY 
After setting up the paths, we will run the container interactively. To do this we have to mount the storage volumes that contain the files. Additionally, we will use other flags in the ``docker run`` command to make our lives easier.
* ``-v`` : absolute path to mount (left) and absolute path mounted as (right)
* ``-w`` : working directory upon opening the container
* ``-e`` : environment variables that we want defined (we're just passing the ones we defined previously)
* ``--gpus all`` : specify if we want the GPU to be used
* ``-it`` : ``i`` for interactive and ``t`` for a terminal
* ``--rm`` : remove the container after we close it (otherwise it's kept open and will consume resources)

```
docker run -v ${TUTORIAL_PATH}:${TUTORIAL_PATH} \
           -w ${TUTORIAL_PATH} \
           -e TUTORIAL=${TUTORIAL} \
           -e TUTORIAL_PATH=${HOME}/Tutorials/${TUTORIAL} \
           -e PYTHON_SCRIPTS_PATH=${TUTORIAL_PATH}/python_scripts \
           --gpus all \
           -it \
           --rm \
           ${CONTAINER_IMAGE} 
```

## CLONE THE TUTORIAL FROM THIS GITHUB
We should now be inside the container (in ``${TUTORIAL_PATH}``) and you should see your command line as ``user@XYZ`` where ``XYZ`` is a string of number and letters. We will now clone this tutorial.
* ``-b`` : specifies the branch wanted
* ``./`` : specifies that the contents of the branch should be cloned here
```
git clone -b ${TUTORIAL} https://github.com/huang-zhu/Tutorials.git \
           ./
```

## PREPARE FILES
We can now run the script that will prepare the initial files to run energy minimization. We will prepare a 125 nm<sup>3</sup> cubic box with 485 molecules of water and 16 molecules of sodium chloride to achieve a ~0.4 M NaCL solution. The box will be generated using ``gmx insert-molecules``. In addition, the topology file and an index file will be generated. 
```
bash bash_scripts/prep_files.sh
cd WaterBox
```
The ``Waterbox/`` directory was created and everything else will be run from this directory. Inside, there are ``.sh`` files that run the different steps of the tutorial (energy minimization, equilibration, production), and there's the ``input_files/`` directory that contains the essential files needed to run GROMACS. 

## ENERGY MINIMIZATION
Inside the ``WaterBox/`` directory we can run the script that will energy minimize the system. This allows atoms to slightly shift their positions to avoid steric clashes that may lead to huge forces, which could lead to the system blowing up.
```
bash run_em.sh
```
The ``em/`` directory was created. Inside, there should be ``em.gro`` which is the energy minimized structure. ADditionally, there should be ``energy.xvg`` which contains the potential energy of the system throughout the energy minimization, if you plot it (not done in this tutorial) you will see that the energy decays and converges, indicating that the system is stable.

## NPT EQUILIBRATION
We can now run the equilibration script. Typically, for all-atom molecular dynamics simulations, an _NPT_ equilibration is performed after an _NVT_ equilibration to allow the temperature to converge first. However, for coarse-grained simulations, the temperature converges very fast, and thus is usually skipped. We will run a 5 ns _NPT_ equilibration with the Berendsen barostat and check for convergence.
```
bash run_npt.sh
cd npt/
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd ../
```
![plots_equilibration_convergence](https://github.com/huang-zhu/Tutorials/assets/98200265/e8bd2414-a456-45d6-9a56-9bf010cb209e)


## PRODUCTION RUN
```
bash run_prod.sh
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd rdf
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_rdf.py --datafile_path ./
cd ../../
```

## ANALYSIS (OPTIONAL)
```
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/analyze_python_rdf.py --datafile_path ./
```

