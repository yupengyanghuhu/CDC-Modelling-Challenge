import pandas as pd
import numpy as np
import numpy.matlib as npm
import scipy.optimize
import matplotlib.pyplot as plt
from matplotlib import cm
import os
# import pyDOE
from timeit import default_timer as timer
from datetime import timedelta
import multiprocessing


from core.MCMCPosteriorSamplingFunction import MCMCPosteriorSampling

def main():
	
	# sigma2_err_known_vec = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	# proposal_variance_factor_vec = [10e4, 10e4, 10e4, 10e4, 10e4, 10e4, 10e4, 10e4, 10e4, 10e4, 5e4, 5e4, 5e4, 5e4, 5e4, 5e4, 5e4, 5e4, 5e4, 5e4]
	sigma2_err_known_vec = [10, 100, 1000, 10000]
	proposal_variance_factor_vec = [10e2, 10e2, 10e2, 10e2]

	runs = []
	for runID in range(len(sigma2_err_known_vec)):

		input_dict = {}
		input_dict['Sim'] = 'MMOD'
		input_dict['thetaprior'] = 'Final'
		input_dict['Model'] = 'Extended'
		input_dict['GeogScale'] = 'Global'
		input_dict['Location'] = ['USCounty']
		input_dict['FitStartDay'] = '3/1/2020'
		input_dict['FitLastDay'] = '5/15/2020'
		input_dict['LockdownBegin'] = 15
		input_dict['LockdownDuration'] = 75
		input_dict['InitialInfections'] = 1
		input_dict['InitialExposedMult'] = 5
		input_dict['iterations'] = 10000
		input_dict['initial_sample'] = [7.16e-01,4.97e-01,1.10e-01,1.21e-01,9.03e-01,3.18e-01,2.06e-01,1.85e-02,4.50e-02,9.83e-01,1.33e-01]
		input_dict['sigma2_err_known'] = sigma2_err_known_vec[runID]
		input_dict['proposal_variance_factor'] = proposal_variance_factor_vec[runID]
	
		runs.append([input_dict])
	
	jobs = []
	for runID in range(len(runs)):
		jobs.append(multiprocessing.Process(target = MCMCPosteriorSampling, args = runs[runID]))
	
	for j in jobs:
		j.start()
	
	for j in jobs:
		j.join()

if __name__ == "__main__":
	# execute only if run as a script
	main()

