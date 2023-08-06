import os
import psycopg2
import pandas as pd

def extractMimicDemographics():
    # information used to create a database connection
    sqluser = 'postgres'
    dbname = 'mimic4'
    hostname = 'localhost'
    port_number = 5434

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(dbname=dbname, user=sqluser, host=hostname, port=port_number, password='mysecretpassword')

    curDir = os.path.dirname(__file__)
    mimicDemographicsPath = os.path.join(curDir, '../extract/sql/mimic_demographics.sql')
    mimicDemographicsFile = open(mimicDemographicsPath)
    mimicDemographicsDf = pd.read_sql_query(mimicDemographicsFile.read(), con)
    return mimicDemographicsDf


def extractOmopDemographics():
    # information used to create a database connection
    sqluser = 'postgres'
    dbname = 'mimic4'
    hostname = 'localhost'
    port_number = 5434

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(dbname=dbname, user=sqluser, host=hostname, port=port_number, password='mysecretpassword')

    curDir = os.path.dirname(__file__)
    mimicOmopDemographicsPath = os.path.join(curDir, '../extract/sql/mimic_omop_demographics.sql')
    mimicOmopDemographicsFile = open(mimicOmopDemographicsPath)
    mimicOmopDemographicsDf = pd.read_sql_query(mimicOmopDemographicsFile.read(), con)
    return mimicOmopDemographicsDf


def extractMimicVitals():
    # information used to create a database connection
    sqluser = 'postgres'
    dbname = 'mimic4'
    hostname = 'localhost'
    port_number = 5434

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(dbname=dbname, user=sqluser, host=hostname, port=port_number, password='mysecretpassword')

    curDir = os.path.dirname(__file__)
    mimicSelectedVitalsPath = os.path.join(curDir, '../extract/sql/mimic_selected_vitals.sql')
    mimicSelectedVitalsFile = open(mimicSelectedVitalsPath)
    mimicSelectedVitalsDf = pd.read_sql_query(mimicSelectedVitalsFile.read(), con)
    return mimicSelectedVitalsDf


def extractMimicOmopVitals():
    # information used to create a database connection
    sqluser = 'postgres'
    dbname = 'mimic4'
    hostname = 'localhost'
    port_number = 5434

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(dbname=dbname, user=sqluser, host=hostname, port=port_number, password='mysecretpassword')

    curDir = os.path.dirname(__file__)
    mimicOmopSelectedVitalsPath = os.path.join(curDir, '../extract/sql/mimic_omop_selected_vitals.sql')
    mimicOmopSelectedVitalsFile = open(mimicOmopSelectedVitalsPath)
    mimicOmopSelectedVitalsDf = pd.read_sql_query(mimicOmopSelectedVitalsFile.read(), con)
    return mimicOmopSelectedVitalsDf


def extractOmopLabMeasurements():
    # information used to create a database connection
    sqluser = 'postgres'
    dbname = 'mimic4'
    hostname = 'localhost'
    port_number = 5434

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(dbname=dbname, user=sqluser, host=hostname, port=port_number, password='mysecretpassword')

    curDir = os.path.dirname(__file__)
    mimicOmopSelectedLabMeasurementsPath = os.path.join(curDir, '../extract/sql/mimic_omop_selected_lab_measurements.sql')
    mimicOmopSelectedLabMeasurementsFile = open(mimicOmopSelectedLabMeasurementsPath)
    mimicOmopSelectedLabMeasurementsDf = pd.read_sql_query(mimicOmopSelectedLabMeasurementsFile.read(), con)
    return mimicOmopSelectedLabMeasurementsDf
