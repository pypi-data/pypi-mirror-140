# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 15:34:04 2022

@author: chris.kerklaan

@docs: Command line tool used for the downloads and conversion of 3Di rasters on a linux server.

"""
# First imports
import pathlib
import threedi_raster_edits as tre
import argparse

# Globals
CELLSIZE = 0.5
THREADS = 1
FIELD_NAME = None


def rextract_convert(
    vector_path: str,
    lizard_key: str,
    output_directory,
    field_name: str,
    cellsize,
    threads: int,
    friction: bool,
    infiltration: bool,
    interception: bool,
):

    # create a dict
    threedi_uuids = {
        "landuse": tre.UUID.THREEDI_LANDUSE,
        "ahn": tre.UUID.THREEDI_AHN4,
        "soil": tre.UUID.THREEDI_SOIL,
    }

    # load you vector
    vector = tre.Vector(vector_path)

    # Create a rextract object
    rextract = tre.RasterExtraction(lizard_key)

    if field_name:
        if not field_name in vector.fields:
            raise ValueError(f"Field name {field_name} not found in {vector.fields}")

    for feature in vector:

        # retrieve the correct field name
        if field_name:
            output_folder_name = feature[field_name]
        else:
            output_folder_name = f"feature_{feature.fid}"

        # check if the folder exists, create otherwise
        folder = pathlib.Path(output_directory + "/" + output_folder_name)
        folder.mkdir(parents=True, exist_ok=True)

        # do download, store locations
        threedi_downloads = {}
        for name, threedi_uuid in threedi_uuids.items():
            path = str(folder / f"{name}.tif")
            rextract.run(path, threedi_uuid, feature.geometry, cellsize=0.5, threads=1)
            threedi_downloads[name] = path

        # do conversion
        group = tre.ThreediRasterGroup(
            dem_file=threedi_downloads["ahn"],
            landuse_file=threedi_downloads["landuse"],
            soil_file=threedi_downloads["soil"],
        )

        # load table
        group.load_landuse_conversion_table()
        group.load_soil_conversion_table()

        # generate the rasters you want
        if friction:
            group.generate_friction()
            group.friction.write(str(folder / "friction.tif"))

        if infiltration:
            group.generate_infiltration()
            group.infiltration.write(str(folder / "infiltration.tif"))

        if interception:
            group.generate_interception()
            group.interception.write(str(folder / "interception.tif"))


def get_parser():
    """Return argument parser."""

    parser = argparse.ArgumentParser(description=__doc__)

    # main
    parser.add_argument("vector_path", help="Features of this vector are downloaded.")
    parser.add_argument("lizard_key", help="Lizard key.")
    parser.add_argument("output_directory", help="Output rasters are placed here.")

    # options
    parser.add_argument(
        "-f", "--friction", default=True, type=bool, help="Generates friction."
    )
    parser.add_argument(
        "-ic", "--interception", default=True, type=bool, help="Generates interception"
    )
    parser.add_argument(
        "-if", "--infiltration", default=True, type=bool, help="Generates infiltration"
    )

    parser.add_argument(
        "-fn",
        "--field_name",
        default=FIELD_NAME,
        help="Field name used to place the rasters in a directory.",
    )
    parser.add_argument(
        "-cs", "--cellsize", default=CELLSIZE, type=float, help="Cellsize."
    )
    parser.add_argument(
        "-tr",
        "--threads",
        default=THREADS,
        type=int,
        help="Amount of threads used. More threads increases speed. Cannot be above 4.",
    )

    return parser


def main():
    """Call extract_all with args from parser."""
    return rextract_convert(**vars(get_parser().parse_args()))


if __name__ == "__main__":
    exit(main())
