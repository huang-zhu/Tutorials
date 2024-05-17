# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 15:14:29 2023

@author: huangzhu
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib import rc
import matplotlib as mpl
from matplotlib import mathtext
plt.rcParams.update({
    'text.usetex':False,
    'font.family':'Arial',
    'font.sans-serif':['Arial'],
    'mathtext.default':'regular',
    })
import os
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import mdtraj as md

def getDistancesWithPBC_XYZ(positions_i, positions_j, size_box):
    """ ====================================================\n
        === Provide coordinates of atom i (positions_i). ===\n
        === Provide coordinates of atom j (positions_j). ===\n
        === Provide size of box (size_box).              ===\n
        === Return distances array between i and j.      ===\n
        ====================================================\n """
    # Take distance between particle i to every other particle j.
    distances = positions_i[:,np.newaxis,:] - positions_j[np.newaxis,:,:]
    # Apple PBC in X and Y dimensions.
    distances[:,:,0] -= ( distances[:,:,0]  >=  size_box[0]/2 )*size_box[0]
    distances[:,:,0] += ( distances[:,:,0]  <  -size_box[0]/2 )*size_box[0]
    distances[:,:,1] -= ( distances[:,:,1]  >=  size_box[1]/2 )*size_box[1]
    distances[:,:,1] += ( distances[:,:,1]  <  -size_box[1]/2 )*size_box[1]
    distances[:,:,2] -= ( distances[:,:,2]  >=  size_box[2]/2 )*size_box[2]
    distances[:,:,2] += ( distances[:,:,2]  <  -size_box[2]/2 )*size_box[2]
    return(distances)

import argparse
class parserNP:
    pass
core = parserNP()
parser = argparse.ArgumentParser()
parser.add_argument('--datafile_path')
args = parser.parse_args()
datafile_path = args.datafile_path

# Specify input files for the structure (GRO) and trajectory (XTC) to analyze
input_GRO = datafile_path + '/md.gro'
input_XTC = datafile_path + '/md.xtc'

# Load the structure and its trajectory
traj = md.load(input_XTC, top=input_GRO)

# Load the topology (the associated index of each atom and its type of atom)
top = traj.topology

# Extract trajectory information that may be useful: timesteps, number of frames, box sizes
md_sim_time   = traj.time
md_num_frames = 64 # traj.n_frames
md_size_box   = traj.unitcell_lengths

# Store topologies by atom name
top_W = top.select('name W')
top_NA = top.select('name NA')
top_CL = top.select('name CL')
top_NACL = top.select('name NA CL')

# Store trajectories/positions by atom type. For ref: traj.xyz[all_frames, atom_indices, all_coordinates]
pos_W = traj.xyz[:, top_W, :]
pos_NA = traj.xyz[:, top_NA, :]
pos_CL = traj.xyz[:, top_CL, :]
pos_NACL = traj.xyz[:, top_NACL, :]

# Generate radial bins
r_i, r_f, dr = 0, 4, 0.01 # nm
radii = np.arange(r_i, r_f + dr, dr)[np.newaxis,:]
counts = np.zeros(len(radii))

# Specify variables to use for plotting
g_r = np.zeros([md_num_frames, len(radii[0])])
r   = radii[0]
for frame in range(md_num_frames):
    print("Analyzing frame " + str(frame))
    
    # Compute the distance between each atom and every other atom
    distances = getDistancesWithPBC_XYZ(pos_W[frame], pos_W[frame], md_size_box[frame])
    norms = np.linalg.norm(distances, axis=2).T
    
    # Compute the density of the selection
    density_sel = len(norms[0,:]) / (md_size_box[frame][0] * md_size_box[frame][1] * md_size_box[frame][2] )
    
    # Re-arrange radii array to match the number of atoms in selection
    bins = np.tile( radii, (len(norms[0]), 1) )
    
    # Compute volume of each shell
    bins_vol = np.array([ 4/3*np.pi*( (r+dr)**3 - (r)**3 ) for r in radii ])
    
    # Bin each selection atom if found within each bin with respect to the reference selection
    binned = np.array( [ (pos[:, np.newaxis] < bins + dr).cumsum(axis=1).cumsum(axis=1) == 1 for pos in norms ] )
    binned_sum = np.sum( np.sum( binned , axis=0 ), axis=0, dtype="float64" )[np.newaxis, :]
    
    # Corrects for i = j 
    binned_sum[0,0] = 0
    
    # Normalize to obtain g(r) (convergence to 1)
    binned_sum /= bins_vol
    binned_sum /= density_sel
    binned_sum /= len(norms[:,0])
    
    # Store the normalized counts 
    g_r[frame] = binned_sum

# Compute average g(r)
g_r_mean = np.average(g_r, axis=0)

# Plot RDF
nrows, ncols = 1, 1
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(4,4))
ax.plot(r, g_r_mean)

ax.set_xlim(0,2)
ylim_UL = [ 4*(pair == 'W-W') + 4*(pair == 'NACL-W') + 1.5*(pair == 'NA-NA') + 8*(pair == 'NA-CL') ][0]
ylim_LL = [ -0.5*(pair == 'W-W') + -0.5*(pair == 'NACL-W') + -0.1*(pair == 'NA-NA') + -1*(pair == 'NA-CL') ][0]
ax.set_ylim(ylim_LL,ylim_UL)

fig.savefig(datafile_path + '/plot_rdf.png', bbox_inches = 'tight', dpi=800)


# ###############################################
# ### EXPERIMENTAL CODE FOR PARALLEL ANALYSIS ###
# ###############################################
# import multiprocessing
# from multiprocessing import Pool
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
# from matplotlib import rc
# import matplotlib as mpl
# from matplotlib import mathtext
# plt.rcParams.update({
#     'text.usetex':False,
#     'font.family':'Arial',
#     'font.sans-serif':['Arial'],
#     'mathtext.default':'regular',
#     })
# import os
# from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes
# import mdtraj as md
# def getDistancesWithPBC_XYZ(positions_i, positions_j, size_box):
#     """ ====================================================\n
#         === Provide coordinates of atom i (positions_i). ===\n
#         === Provide coordinates of atom j (positions_j). ===\n
#         === Provide size of box (size_box).              ===\n
#         === Return distances array between i and j.      ===\n
#         ====================================================\n """
#     # Take distance between particle i to every other particle j.
#     distances = positions_i[:,np.newaxis,:] - positions_j[np.newaxis,:,:]
#     # Apple PBC in X and Y dimensions.
#     distances[:,:,0] -= ( distances[:,:,0]  >=  size_box[0]/2 )*size_box[0]
#     distances[:,:,0] += ( distances[:,:,0]  <  -size_box[0]/2 )*size_box[0]
#     distances[:,:,1] -= ( distances[:,:,1]  >=  size_box[1]/2 )*size_box[1]
#     distances[:,:,1] += ( distances[:,:,1]  <  -size_box[1]/2 )*size_box[1]
#     distances[:,:,2] -= ( distances[:,:,2]  >=  size_box[2]/2 )*size_box[2]
#     distances[:,:,2] += ( distances[:,:,2]  <  -size_box[2]/2 )*size_box[2]
#     return(distances)
# import argparse
# class parserNP:
#     pass
# core = parserNP()
# parser = argparse.ArgumentParser()
# parser.add_argument('--datafile_path')
# args = parser.parse_args()
# datafile_path = args.datafile_path
# def computeRDF(FRAME_INDEX):
#     print("Analyzing frame " + str(FRAME_INDEX))
#     #g_r = []
#     # Compute the distance between each atom and every other atom
#     distances = getDistancesWithPBC_XYZ(pos_W[FRAME_INDEX], pos_W[FRAME_INDEX], md_size_box[FRAME_INDEX])
#     norms = np.linalg.norm(distances, axis=2).T
#     # Compute the density of the selection
#     density_sel = len(norms[0,:]) / (md_size_box[FRAME_INDEX][0] * md_size_box[FRAME_INDEX][1] * md_size_box[FRAME_INDEX][2] )
#     # Re-arrange radii array to match the number of atoms in selection
#     bins = np.tile( radii, (len(norms[0]), 1) )
#     # Compute volume of each shell
#     bins_vol = np.array([ 4/3*np.pi*( (r+dr)**3 - (r)**3 ) for r in radii ])
#     # Bin each selection atom if found within each bin with respect to the reference selection
#     binned = np.array( [ (pos[:, np.newaxis] < bins + dr).cumsum(axis=1).cumsum(axis=1) == 1 for pos in norms ] )
#     binned_sum = np.sum( np.sum( binned , axis=0 ), axis=0, dtype="float64" )[np.newaxis, :]
#     # Corrects for i = j
#     binned_sum[0,0] = 0
#     # Normalize to obtain g(r) (convergence to 1)
#     binned_sum /= bins_vol
#     binned_sum /= density_sel
#     binned_sum /= len(norms[:,0])
#     # Store the normalized counts
#     # g_r = binned_sum
#     return binned_sum
# # Specify input files for the structure (GRO) and trajectory (XTC) to analyze
# input_GRO = datafile_path + '/prod.gro'
# input_XTC = datafile_path + '/prod.xtc'
# # Load the structure and its trajectory
# traj = md.load(input_XTC, top=input_GRO)
# # Load the topology (the associated index of each atom and its type of atom)
# top = traj.topology
# # Extract trajectory information that may be useful: timesteps, number of frames, box sizes
# md_sim_time   = traj.time
# md_num_frames = 64 #traj.n_frames
# md_size_box   = traj.unitcell_lengths
# # Store topologies by atom name
# top_W = top.select('name W')
# top_NA = top.select('name NA')
# top_CL = top.select('name CL')
# top_NACL = top.select('name NA CL')
# # Store trajectories/positions by atom type. For ref: traj.xyz[all_frames, atom_indices, all_coordinates]
# pos_W = traj.xyz[:, top_W, :]
# pos_NA = traj.xyz[:, top_NA, :]
# pos_CL = traj.xyz[:, top_CL, :]
# pos_NACL = traj.xyz[:, top_NACL, :]
# # Generate radial bins
# r_i, r_f, dr = 0, 4, 0.01 # nm
# radii = np.arange(r_i, r_f + dr, dr)[np.newaxis,:]
# counts = np.zeros(len(radii))
# # Specify variables to use for plotting
# #g_r = np.zeros([md_num_frames, len(radii[0])])
# r   = radii[0]
# # Compute average g(r)
# pool = Pool(processes=64)
# g_r_mean = np.array(pool.map(computeRDF, (FRAME_INDEX for FRAME_INDEX in range(md_num_frames))))
# g_r_mean = np.mean(g_r_mean, axis=0)[0]
# # Plot RDF
# nrows, ncols = 1, 1
# fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(4,4))
# ax.plot(r, g_r_mean)
# ax.set_xlim(0,2)
# ylim_UL = [ 4*(pair == 'W-W') + 4*(pair == 'NACL-W') + 1.5*(pair == 'NA-NA') + 8*(pair == 'NA-CL') ][0]
# ylim_LL = [ -0.5*(pair == 'W-W') + -0.5*(pair == 'NACL-W') + -0.1*(pair == 'NA-NA') + -1*(pair == 'NA-CL') ][0]
# ax.set_ylim(ylim_LL,ylim_UL)
# fig.savefig(datafile_path + '/plot_rdf.png', bbox_inches = 'tight', dpi=800)









