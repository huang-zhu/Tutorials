# Coarse-grained water box

In this tutorial, we will perform a coarse-grained simulation of a 0.4 M solution of NaCl. We will be using the MARTINI coarse-grained force field and its refined polarizable water model.

The purpose of this tutorial is to perform inexpensive simulations that do not require high-performance computing resources (i.e., you can run this on almost any Windows laptop). If your laptop/desktop has a dedicated NVIDIA graphics processing unit (GPU), then you will be able to complete this tutorial much faster (the scripts will detect the GPU and run accordingly). GROMACS must be installed with the correct settings depending on the availability of an NVIDIA GPU (you should have completed this before starting this tutorial). At the end there will be an optional section that you can decide whether to complete or not.

NOTE: Below are the _MANUAL METHOD_ and the _AUTOMATED METHOD_ for you to follow. 
- _MANUAL METHOD_ (Recommended for new GROMACS users):
  - consists of completing the tutorial by running each line manually, this allows you to see the specific commands used and learn about the syntax used, along with running intermediate steps (_e.g._, transfer and generate files).
- _AUTOMATED METHOD_ (Recommended if you have some experience with ``bash`` and GROMACS):
  - consists of completing the tutorial by running provided ``.sh`` scripts that combine the lines from the _MANUAL METHOD_, this allows you to automate your workflow.

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

# _===== MANUAL METHOD =====_
We need to first define the corresponding directories and generate them.
```
MAIN_PATH=${TUTORIAL_PATH}
WORKING_DIR=WaterBox
INPUT_FILES_DIR=input_files
INPUT_FILES_PATH=${MAIN_PATH}/${WORKING_DIR}/${INPUT_FILES_DIR}
mkdir -p ${INPUT_FILES_PATH}
```

Once created, we can copy the required files into the corresponding directory.
```
cp -rv ${MAIN_PATH}/inputs/ff/*        ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/inputs/mdp/*       ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/inputs/molecules/* ${INPUT_FILES_PATH}
cp -rv ${MAIN_PATH}/bash_scripts/*     ${INPUT_FILES_PATH}/../
```

We will be using GROMACS, and I like to define the ``GMX`` variable for ease of porting code to other computing resources.
```
GMX="$(type -P gmx)"
``` 

Now, let's define our system parameters. We will then prepare a 125 nm<sup>3</sup> cubic box with 485 molecules of water and 16 molecules of sodium chloride to achieve a ~0.4 M NaCL solution. 
```
NUM_PW=485
NUM_CATION=16
NUM_ANION=16
BOX_ARRAY=(5 5 5)

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
```

We will now created an ``index.ndx`` file in which we will group the water molecules and ions into a single group.
```
${GMX} make_ndx -f ${INPUT_FILES_PATH}/init.gro \
                -o ${INPUT_FILES_PATH}/index.ndx << INPUTS
r PW ION 
name 4 PW_ION
q
INPUTS
```

Finally, a topology file (``topology.top`` here) is needed to tell GROMACS information about our system.
```
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
```

We are now ready to run energy minimization. This allows atoms to slightly shift their positions to avoid steric clashes that may lead to huge forces, which could lead to the system blowing up. The resulting ``em/em.gro`` is the energy minimized structure and is needed to run equilibration next. Additionally we also use ``gmx energy`` to compute the Potential Energy during the energy minimization. If you plot the resulting ``em/energy.xvg`` data (not done here), you will see that the Potential Energy decays and converges, indicating that the system is stable. 
```
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
```

We can now run the equilibration. Typically, for all-atom molecular dynamics simulations, an _NPT_ equilibration is performed after an _NVT_ equilibration to allow the temperature to converge first, and avoid instabilities that my arise from generating velocities and applying a barostat. However, for coarse-grained simulations, this is typically not a problem, and thus is usually skipped. We will run a 5 ns _NPT_ equilibration with the Berendsen barostat and check for convergence. Using the Berendsen barostat first during equilibration allows for a faster and more stable equilibration at the expense of some accuracy. For the production run, we will change to a Parrinello-Rahman barostat which captures pressure fluctuations more accurately. We will run 20 short (1,000 steps) simulations in increments of 1 fs (0.001 ps) to slowly release the system. This is completely arbitrary, but it's my preferred way of beginning most coarse-grained simulations, especially when it's a highly unstable one. Aftwards, we will run the full equilibration.

```
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
```

After the equilibration finishes, we will process the trajectory so that molecules are not broken by the periodic boundary conditions and we will use ``gmx energy`` to compute the Temperature, Pressure, Density, and Potential Energy during the trajectory.

```
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

${GMX} energy -f ${CURRENT}/${CURRENT}.edr \
              -o ${CURRENT}/energy.xvg <<< $'Temperature\nPressure\nDensity\nPotential'  
```

Once the equilibration finishes, we can plot some properties as a time series to assess convergence. 
```
cd npt/
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd ../
```
We can see that the system converges really fast, and so 5 ns of _NPT_ equilibration is sufficient. 
<p align="center">
  <img src=https://github.com/huang-zhu/Tutorials/assets/98200265/e8bd2414-a456-45d6-9a56-9bf010cb209e>
</p>

We can now run the production. We run a 200 ns simulation, sampling every 50 ps (_i.e._, saving a frame). This simulation will take much longer than the equilibration so you should plan accordingly (_e.g._, leave it running overnight or for a period of time when you won't be using your computer for any other work). To get an estimate beforehand, you can look at the end of the previous ``npt.log`` file, where it says ``Performance:`` and you can estimate how long a 200 ns will take by either using the ``ns/day`` or ``hr/ns`` metrics. Once everything is set, we can proceed.
```
### IDENTIFY CUDA DEVICES
CUDA=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

### DEFINE BINARIES
GMX="$(type -P gmx)"

### DEFINE ARGUMENTS
NSTEPS=npt
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
```

Again, we will process the trajectory and use ``gmx energy`` to for analysis.
```
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
```

In addition, we will use use ``gmx rdf`` to generate radial distribution functions (RDF).
```
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
```

We can plot the same properties as before to ensure we are converged. Since this is a small and simple system, we should be fully converged and should be able to use the full trajectory for analysis. Oftentimes, a portion of the production run must be discarded to use only the fully converged trajectory. Ideally, we'd want to minimize the amount of data that we discard due to computing factors (_e.g._, time limitations on computing resources) as well as convenience (_e.g._, we don't want to load a huge number of frames only to discard half of them). Therefore, it's always more convenient to perform long equilibrations before production runs to minimize the discarded data.  
```
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
```
We can see that the system converges really fast, and so we can use the full trajectory for analysis. Note that here assume that the production run is fully converged. If the trajectory was not converged, the analyses commands should be modified with the ``-b`` flag to specify where to start in the trajectory.  
<p align="center">
  <img src=https://github.com/huang-zhu/Tutorials/assets/98200265/281be24a-3090-4e94-8324-4079ac70d15e>
</p>

We can now plot the RDF to study the distribution of species in the system. Run the following python script to plot the data generated by ``gmx rdf`` for four pairs: W-W, NaCl-W, Na-Na, Na-Cl.
```
cd rdf
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_rdf.py --datafile_path ./
cd ../../
```
<p align="center">
  <img width="800" height="800" src=https://github.com/huang-zhu/Tutorials/assets/98200265/0124b819-baf3-46fc-948f-dc13eead6f88>
</p>








# _===== AUTOMATED METHOD =====_
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
The ``em/`` directory was created. Inside, there should be ``em.gro`` which is the energy minimized structure. Additionally, there should be ``energy.xvg`` which contains the potential energy of the system throughout the energy minimization, if you plot it (not done in this tutorial) you will see that the energy decays and converges, indicating that the system is stable.

## NPT EQUILIBRATION
We can now run the equilibration script. Typically, for all-atom molecular dynamics simulations, an _NPT_ equilibration is performed after an _NVT_ equilibration to allow the temperature to converge first, and avoid instabilities that my arise from generating velocities and applying a barostat. However, for coarse-grained simulations, this is typically not a problem, and thus is usually skipped. We will run a 5 ns _NPT_ equilibration with the Berendsen barostat and check for convergence. Using the Berendsen barostat first during equilibration allows for a faster and more stable equilibration at the expense of some accuracy. For the production run, we will change to a Parrinello-Rahman barostat which captures pressure fluctuations more accurately. The ``run_npt.sh`` script will run 20 short (1,000 steps) simulations in increments of 1 fs (0.001 ps) to slowly release the system. This is completely arbitrary, but it's my preferred way of beginning most coarse-grained simulations, especially when it's a highly unstable one. Aftwards, the full equilibration will begin.
```
bash run_npt.sh
```

Once the equilibration finishes, we can plot some properties as a time series to assess convergence. 
```
cd npt/
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
cd ../
```
We can see that the system converges really fast, and so 5 ns of _NPT_ equilibration is sufficient. 
<p align="center">
  <img src=https://github.com/huang-zhu/Tutorials/assets/98200265/e8bd2414-a456-45d6-9a56-9bf010cb209e>
</p>

## PRODUCTION RUN
We are now ready for the production run. This script will run a 200 ns simulation, sampling every 50 ps (_i.e._, saving a frame). This simulation will take much longer than the equilibration so you should plan accordingly (_e.g._, leave it running overnight or for a period of time when you won't be using your computer for any other work). To get an estimate beforehand, you can look at the end of the previous ``npt.log`` file, where it says ``Performance:`` and you can estimate how long a 200 ns will take by either using the ``ns/day`` or ``hr/ns`` metrics. Once everything is set, run the production script.
```
bash run_prod.sh
```

Once the production finishes, we can plot the same properties as before to ensure we are converged. Since this is a small and simple system, we should be fully converged and should be able to use the full trajectory for analysis. Oftentimes, a portion of the production run must be discarded to use only the fully converged trajectory. Ideally, we'd want to minimize the amount of data that we discard due to computing factors (_e.g._ time limitations on computing resources) as well as convenience (_e.g._ we don't want to load a huge number of frames only to discard half of them). Therefore, it's always more convenient to perform long equilibrations before production runs to minimize the discarded data.  
```
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_convergence.py --datafile energy.xvg
```
We can see that the system converges really fast, and so we can use the full trajectory for analysis. Note that all scripts here assume that the production run is fully converged. In the ``run_prod.sh`` script, we also use ``gmx rdf`` to generate radial distribution functions (RDF), if the trajectory was not converged, these commands should be modified with the ``-b`` flag to specify where to start in the trajectory.  
<p align="center">
  <img src=https://github.com/huang-zhu/Tutorials/assets/98200265/281be24a-3090-4e94-8324-4079ac70d15e>
</p>

We can now plot the RDF to study the distribution of species in the system. Run the following python script to plot the data generated by ``gmx rdf`` for four pairs: W-W, NaCl-W, Na-Na, Na-Cl.
```
cd rdf
python3.10 ${PYTHON_SCRIPTS_PATH}/plot_rdf.py --datafile_path ./
cd ../../
```
<p align="center">
  <img width="800" height="800" src=https://github.com/huang-zhu/Tutorials/assets/98200265/0124b819-baf3-46fc-948f-dc13eead6f88>
</p>

# CONCLUSIONS
Main takeaways from these RDFs:
1. Water molecules contain 2-3 water molecules within its first solvation shell.
2. Ions contain 3-4 water molecules within their first solvation shell.
3. Na contains 1 Na ion within its first solvation shell.
4. Na contains 7-8 Cl ions within its first solvation shell.


At this point, this tutorial is essentially finished, while the remaining section is optional, so congrats on completing the tutorial and thanks for checking out my work!

## ANALYSIS (OPTIONAL)
Up to now, all the analyses have been done using GROMACS native tools, but a lot of times, we would need Python for other analyses. This section essentially reproduces the ``gmx rdf`` function to generate the RDF for the W-W pair. Ideally, you would try to write your own code to get some experience in using Python to analyze molecular trajectories, but it's also fine if you look at the script provided and read through it to grasp the general algorithm. The script is written to be run either in serial or in parallel, meaning you analyze frame by frame consecutively, or you can analyze multiple frames concurrently. By default, it will run serially, but if you want it to run in parallel, you need to change the line that says ``multi = False`` to ``multi = True``. Also, by default, it will only run the first 64 frames for time purposes. If you have the time and want to experiment, you can run it for the whole trajectory by deleting the ``64`` and uncommenting the line. You can also run it for the other pairs by replacing ``pos_W[frame]`` with ``pos_NA[frame]``, ``pos_CL[frame]``, or ``pos_NACL[frame]``.
```
cd prod
python3.10 ${PYTHON_SCRIPTS_PATH}/analyze_python_rdf.py --datafile_path ./
```

We can see that we get basically the same RDF, albeit with more noise because of the limited number of frames analyzed.
<p align="center">
  <img width="400" height="400" src=https://github.com/huang-zhu/Tutorials/assets/98200265/36634daf-f015-45d5-a206-fb2db018be99>
</p>






