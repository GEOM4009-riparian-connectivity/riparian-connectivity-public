# GEOM 4009 - Riparian Connectivity

Welcome to our GEOM 4009 Riparian Connectivity project! This is a student-led project at Carleton University in Ottawa, ON.

## Description

Our Riparian-Connectivity Python package intends to quantify vegetation connectivity within the riparian buffer of a watershed's surface waters. The current release is our initial draft release (v0.1.1) and while it has been tested on the "sample1" dataset found in the `testing/sample_data` directory, it's possible there will be bugs and/or long computation times if run on other datasets.

This package is a work in progress, as is the documentation. Please bear with us as we develop it further.

## Installation

### Download

Just [click here](https://github.com/GEOM4009-riparian-connectivity/riparian-connectivity-public/releases) or on our repo's GitHub `Releases` link and then download a copy of this repository to your computer.

### Environment

Riparian-Connectivity is best run within the `riparian_dev` conda environment, as defined in the `riparian_dev_env.yml` file.

>Note: If you're not familiar with conda, it's a Python package and environment manager than is most commonly downloaded as part of the [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) Python distributions. Anaconda is a very large download that includes conda, multiple other applications, and hundreds of pre-installed packages. Miniconda on the other hand, is bare minimum installation that only includes conda, Python, and a minimal amount of useful packages. When an environment is created, conda installs only those packages that are needed - this makes Miniconda the best option if you want a simple and lightweight installation.


The `riparian_dev` conda environment can be installed at the command line by navigating to your local copy of the repository and then running the following command:

```
conda env create -f riparian_dev_env.yml
```

If conda stalls on the `Solving environment:` step you might want to try [Mamba](https://mamba.readthedocs.io/en/latest/index.html) instead. Mamba is fully compatible with conda and might be faster way to install the environment. It's as simple as running the following two commands from your base conda environment.

Install mamba:
```
conda install mamba -n base -c conda-forge
```

Create the environment:
```
mamba env create -f riparian_dev_env.yml
```

## Usage

Once you have downloaded the package and installed the environment, navigate to the directory containing the script (if you're not already there) and run the following commands.

Activate the environment:

```
conda activate riparian_dev
```

Run the script:

```
python -m riparian-connectivity
```

 This will start the script and it will begin by prompting you to enter inputs for the following:

1. **File paths to the following files in Shapefile (.shp) or GeoPackage (.gpkg) format**
	- Watershed boundary (polygon)
	- Water bodies (polygon)
	- Water courses (line)

 A good source for these files in Canada is the [National Hydro Network - NHN - GeoBase Series](https://open.canada.ca/data/en/dataset/a4b190fe-e090-4e6d-881e-b87956c07977) dataset.

2. **Path to a multispectral image (e.g. ESA Sentinel-2 image) in the GeoTiff (.tiff) format** 
	- It's important that this image has the red band as Band 4 and the NIR band as Band 8 (this is the standard). These bands will be used to calculate the Normalized Difference Vegetation Index (NDVI) of the riparian buffer.

3. **The riparian buffer width in meters.**
	- This is the distance away from each water body and water course that will be considered  within the riparian buffer.

 After these initial inputs have been entered the script will perform the  processing necessary to create the riparian buffer and calculate the NDVI. A  histogram of the NDVI values in an image format (.png) will be saved to file  and the path to it will be printed to the screen. Please refer to this  historgram to determine the suitable threshold value for the NDVI. Anything  over the threshold will be considered riparian vegetation, and anything  under it will be considered not-vegetation.

 Once you have decided on a suitable NDVI threshold please return to the prompt and input:

4. **The NDVI threshold**

Riparian-connectivity will then use that threshold to classify the imagery's pixels within the riparian buffer as vegetation or not-vegetation and then calculate statistics that represent a quantification of the riparian connectivity.

The statistical aspect of this is still very much a work in progress - see below for comments regarding on-going development.


## On-going Development

The draft script published as release v0.1.1 uses a specific `riparian_stats_testing()` function that matches the `full_workflow-test.ipynb` notebook found in this repo. This was done in order to evaluate the script's ability to output the same results as that notebook. Once the script has passed through GEOM 4009's Progress Report #3 milestone, a v0.2.0 release will be made that includes a draft of the actual `riparian_stats()` function under development.



### Testing Notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GEOM4009-riparian-connectivity/riparian-connectivity-public/HEAD)

Take a look at our test notebooks by following the Binder link and then opening the `full_workflow-test.ipynb` and `connectivity_stats-test.ipynb` notebooks files in the Jupyter Lab file explorer that will launch in your browser. It might take some time for Binder to build the environment if any changes to the repo were made recently.



