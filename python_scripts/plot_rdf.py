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
parser.add_argument('--datafile_path')
args = parser.parse_args()

datafile_path = args.datafilepath

pairs = ['W-W','NACL-W','NA-NA','NA-CL']

nrows, ncols = 2, 2
fig, ax = plt.subplots( nrows=nrows, ncols=ncols, figsize=(8,8) )
row, col = 0, 0
for pair in pairs: 
    
    datafile = datafile_path + '/' + pair + '.xvg'
    data = np.loadtxt( datafile, comments=['#','@'] )

    ax[row, col].plot(data[:,0],
                      data[:,1],
                      label=pair)
    ax[row, col].legend()
    ax[row, col].set_xlabel('$r$ (nm)')
    ax[row, col].set_ylabel('$g(r)$')
    
    xticks = np.arange(0, 2.5, 0.5)
    ax[row, col].set_xticks(xticks)
    if pair == 'W-W':       yticks = np.arange(0, 5, 1)
    elif pair == 'NACL-W': yticks = np.arange(0, 5, 1)
    elif pair == 'NA-NA':   yticks = np.arange(0, 2, 0.5)
    elif pair == 'NA-CL':   yticks = np.arange(0, 10, 2)
    ax[row, col].set_yticks(yticks)
    
    ax[row, col].set_xlim(0,2)
    ylim_UL = [ 4*(pair == 'W-W') + 4*(pair == 'NA CL-W') + 1.5*(pair == 'NA-NA') + 8*(pair == 'NA-CL') ][0]
    ylim_LL = [ -0.5*(pair == 'W-W') + -0.5*(pair == 'NA CL-W') + -0.1*(pair == 'NA-NA') + -1*(pair == 'NA-CL') ][0]
    ax[row, col].set_ylim(ylim_LL,ylim_UL)

    col += 1
    if col == 2: 
       row += 1
       col = 0
    
fig.savefig('plot_rdf.png', bbox_inches = 'tight', dpi=800)

