import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='EHRQC',
    version='0.2',
    author='Yashpal Ramakrishnaiah <ryashpal.ramakrishnaiah1@monash.edu>, Sonika Tyagi <sonika.tyagi@monash.edu>',
    author_email='ryashpal.ramakrishnaiah1@monash.edu, sonika.tyagi@monash.edu',
    description='Package for performing QC on Electronic Health Record (EHR) data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ryashpal/EHRQC',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=[
        "demographicsGraphs"
        , "vitalsGraphs"
        , "labMeasurementsGraphs"
        , "vitalsAnomalies"
        , "labMeasurementsAnomalies"
        , "missingDataImputation"
        , "anomaly"
        , "utils"
        ],             # Name of the python package
    package_dir={'qc':'qc'},     # Directory of the source code of the package
    install_requires=[
        ],
)
