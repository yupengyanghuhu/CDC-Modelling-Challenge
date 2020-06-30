import pandas as pd
import math
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

import core.CountryModel
import core.EpiEquations
import core.PostProcessing
import core.ProcessData
import core.Utils
import core.CostFunction
import core.RunProjections

        
def main():

    Sim = 'MMOD'
    thetaprior = 'Final'
    Model = 'Extended'
    FitStartDay = '3/1/2020'
    FitLastDay = '5/15/2020'
    InitialInfections = 1
    InitialExposedMult = 5
    lockdown_begin = 15 
    lockdown_duration = 75
    
    print('Starting Posterior Sampling for ' + Sim + ' with ' + thetaprior + ' theta priors')
    StorageFolder = 'MCMC_' + Sim + thetaprior + Model + '_data' 
    # Import Case Data
    Population = 100000
    Confirmed, Deaths, Dates = core.ProcessData.ImportCountyCaseData(FitStartDay, FitLastDay)
    fitData = np.vstack([Confirmed, Deaths])
    AcceptedFile = 'AcceptedUniqueParameters_MMODFinalExtended_sigma2err_10000_SigmaPrFact_1000.0.txt'

    tmin = 1
    tmax = tsteps = 270
    fitTime = np.linspace(tmin,tmax,tsteps)    
    AcceptedUniqueParameters = np.loadtxt(StorageFolder + '/' + AcceptedFile)

    SimLabel = Sim + thetaprior + Model + 'Closed'
    core.RunProjections.RunProjections(AcceptedUniqueParameters, tmax, fitData, Population, InitialInfections, 
        InitialExposedMult, lockdown_begin, lockdown_duration, Dates, SimLabel)


    SimLabel = Sim + thetaprior + Model + 'Open'
    AcceptedUniqueParametersOpen = AcceptedUniqueParameters
    for i in range(len(AcceptedUniqueParameters)):
        AcceptedUniqueParametersOpen[i][-1] = 1
    core.RunProjections.RunProjections(AcceptedUniqueParametersOpen, tmax, fitData, Population, InitialInfections, 
        InitialExposedMult, lockdown_begin, lockdown_duration, Dates, SimLabel)

    SimLabel = Sim + thetaprior + Model + '2weeks'
    lockdown_duration2 = 182 + 14
    core.RunProjections.RunProjections(AcceptedUniqueParametersOpen, tmax, fitData, Population, InitialInfections, 
        InitialExposedMult, lockdown_begin, lockdown_duration2, Dates, SimLabel)

    # SimLabel = Sim + thetaprior + Model + '1percent'


if __name__ == "__main__":
    # execute only if run as a script
    main()

