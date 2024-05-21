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
The ``em/`` directory was created. Inside, there should be ``em.gro`` which is the energy minimized structure. Additionally, there should be ``energy.xvg`` which contains the potential energy of the system throughout the energy minimization, if you plot it (not done in this tutorial) you will see that the energy decays and converges, indicating that the system is stable.

## NPT EQUILIBRATION
We can now run the equilibration script. Typically, for all-atom molecular dynamics simulations, an _NPT_ equilibration is performed after an _NVT_ equilibration to allow the temperature to converge first, and avoid instabilities that my arise from generating velocities and applying a barostat. However, for coarse-grained simulations, this is typically not a problem, and thus is usually skipped. We will run a 5 ns _NPT_ equilibration with the Berendsen barostat and check for convergence. Using the Berendsen barostat first during equilibration allows for a faster and more stable equilibration at the expense of some accuracy. For the production run, we will change to a Parrinello-Rahman barostat which captures pressure fluctuations more accurately. 
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
Main takeaways from these RDFs:
1. Water molecules contain 2-3 water molecules within its first solvation shell.
2. Ions contain 3-4 water molecules within their first solvation shell.
3. Na contains 1 Na ion within its first solvation shell.
4. Na contains 7-8 Cl ions within its first solvation shell.
<p align="center">
  <img width="800" height="800" src=https://github.com/huang-zhu/Tutorials/assets/98200265/0124b819-baf3-46fc-948f-dc13eead6f88>
</p>

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






