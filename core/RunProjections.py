import numpy as np
import os
import pandas as pd
import scipy.optimize
import matplotlib.pyplot as plt
from matplotlib import cm
import multiprocessing

import core.CountryModel
import core.EpiEquations
import core.PostProcessing
import core.ProcessData
import core.CalculateMetrics
import core.PlotFunctions


def RunProjections(AcceptedParms, TotalTime, fitData, Population, InitialInfections, InitialExposedMult, lockdown_begin, lockdown_duration, 
    FittedDates, SimLabel):
    print('*****************  Loading Input Data')
    inFolder = 'MCParameterSelection'
    outFolder = 'results'
    InfectionStart = 1              # Intervention start time
    numSims = len(AcceptedParms)

    # Run Model
    Dmat = np.zeros((TotalTime,numSims))
    INmat = np.zeros((TotalTime,numSims))
    IHmat = np.zeros((TotalTime,numSims))
    CumIHmat = np.zeros((TotalTime,numSims))
    CumINmat = np.zeros((TotalTime,numSims))
    CumTotInfmat = np.zeros((TotalTime,numSims))
    TotInfmat = np.zeros((TotalTime,numSims))
    print(AcceptedParms)


    for i in range(numSims):
        iParams = AcceptedParms[i]
        parmsFit = iParams[:-2]
        scenario = iParams[-2:]

        tmin = 1
        tsteps = tmax = lockdown_begin #57# 185
        tdom = np.linspace(tmin, tmax, tsteps)
        InterventionMult = 1 
        Y0, Constants, CompNames = core.CountryModel.SetupCountryModel(parmsFit, InterventionMult, Population, InitialInfections, InitialExposedMult)
        Yout1 = core.CountryModel.RunCountrySim(core.EpiEquations.EpiEquationsExtended, Y0, tdom, Constants)
        NewInitialConditions = Yout1[tmax-1,:]

        # Stage 2 (Intervention)
        tmax = tsteps = lockdown_duration + 1 #30 #1
        tdom = np.linspace(tmin, tmax, tsteps)
        InterventionMult = scenario[0] #1 + lockdown_intensity/100 # #.56 #setting to 1 removes intervention to run baseline model
        Y0, Constants, CompNames = core.CountryModel.SetupCountryModel(parmsFit, InterventionMult, Population, InitialInfections, InitialExposedMult)
        Yout2 = core.CountryModel.RunCountrySim(core.EpiEquations.EpiEquationsExtended, NewInitialConditions, tdom, Constants)
        NewInitialConditions = Yout2[tmax-1,:]

        # Stage 3 (Retrun to Baseline)
        tmax = tsteps = TotalTime + 1 - (lockdown_begin + lockdown_duration) #1
        tdom = np.linspace(tmin, tmax, tsteps)
        InterventionMult = scenario[1] #.75#1
        Y0, Constants, CompNames = core.CountryModel.SetupCountryModel(parmsFit, InterventionMult, Population, InitialInfections, InitialExposedMult)
        Yout3 = core.CountryModel.RunCountrySim(core.EpiEquations.EpiEquationsExtended, NewInitialConditions, tdom, Constants)

        ALLout = np.vstack([Yout1,Yout2[+1:,:],Yout3[+1:,:]])
        S, E, C, IN, IH, D, R, CumC, CumIN, CumIH = core.Utils.AssembleOutputExtended(ALLout, 1)
        INmat[:,i] = IN.sum(1)
        IHmat[:,i] = IH.sum(1)
        TotInfmat[:,i] = IN.sum(1) + IH.sum(1) 
        Dmat[:,i] = D.sum(1)
        CumINmat[:,i] = CumIN.sum(1)
        CumIHmat[:,i] = CumIH.sum(1)
        CumTotInfmat[:,i] = CumIN.sum(1) + CumIH.sum(1)
    try:
        os.mkdir(outFolder)
    except:
        pass

    CumIActual = fitData[0]
    CumDActual = fitData[1] 

    # Write Results    
    core.PostProcessing.WriteSeriesCsv(CumINmat, 'Cumulative Symptomatic', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(CumIHmat, 'Cumulative Hospitalized', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(CumTotInfmat, 'Cumulative Total Infections', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(TotInfmat, 'Total Infections', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(Dmat, 'Deaths', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(INmat, 'Symptomatic', outFolder, SimLabel)
    core.PostProcessing.WriteSeriesCsv(IHmat, 'Hospitalized', outFolder, SimLabel)

    # Plot Results
    core.PlotFunctions.PlotInfectionSubsystemBounds(tmin, CumIActual, CumDActual, CumINmat, CumIHmat, Dmat, outFolder, SimLabel)
