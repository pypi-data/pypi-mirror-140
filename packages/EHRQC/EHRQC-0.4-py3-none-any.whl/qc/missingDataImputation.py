import numpy as np
import pandas as pd

from sklearn.metrics import r2_score

import impyute as impy
import miceforest as mf
from statsmodels.multivariate.pca import PCA
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA as sklearnPCA
from utils import MissForest


def compare(fullDf, p=0.1):
    mask = np.random.choice(a=[True, False], size=fullDf.shape, p=[p, 1-p])
    missingDf = fullDf.mask(mask)

    meanImputer = SimpleImputer(strategy='mean')
    meanImputedData = meanImputer.fit_transform(missingDf)
    meanImputedDf = pd.DataFrame(meanImputedData, columns=[(col + '_mean') for col in missingDf.columns], index=missingDf.index)
    meanR2 = r2_score(fullDf, meanImputedDf)

    medianImputer = SimpleImputer(strategy='median')
    medianImputedData = medianImputer.fit_transform(missingDf)
    medianImputedDf = pd.DataFrame(medianImputedData, columns=[(col + '_median') for col in missingDf.columns], index=missingDf.index)
    medianR2 = r2_score(fullDf, medianImputedDf)

    knnImputer = KNNImputer()
    knnImputedData = knnImputer.fit_transform(missingDf)
    knnImputedDf = pd.DataFrame(knnImputedData, columns=[(col + '_knn') for col in missingDf.columns], index=missingDf.index)
    knnR2 = r2_score(fullDf, knnImputedDf)

    mfImputer = MissForest()
    mfImputedData = mfImputer.fit(missingDf).transform(missingDf)
    mfImputedDf = pd.DataFrame(mfImputedData, columns=[(col + '_mf') for col in missingDf.columns], index=missingDf.index)
    mfR2 = r2_score(fullDf, mfImputedDf)

    emImputedData = impy.em(missingDf.to_numpy())
    emImputedDataDf = pd.DataFrame(emImputedData, columns=[(col + '_em') for col in missingDf.columns], index=missingDf.index)
    emR2 = r2_score(fullDf, emImputedDataDf)

    miKernel = mf.ImputationKernel(
    missingDf,
    datasets=4,
    save_all_iterations=True,
    random_state=1
    )
    miKernel.mice(2)
    miImputedDataDf = miKernel.complete_data(dataset=0, inplace=False)
    miImputedDf = pd.DataFrame(miImputedDataDf.to_numpy(), columns=[(col + '_mi') for col in missingDf.columns], index=missingDf.index)
    miR2 = r2_score(fullDf, miImputedDf)

    return meanR2, medianR2, knnR2, mfR2, emR2, miR2


def impute(dataDf, algorithm):

    if algorithm == 'mean':
        meanImputer = SimpleImputer(strategy='mean')
        meanImputedData = meanImputer.fit_transform(dataDf)
        imputedDf = pd.DataFrame(meanImputedData, columns=[(col + '_mean') for col in dataDf.columns], index=dataDf.index)
    if algorithm == 'median':
        medianImputer = SimpleImputer(strategy='median')
        medianImputedData = medianImputer.fit_transform(dataDf)
        imputedDf = pd.DataFrame(medianImputedData, columns=[(col + '_median') for col in dataDf.columns], index=dataDf.index)
    if algorithm == 'knn':
        knnImputer = KNNImputer()
        knnImputedData = knnImputer.fit_transform(dataDf)
        imputedDf = pd.DataFrame(knnImputedData, columns=[(col + '_knn') for col in dataDf.columns], index=dataDf.index)
    if algorithm == 'miss_forest':
        mfImputer = MissForest()
        mfImputedData = mfImputer.fit(dataDf).transform(dataDf)
        imputedDf = pd.DataFrame(mfImputedData, columns=[(col + '_mf') for col in dataDf.columns], index=dataDf.index)
    if algorithm == 'expectation_maximization':
        emImputedData = impy.em(dataDf.to_numpy())
        imputedDf = pd.DataFrame(emImputedData, columns=[(col + '_em') for col in dataDf.columns], index=dataDf.index)
    if algorithm == 'multiple_imputation':
        miKernel = mf.ImputationKernel(
        dataDf,
        datasets=4,
        save_all_iterations=True,
        random_state=1
        )
        miKernel.mice(2)
        miImputedDataDf = miKernel.complete_data(dataset=0, inplace=False)
        imputedDf = pd.DataFrame(miImputedDataDf.to_numpy(), columns=[(col + '_mi') for col in dataDf.columns], index=dataDf.index)

    return imputedDf
