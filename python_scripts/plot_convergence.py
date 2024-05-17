# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 20:56:00 2023

@author: huangzhu
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Arial'

import argparse
class parserNP:
    pass
core = parserNP()
parser = argparse.ArgumentParser()
parser.add_argument('--datafile')
args = parser.parse_args()
datafile = args.datafile

data = np.loadtxt( datafile, comments=['#','@'] )

nrows, ncols = 1, 1

### PLOT TEMPERATURE TIMESERIES
fig, ax = plt.subplots( nrows=nrows, ncols=ncols, figsize=(4,4) )
ax.plot(data[:,0],
        data[:,1])
ax.set_xlabel('Simulation Time (ps)')
ax.set_ylabel('Temperature (K)')
fig.savefig('plot_convergence_temperature.png', bbox_inches = 'tight', dpi=800)
fig.tight_layout()

### PLOT PRESSURE TIMESERIES
fig, ax = plt.subplots( nrows=nrows, ncols=ncols, figsize=(4,4) )
ax.plot(data[:,0],
        data[:,2])
ax.set_xlabel('Simulation Time (ps)')
ax.set_ylabel('Pressure (bar)')
fig.savefig('plot_convergence_pressure.png', bbox_inches = 'tight', dpi=800)
fig.tight_layout()

### PLOT DENSITY TIMESERIES
fig, ax = plt.subplots( nrows=nrows, ncols=ncols, figsize=(4,4) )
ax.plot(data[:,0],
        data[:,3])
ax.set_xlabel('Simulation Time (ps)')
ax.set_ylabel('Density (kg/m{^3})')
fig.savefig('plot_convergence_density.png', bbox_inches = 'tight', dpi=800)
fig.tight_layout()