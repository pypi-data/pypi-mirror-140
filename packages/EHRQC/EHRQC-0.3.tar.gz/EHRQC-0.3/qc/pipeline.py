from extract import extractMimicDemographics
from extract import extractOmopDemographics
from extract import extractMimicVitals
from extract import extractOmopVitals
from extract import extractMimicLabMeasurements
from extract import extractOmopLabMeasurements

from demographicsGraphs import plot as plotDemographicsGraphs
from vitalsGraphs import plot as plotVitalsGraphs
from labMeasurementsGraphs import plot as plotLabMeasurementsGraphs

from missingDataImputation import compare as missingDataImputationCompare
from missingDataImputation import impute as missingDataImputationImpute


def run(source='mimic', type='demographics', graph=False, impute_missing=False):

    print('extracting data')
    data = None
    if (source == 'mimic') and (type == 'demographics'):
        data = extractMimicDemographics()
    elif (source == 'omop') and (type == 'demographics'):
        data = extractOmopDemographics()
    if (source == 'mimic') and (type == 'vitals'):
        data = extractMimicVitals()
    elif (source == 'omop') and (type == 'vitals'):
        data = extractOmopVitals()
    if (source == 'mimic') and (type == 'lab_measurements'):
        data = extractMimicLabMeasurements()
    elif (source == 'omop') and (type == 'lab_measurements'):
        data = extractOmopLabMeasurements()

    if graph:
        print('generating graphs')
        if (type == 'demographics'):
            plotDemographicsGraphs(data[['age', 'weight', 'height', 'gender', 'ethnicity', 'dob', 'dod']])
        elif (type == 'vitals'):
            plotVitalsGraphs(data)
        elif (type == 'lab_measurements'):
            plotLabMeasurementsGraphs(data)

    if impute_missing:
        print('imputing missing data')
        fullData = data.dropna()
        meanR2, medianR2, knnR2, mfR2, emR2, miR2 = missingDataImputationCompare(fullData)

        print('mean: ', meanR2, 'median: ', medianR2, 'knn: ', knnR2, 'mf: ', mfR2, 'em: ', emR2, 'mi: ', miR2)

        if (meanR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using mean imputation')
            data = missingDataImputationImpute(data, 'mean')
        elif (medianR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using median imputation')
            data = missingDataImputationImpute(data, 'median')
        elif (knnR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using knn imputation')
            data = missingDataImputationImpute(data, 'knn')
        elif (mfR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using mf imputation')
            data = missingDataImputationImpute(data, 'miss_forest')
        elif (emR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using em imputation')
            data = missingDataImputationImpute(data, 'expectation_maximization')
        elif (miR2 == max([meanR2, medianR2, knnR2, mfR2, emR2, miR2])):
            print('using mi imputation')
            data = missingDataImputationImpute(data, 'multiple_imputation')

    return data


if __name__ == '__main__':
    data = run(source='mimic', graph=True, impute_missing=True)
    print(data.head())
