#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

File docstring to be completed



"""

# %% Import packages

# built-ins
import os
from pathlib import Path
import sys
import operator
import warnings

# data manipulation
import geopandas as gpd
import numpy as np
import pandas as pd
import rioxarray as rxr

# plotting
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# raster to vector function
from ast import literal_eval
from joblib import Parallel, delayed
import multiprocessing
from rasterio import features
from shapely.geometry import shape


# %% User input function - John


def user_input(input_message):
    """Get user input or q to quit."""
    raw_input = input(input_message)
    if raw_input.lower() == "q" or raw_input.lower() == "quit":
        print("\nGoodbye!")
        sys.exit()
    else:
        return raw_input


# %% 1) Function to read the vector and raster data - John
"""
To do
-----
    1. Check the geometry types of the vector data to ensure they have the correct types
    2. Check to ensure that all of the layers have the same spatial coverage
    4. Make the TUI less clunky

"""


def load_data_ui():
    """
    Provide a textual user interface for the loading of the required data.

    Returns
    -------
    data_dict : dictionary
        Returns a dictionary with each of the data objects as the value of an
        appropriately named key.
    """
    print("\nRiparian Connectivity v0.1")
    print("------------------------------------------------------------")
    print("Please enter required information or 'q' or 'quit' to quit.")
    print("------------------------------------------------------------")

    # Get the watershed name
    loaded = False
    while loaded == False:
        watershed_name = user_input("Watershed name: ")
        loaded = True

    # Read the watershed boundary vector data; only keep geometry, and dissolve
    loaded = False
    while loaded == False:
        input_path = user_input("\nPath to the watershed polygon file: ")
        try:
            watershed_path = os.path.join(*Path(input_path).parts)
            print("\nReading file...", end="")
            watershed_gdf = gpd.read_file(watershed_path)
            watershed_gdf = watershed_gdf[["geometry"]].dissolve()
            print("watershed polygon file loaded successfully.")
            loaded = True
        except:
            print("Error: Watershed polygon file not loaded successfully.\n")
            print("Please enter a path to a valid file or enter 'q' or 'quit' to quit.")

    # Read the water bodies vector data; only keep geometry, and dissolve
    loaded = False
    while loaded == False:
        input_path = user_input("\nPath to the water bodies polygon file: ")
        try:
            waterbodies_path = os.path.join(*Path(input_path).parts)
            print("\nReading file...", end="")
            waterbodies_gdf = gpd.read_file(waterbodies_path)
            waterbodies_gdf = waterbodies_gdf[["geometry"]].dissolve()
            print("Water bodies polygon file loaded successfully.")
            loaded = True
        except:
            print("Error: Water bodies polygon file not loaded successfully.\n")
            print("Please enter a path to a valid file or enter 'q' or 'quit' to quit.")

    # Read the water courses vector data; only keep geometry, and dissolve
    loaded = False
    while loaded == False:
        input_path = user_input("\nPath to the water courses line file: ")
        try:
            watercourses_path = os.path.join(*Path(input_path).parts)
            print("\nReading file...", end="")
            watercourses_gdf = gpd.read_file(watercourses_path)
            watercourses_gdf = watercourses_gdf[["geometry"]].dissolve()
            print("Water courses line file loaded successfully.")
            loaded = True
        except:
            print("Error: Water courses line file not loaded successfully.\n")
            print("Please enter a path to a valid file or enter 'q' or 'quit' to quit.")

    # Read the multispectral watershed imagery file
    loaded = False
    while loaded == False:
        input_path = user_input("\nPath to the multispectral imagery file: ")
        try:
            imagery_path = os.path.join(*Path(input_path).parts)
            print("\nReading file...", end="")
            imagery_da = rxr.open_rasterio(filename=imagery_path)
            imagery_crs = imagery_da.rio.crs
            if imagery_crs != None:
                print("Multispectral imagery file loaded successfully.")
                loaded = True
            else:
                print("Error: Unable to determine coordinate reference system.\n")
                print("The imagery file must have a valid CRS.")

                raise Exception
        except:
            print("\nError: Multispectral imagery file not loaded successfully.\n")
            print("Please enter a path to a valid file or enter 'q' or 'quit' to quit.")

    # Input the buffer width
    loaded = False
    while loaded == False:
        buffer_width = user_input("\nRiparian buffer width in meters: ")
        try:
            buffer_width = float(buffer_width)
            if buffer_width > 0:
                loaded = True
            else:
                raise Exception
        except:
            print("\nError: Buffer width must be a valid integer or float > 0\n")

    # Return the results as a dictionary
    data_dict = {
        "watershed_name": watershed_name,
        "watershed": watershed_gdf,
        "waterbodies": waterbodies_gdf,
        "watercourses": watercourses_gdf,
        "imagery": imagery_da,
        "imagery_crs": imagery_crs,
        "buffer_width": buffer_width,
    }

    print("\nAll data loaded successfully\n")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    """
    warnings.filterwarnings("ignore", category=FutureWarning)

    print("Exporting intermediate data...", end="")
    data_dict["watershed"].to_file(
        filename="intermediate_outputs.gpkg", layer="1_watershed_input", driver="GPKG"
    )

    data_dict["waterbodies"].to_file(
        filename="intermediate_outputs.gpkg", layer="1_waterbodies", driver="GPKG"
    )

    data_dict["watercourses"].to_file(
        filename="intermediate_outputs.gpkg", layer="1_watercourses", driver="GPKG"
    )

    # data_dict["imagery"].rio.to_raster(raster_path="1_imagery.tiff")

    with open("1_imagery_crs.txt", "w") as crs_file:
        crs_file.write(str(imagery_crs))

    with open("1_buffer_width.txt", "w") as buffer_width_file:
        buffer_width_file.write(str(buffer_width))

    print("done")
    # ---------------------------------------------------------------------
    """
    return data_dict


# %% 2) Function to perform vector operations to create riparian zone - Ben


def vector_operations(data_dict):

    """
    Perform vector operations to create a waterbodies and watercourses buffer.

    Parameters
    ----------
    data_dict : Data Dictionary
        A 'dictionary' or 'list' of data objects assigned to a variable name.
        Ex. watershed_gdf = data_dict["watershed"].

    gdf : GeoDataFrame (pandas)
        A GeoDataFrame that contains a GeoSeries that stores geometry.

    geom : Geometry type
        Examples: POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON,
        GEOMETRYCOLLECTION, GEOMETRY.

    crs : Coordinate Reference System
        This instance: CRS of the raster imagery that will be used for the whole project.

    Buffer_width: Integer
        Specified buffer distance from user input.

    Returns
    -------
    riparian_buff_geom : Geometry type
        A geometry type that contains the waterbody and watercourses buffer.
    """

    print("\nCreating riparian buffer...", end="")
    watershed_gdf = data_dict["watershed"]
    waterbodies_gdf = data_dict["waterbodies"]
    watercourses_gdf = data_dict["watercourses"]
    imagery_crs = data_dict["imagery_crs"]
    buffer_width = data_dict["buffer_width"]

    # Reproject the GeoDataFrames
    watershed_gdf = watershed_gdf.to_crs(imagery_crs)
    waterbodies_gdf = waterbodies_gdf.to_crs(imagery_crs)
    watercourses_gdf = watercourses_gdf.to_crs(imagery_crs)

    # Access the dissolved geometries
    watershed_geom = watershed_gdf["geometry"]
    waterbodies_geom = waterbodies_gdf["geometry"]
    watercourses_geom = watercourses_gdf["geometry"]

    # Create water bodies and water courses buffer geometry
    waterbodies_buff_geom = waterbodies_geom.buffer(buffer_width)
    watercourses_buff_geom = watercourses_geom.buffer(buffer_width)

    # Perform union between the water bodies and water courses buffer geometry
    water_buff_geom = waterbodies_buff_geom.union(other=watercourses_buff_geom)

    # Clip to watershed boundary
    water_buff_geom = water_buff_geom.clip(mask=watershed_geom)

    # Get difference of buffered water bodies and water bodies to get the outer buffer
    riparian_buff_geom = water_buff_geom.difference(waterbodies_geom)

    print("done\n")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    # Create new GeoDataFrame containing the difference of the geometries
    # NOTE: This GeoDataFrame is just for plotting and saving the intermediate results
    riparian_buff_gdf = gpd.GeoDataFrame(geometry=riparian_buff_geom)
    riparian_buff_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="1_riparian_buff", driver="GPKG"
    )
    print("done\n")
    # ---------------------------------------------------------------------

    return riparian_buff_geom


# %% 3) Function to perform NDVI image processing - Haley


def create_ndvi(imagery_da, riparian_buff_geom):
    """will create an ndvi image
    Inputs
    ------------
    1. sentinel2_da = Sentinel-2 DataArray
    2. riparian_buff_geom = Riparian Buffer geometry GeoSeries created in previous section.
    3. red_da = red band selected from riparian_buff_da
    4. nir_da = NIR band selected from riparian_beff_da

    Outputs / Returns
    ----------
    ndvi_da = Riparian Buffer NDVI DataArray

    """

    print("\nCalculating NDVI of the riparian buffer...")
    # Set the nodata value to be nan
    imagery_da.attrs["_FillValue"] = np.nan

    # Clip the DataArray
    riparian_buff_da = imagery_da.rio.clip(geometries=riparian_buff_geom.geometry)

    # Select the Red band and keep only its long name attribute
    red_da = riparian_buff_da.sel(band=4)
    red_da.attrs["long_name"] = red_da.attrs["long_name"][3]

    # Select the NIR band and keep only its long name attribute
    nir_da = riparian_buff_da.sel(band=8)
    nir_da.attrs["long_name"] = nir_da.attrs["long_name"][7]

    # Calculate NDVI
    ndvi_da = (nir_da - red_da) / (nir_da + red_da)
    ndvi_da.attrs["long_name"] = "NDVI (Normalized Difference Vegetation Index)"

    print("done\n")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    ndvi_da.rio.to_raster("3_riparian_buff_NDVI.tiff")
    print("done\n")
    # ---------------------------------------------------------------------

    return ndvi_da


# %% 4) Function to create Riparian Vegetation DataArray - Taji


def create_binary_riparian_da(ndvi_da):
    """Create binary riparia da - docstring to be completed later"""

    # Plot riparian NDVI histogram - this is a placeholder by John until Taji can check it
    ndvi_da.plot.hist(bins=50, figsize=(10, 10))
    plt.title("Histogram of Riparian Zone NDVI Values")
    fig_path = "4_NDVI_histogram.png"
    plt.savefig("4_NDVI_histogram.png")
    fig_full_path = os.path.join(os.getcwd(), fig_path)
    print(
        "Histogram of the riparian buffer NDVI values has been saved here:"
        f"{fig_full_path}\n"
        "Please refer to it as an aid to determine an apporpriate NDVI threshold."
    )

    # Input the NDVI threshold - this is a placeholder by John until Taji can check it
    loaded = False
    while loaded == False:
        threshold = user_input("\nPlease enter the NDVI threshold: ")
        try:
            threshold = float(threshold)
            if threshold > 0 and threshold < 1:
                print("\nNDVI threshold loaded successfully.\n")
                loaded = True
            else:
                raise Exception
        except:
            print("\nError: NDVI threshold must be a decimal number between 0 and 1")

    # Specify a threshold and create a binary riparian vegetation DataArray
    # ------------------------------------------------------------------------

    print("Creating a binary riparian vegetation DataArray...", end="")
    # Boolean vegetation DataArray
    veg_da = ndvi_da > threshold

    # Binary vegetation DataArray
    veg_da = veg_da.astype("uint8")

    # Boolean not-vegetation DataArray
    not_veg_da = ndvi_da < threshold

    # Binary not-vegetation DataArray
    not_veg_da = not_veg_da.astype("uint8")

    # Create a riparian vegetation/not vegeation DataArray
    riparian_da = veg_da - not_veg_da

    print("done\n")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    riparian_da.rio.to_raster("4_riparian_da.tiff")
    print("done\n")
    # --------------------------------------------------------------------
    return riparian_da


# %% 5) Function to convert Riparian Vegetation DataArray to GeoDataFrame - John


def extract_raster_features(da, n_jobs=-1):
    """
    Convert a RioXarray DataArray to a GeoPandas GeoDataFrame.

    Contiguous pixels of the same value are turned into polygons with a column named
    'value' which represents the values of the source pixels. The boundary of the
    polygons matches the boundary of the pixels

    Parameters
    ----------
    da : DataArray
        The RioXarray DataArray to be converted to a GeoPandas GeoDataFrame. Must
        have a valid Rasterio CRS (e.g. da.rio.crs).

    n_jobs : int, optional
        The default is -1. This will then count the number of available processes for
        multiprocessing.

    Returns
    -------
    gdf : GeoDataFrame
        A GeoDataFrame containing Shapely polygons and pixel values.
    """
    # Print initial log message
    print("Converting the riparian vegetation DataArray to a GeoDataFrame...", end="")

    def _chunk_dfs(geoms_to_chunk, n_jobs):
        chunk_size = geoms_to_chunk.shape[0] // n_jobs + 1
        for i in range(n_jobs):
            start = i * chunk_size
            yield geoms_to_chunk.iloc[start : start + chunk_size]

    def _apply_parser(df):
        return df.apply(_parse_geom)

    def _parse_geom(geom_str):
        return shape(literal_eval(geom_str))

    # CRS of the DataArray
    raster_crs = da.rio.crs

    # Convert regions to polygons
    shapes = list(features.shapes(da.values, transform=da.rio.transform()))

    # Get number of processes for multiprocessing
    if n_jobs == -1:
        n_jobs = multiprocessing.cpu_count()

    res = list(zip(*shapes))
    geoms = pd.Series(res[0], name="geometry").astype(str)
    pieces = _chunk_dfs(geoms, n_jobs)
    geoms = pd.concat(
        Parallel(n_jobs=n_jobs)(delayed(_apply_parser)(i) for i in pieces)
    )

    geoms = gpd.GeoSeries(geoms).buffer(0)  # we sometimes get self-intersecting rings
    vals = pd.Series(res[1], name="value")
    riparian_gdf = gpd.GeoDataFrame(vals, geometry=geoms, crs=raster_crs)

    # Print completed log message
    print("completed\n")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    riparian_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="6_riparian_gdf", driver="GPKG"
    )
    print("done\n")
    # ---------------------------------------------------------------------

    return riparian_gdf


# %% 6) Function to calculate Riparian Connectivity Statistics - John / team
"""
To do
-----
    1. Watershed name - where should it come from?
    2. Add watershed area
"""


def riparian_stats(watershed_name, riparian_gdf, watershed_gdf):
    """
    Generate statistics related to the riparian zones.

    Parameters
    ----------
    gdf : GeoPandas GeoDataFrame
        A GeoDataFrame containing two different types of riparian features: vegetated
        and non-vegetated. Vegetated riparian features must be designated with an
        integer value of 1 in a column named 'value'. Non-vegetated features must be
        designated with an integer value of -1 in the same column.

    Returns
    -------
    df : Pandas DataFrame
        A DataFrame with descriptive column names and associated values.
        - Column names:
            - Watershed name
            - Watershed area
            - Riparian area
            - Vegetated riparian area
            - Non-vegetated riparian area
            - Vegetated riparian coverage
            - Mean non-vegetated patch size
            - non-vegetated riparian coverage
            - n vegetated riparian features
            - n non-vegetated riparian features

        - permiter of vegetation over area of watershed
    """

    # Print initial log message
    print("Calculating riparian statistics...", end="")

    # Subset by vegetation and not-vegetation features
    veg_gdf = riparian_gdf.loc[riparian_gdf["value"] == 1]
    not_veg_gdf = riparian_gdf.loc[riparian_gdf["value"] == 255]

    # Dissolve all riparian features into unique contiguous features
    riparian_gdf = (
        riparian_gdf.loc[(riparian_gdf["value"] == 1) | (riparian_gdf["value"] == 255)]
        .dissolve()
        .explode(ignore_index=True)
    )

    # Area of features
    veg_area = veg_gdf["geometry"].area.sum() / 1_000_000
    not_veg_area = not_veg_gdf["geometry"].area.sum() / 1_000_000
    riparian_area = riparian_gdf["geometry"].area.sum() / 1_000_000
    watershed_area = watershed_gdf["geometry"].area.sum() / 1_000_000

    # Mean patch size of not-vegetation features
    not_veg_mean_size = not_veg_gdf["geometry"].area.mean() / 1_000_000

    # Perimeter of features
    veg_perimeter = veg_gdf["geometry"].length.sum() / 1000
    not_veg_perimeter = not_veg_gdf["geometry"].length.sum() / 1000
    riparian_perimeter = riparian_gdf["geometry"].length.sum() / 1000

    # Number of features
    veg_n_feature = len(veg_gdf)
    not_veg_n_feature = len(not_veg_gdf)
    riparian_n_feature = len(riparian_gdf)  # Not used yet

    # Coverage of total riparian area
    veg_coverage = veg_area / riparian_area * 100
    not_veg_coverage = not_veg_area / riparian_area * 100

    data = {
        "Watershed name": [watershed_name],
        "Watershed area (km2)": [watershed_area],
        "Riparian area (km2)": [riparian_area],
        "Vegetated riparian area (km2)": [veg_area],
        "Non-vegetated riparian area (km2)": [not_veg_area],
        "Vegetated riparian coverage (%)": [veg_coverage],
        "Mean non-vegetated patch size (km2)": [not_veg_mean_size],
        "non-vegetated riparian coverage (%)": [not_veg_coverage],
        "n vegetated riparian features": [veg_n_feature],
        "n non-vegetated riparian features": [not_veg_n_feature],
        "Perimeter of vegetation features (km)": [veg_perimeter],
        "Perimeter of not-vegetation features (km)": [not_veg_perimeter],
        "Perimeter of riparian buffer (km)": [riparian_perimeter],
    }

    df = pd.DataFrame.from_dict(data=data, orient="index")

    # Print completed log message

    print("done")

    print(df)

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    veg_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_veg_gdf", driver="GPKG"
    )
    not_veg_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_not_veg_gdf", driver="GPKG"
    )
    riparian_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_riparian_gdf", driver="GPKG"
    )

    df.to_csv("7_stats_df.csv")

    print("done\n")
    # ---------------------------------------------------------------------


# %% Riparian stats function for testing


def riparian_stats_testing(watershed_name, riparian_gdf, watershed_gdf):
    """
    FOR DEVELOPMENT ONLY

    This function is a temporary stand-in for the riparian stats function.
    The stats generated here match the full_workflow.ipynb testing notebook. This
    function is used to check if the output of this script matches the output of that
    notebook.
    """
    # Print initial log message
    print("Calculating riparian statistics...", end="")

    # Subset by vegetation and not-vegetation features
    veg_gdf = riparian_gdf.loc[riparian_gdf["value"] == 1]
    not_veg_gdf = riparian_gdf.loc[riparian_gdf["value"] == 255]

    # Dissolve all riparian features into unique contiguous features
    riparian_gdf = (
        riparian_gdf.loc[(riparian_gdf["value"] == 1) | (riparian_gdf["value"] == 255)]
        .dissolve()
        .explode(ignore_index=True)
    )

    # Sample 1 perimeters
    veg_perimeter = veg_gdf["geometry"].length.sum() / 1000
    not_veg_perimeter = not_veg_gdf["geometry"].length.sum() / 1000

    # Sample 1 areas
    veg_area = veg_gdf["geometry"].area.sum() / 1_000_000
    not_veg_area = not_veg_gdf["geometry"].area.sum() / 1_000_000

    # Sampel 1 n features
    veg_n_features = len(veg_gdf)
    not_veg_n_features = len(not_veg_gdf)

    riparian_stats_df = pd.DataFrame(
        {
            "Veg area (km2)": [veg_area],
            "Not veg area (km2)": [not_veg_area],
            "Veg perimeter (km)": [veg_perimeter],
            "Not veg perimeter (km)": [not_veg_perimeter],
            "Veg n features": [veg_n_features],
            "Not veg n features": [not_veg_n_features],
            "Not veg n features / riparian area": [
                (not_veg_n_features / (veg_area + not_veg_area))
            ],
            "Not veg perimeter / veg perimeter": [(not_veg_perimeter / veg_perimeter)],
        },
        index=["sample1"],
    )

    print("done")

    # FOR DEBUGGING ------------------------------------------------------
    # Write intermediate data to file for debugging
    print("Exporting intermediate data...", end="")
    veg_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_veg_gdf", driver="GPKG"
    )
    not_veg_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_not_veg_gdf", driver="GPKG"
    )
    riparian_gdf.to_file(
        filename="intermediate_outputs.gpkg", layer="7_riparian_gdf", driver="GPKG"
    )

    riparian_stats_df.to_csv("7_stats_df.csv")

    print("done\n")
    # ---------------------------------------------------------------------


# %% 7) Function to produce a report - John & Haley
"""
Parameters (inputs)
-------------------
    - Watershed GeoDataFrame
    - Riparian Vegetation GeoDataFrame
    - Riparian connectivity statistics DataFrame
    

Prints / Exports
----------------
    - PDF report
        - Map
            - Watershed boundary
            - Riparian Vegetation GeoDataFrame
        - Table
        - Riparian connectivity statistics DataFrame
    - Log messages
    
Returns (outputs)
-----------------
    - None

"""


# %% def main function


def main():

    # 1) Function to read the vector and raster data - John
    data_dict = load_data_ui()

    # 2) Function to perform vector operations to create riparian zone - Ben
    riparian_buff_geom = vector_operations(data_dict=data_dict)

    # 3) Function to perform NDVI image processing - Haley
    ndvi_da = create_ndvi(
        imagery_da=data_dict["imagery"], riparian_buff_geom=riparian_buff_geom
    )

    # 4) Function to create Riparian Vegetation DataArray - Taji
    riparian_da = create_binary_riparian_da(ndvi_da=ndvi_da)

    # 5) Function to convert Riparian Vegetation DataArray to GeoDataFrame - John
    riparian_gdf = extract_raster_features(riparian_da)

    # 6) Function to calculate Riparian Connectivity Statistics - Taji / John
    stats_df = riparian_stats(
        watershed_name=data_dict["watershed_name"],
        riparian_gdf=riparian_gdf,
        watershed_gdf=data_dict["watershed"],
    )
    print(stats_df)

    # 7) Function to produce a report - John & Haley
    # TBA


# %% run main function
if __name__ == "__main__":
    main()
