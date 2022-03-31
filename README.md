# GEOM 4009 - Riparian Connectivity

Welcome to our GEOM 4009 Riparian Connectivity project. This is a student-led project at Carleton University in Ottawa, ON.

Authors: Benjamin Colbourne, John Foster, Taji Hamilton, Haley Nicholson

## Description

Riparian-Connectivity is a Python script that runs at the command line interface. It attempts to quanitify several geometric characteristics of vegetation falling within the riparian buffer of a watershed's surface waters. It does this by:

1. Creating a riparian buffer around the water bodies and water courses of a watershed
2. Calculating the Normalized Difference Vegetation Index (NDVI) of the riparian buffer
3. Classifying the riparian buffer as vegetation and not-vegetation using an NDVI threshold
4. Calculating descriptive statistics on the vegetation and not-vegetation features found with the riparian buffer

The [Usage](#usage) section of the README contains important information about the necessary inputs, the processing that occurs, and how to access the results and intermediate data. Additionally, relevant definitions have been provided in the [Definitions](#definitions) section.

This script is a work in progress, as is the documentation. Please bear with us while we develop it further.

## Installation

### Download

Just [click here](https://github.com/GEOM4009-riparian-connectivity/riparian-connectivity-public/releases) to download a copy of the latest release from GitHub.

### Dependencies / Conda Environment

Riparian-Connectivity depends on a number of external Python modules:

- folium
- geopandas
- joblib
- numpy
- matplotlib
- pandas
- rasterio
- rioxarray
- shapely
- scikit-image

To manage these dependencies, Riparian-Connectivity is best run within the `riparian_connect` Conda environment, as defined in the `environment.yml` file.

>Note: If you're not familiar with Conda, it's a Python package and environment manager than is most commonly downloaded as part of the [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) Python distributions. Anaconda is a very large download that includes Conda, multiple other applications, and hundreds of pre-installed modules. Miniconda on the other hand, is bare minimum installation that only includes Conda, Python, and a minimal number of useful modules. When an environment is created, Conda installs only those packages that are needed - this makes Miniconda better than Anaconda if you want a simple and lightweight installation.

The `riparian_connect` Conda environment can be installed at the command line by navigating to the directory you downloaded your copy of this repository to and then running the following command.

```
conda env create -f environment.yml
```

If Conda stalls on the `Solving environment` step you might want to try [Mamba](https://mamba.readthedocs.io/en/latest/index.html) instead. Mamba is fully compatible with Conda and is often a much faster method for installing Conda environments. It's as simple as running the following two commands from your base Conda environment.

Install mamba:

```
conda install mamba -n base -c conda-forge
```

Create the environment:

```
mamba env create -f environment.yml
```

## Usage

### Start the Script

Once you have downloaded the package and installed the `riparian_connect` Conda environment, navigate to the directory containing the script (if you're not already there) and run the following commands.

Activate the environment:

```
conda activate riparian_connect
```

Run the script:

```
python -m riparian-connectivity
```

### Required Inputs for the Script

When the script starts it will begin by prompting you to enter a number of inputs. Information about each input is provided below. 


**1. Watershed name**

- The name used to label a subdirectory with the `results` directory which will contain the results of the analysis. It will also be included as an identifier in the table of results.


**2. File paths to the following files in Shapefile (.shp) or GeoPackage (.gpkg) format**

- Watershed boundary
	- Must have a geometry type of 'Polygon' or 'MultiPolygon'
	- Must contain only one feature - the watershed to be evaluated
- Water bodies (polygon)
	- Must have a geometry type of 'Polygon' or 'MultiPolygon'
	- Can contain one large "dissolved" feature or many features
- Water courses (line)
	- Must have a geometry type of 'LineString' or 'MultiLineString'

> Note: A good source for these files in Canada is the [National Hydro Network - NHN - GeoBase Series](https://open.canada.ca/data/en/dataset/a4b190fe-e090-4e6d-881e-b87956c07977) dataset.


**3. Path to an ESA Sentinel-2 multispectral image in the GeoTiff (.tiff) format** 

- It is important that this image has the following characteristics:
	- Red band as Band 4
	- NIR band as Band 8
	- A projected coordinate reference system with units in meters


**4. The riparian buffer width in meters**

- This value will determine the width of the buffer around the water bodies and water courses.

**5. The NDVI threshold**

- The NDVI threshold value will be used as the cut point for classifying the Sentinel-2 multispectral image's pixels into vegetation and not-vegetation classes. Values under the threshold will be considered not-vegetation and values equal to or over it will be considered vegetation. Only the pixels within the riparian buffer will be classified.
- To assist in the determination of an appropriate threshold a histogram of the NDVI values will be saved to the results directory and the path to it will be printed to the screen.
- Additionally, an experimental Otsu thresholding function will print a suggested NDVI cutoff to the screen.


## Analysis Output

Riparian-Connectivity will export files at each of the intermediate steps. These files can be evaluated in order to ensure that:

- Appropriate inputs were provided
- The script is running as expected
- To perform additional anaylsis on the intermediate data.

These files will be placed in a directory with the following relative path: `/results/my_watershed/`

If you run Riparian-Connectivity on the same watershed more than once it's a good idea to provide a unique name when prompted for the `Watershed name`. If the same name is repeatedly entered a number will be appended to the watershed's results folder to ensure the previous results will not be overwritten. e.g.  `/results/my_watershed_2/`

>Note: The list below contains all the intermediate file outputs for each function. They are organized by each function that produces an intermediate file; not all functions produce an intermediate file. A short description of what each output file is, and what it does has been provided. Each intermediate file can be loaded into a GIS application if one is interested in visualizing the results.

- `1-riparian_buffer.gpkg` - A GeoPackage file of the union of the water bodies and water course buffers.
- `2-riparian_buffer-NDVI.tiff` - A GeoTiff file of the Normalized Difference Vegetation Index image of the riparian buffer.
- `3-riparian_buffer-NDVI_histogram.png` - A PNG file of the histogram of the riparian buffer NDVI values.
- `3-riparian_buffer-vegetation.tiff` - A GeoTiff file of the classified riparian buffer where pixel values of 0 are no data, pixel values of 1 are  vegetation, and pixel values of 2 are not-vegetation.
- `4-riparian_buffer-not_vegetation.gpkg` - A GeoPackage file of the not-vegetation pixel class, converted to a vector format.
- `4-riparian_buffer-vegetation.gpkg` - A GeoPackage file of the vegetation pixel class, converted to a vector format.
- `4-riparian_buffer.gpkg` - A GeoPackage file of the riparian buffer, covering the same same extent as the vegetation and not-vegetation pixels.
- `4-statistics_table.csv` - A CSV file of the output statistics
- `5-report.html` - An HTML report containing the a table of the statistics and an interactive Folium map of the vegetation and not-vegetation features found within the riparian buffer.



## Definitions

### Description of Statistics

**Watershed area (km2)** - The total area of the watershed (km2), as represented by the user provided file.

**Riparian buffer area (km2)** - The total area (km2) of the riparian buffer. It is "pixelated", in that its boundary conforms to the boundary of the pixels that fell mostly (e.g. more than 50%) within the union of the dissolved buffers around the water bodies and water courses features provided by the user.

**Vegetation area (km2):** The total area (km2) of the pixels classified as vegetation within the riparian buffer. These pixels have an NDVI equal to or higher than the NDVI threshold provided by the user.

**Not-vegetation area (km2):** The total area (km2) of the pixels classified as not-vegetation within the riparian buffer. These pixels have an NDVI lower than the NDVI threshold provided by the user.

**Vegetation coverage (%):** Percentage of vegetation coverage within the riparian buffer. Equivalent to:
`(Vegetation area (km2) / Riparian buffer area (km2)) * 100`

**Non-vegetation coverage (%):** Percentage of not-vegetation coverage within the riparian buffer. `Non-vegetation coverage (%) = (Not-vegetation area (km2) / Riparian buffer area (km2)) * 100`

**Mean area of not-vegetation patches(km2):** Mean size (km2) of the not-vegetation features within the riparian buffer. Non-vegetation features are formed by contiguous pixels classed as not-vegetation.

**Number of riparian buffer features:** The total number of riparian buffer features in the watershed. Riparian buffer features are formed by contiguous pixels classed as either vegetation or not-vegetation. Equivalent to all the pixels that fell mostly (e.g. more than 50%) within the union of the dissolved buffers around the water bodies and water courses features provided by the user.

**Number of vegetation features:** The total number of vegetation features in the riparian buffer. Vegetation features are formed by contiguous pixels classed as vegetation.

**Number of not-vegetation features:** The total number of not-vegetation features in the riparian buffer. Not-vegetation features are formed by contiguous pixels classed as not-vegetation.

**Perimeter of riparian buffer (km):** The total perimeter (km) of the riparian buffer features.

**Perimeter of vegetation features (km):** The total perimeter (km) of the vegetation features.

**Perimeter of not-vegetation features (km):** The total perimeter of not-vegetation features.

**Vegetation Connectivity:** The quotient of the number of riparian buffer features divided by the number of vegetation features. `connectivity = Number of riparian buffer features / Number of vegetation features`. If there are an equal number of vegetation features as there are riparian buffer features then there are is no fragmentation of the riparian buffer and the result would be `1`. As the number of vegetation features increases, the level of connectivity decreases, lowering the connectivity value towards `0`.

**Vegetation Compactness:** An attempt to quantify the the compactness of the riparian vegetation features. The long name of this could be 'normalized isoperimetric ratio'. The [Isoperimetric Ratio](https://en.wikipedia.org/wiki/Isoperimetric_ratio) is the perimeter squared / area. The minimum isoperimetric ratio is for a circle and it yields a compactness result of 4π. If we get the isoperimetric ratio of the vegetation features and the isoperimetric ratio of the buffer features then we can normalize the isoperimetric ratio of the vegetation features to that of the buffer features. In python it looks like this

```
# Reference compactness i.e. riparian buffer compactness
riparian_compactness =  riparian_perimeter**2 / riparian_area

# Actual compactness i.e. riparian vegetation compactness
vegetation_compactness = veg_perimeter**2 / veg_area

# Normalized compactness
compactness =  riparian_compactness / actual_compactness
```

## On-going Development

This project is ongoing and several more releases are planned in order to polish the functions, further develop the statistical outputs, and work through any bugs.


### Testing Notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GEOM4009-riparian-connectivity/riparian-connectivity-public/HEAD)

Take a look at our exploratory test notebooks by following the Binder link and then opening the `full_workflow-test.ipynb` and `connectivity_stats-test.ipynb` notebooks files in the Jupyter Lab file explorer that will launch in your browser. It might take some time for Binder to build the environment if any changes to the repo were made recently.


