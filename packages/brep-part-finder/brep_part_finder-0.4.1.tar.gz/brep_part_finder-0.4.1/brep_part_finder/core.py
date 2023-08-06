import warnings
from collections.abc import Iterable
from typing import Tuple

import numpy as np
from cadquery import *
from cadquery.occ_impl.shapes import Shape


def get_brep_part_properties(filename: str):
    """Imports a Brep CAD file and returns the contents as a CadQuery Shape
    object

    Args:
        filename: the filename of the brep file
    """

    brep_shapes = Shape.importBrep(filename)

    my_brep_part_details = {}
    for counter, part in enumerate(brep_shapes.Solids(), 1):
        part_details = {}
        part_details["Center.x"] = part.Center().x
        part_details["Center.y"] = part.Center().y
        part_details["Center.z"] = part.Center().z

        part_details["Volume"] = part.Volume()

        part_details["BoundingBox.xmin"] = part.BoundingBox().xmin
        part_details["BoundingBox.ymin"] = part.BoundingBox().ymin
        part_details["BoundingBox.zmin"] = part.BoundingBox().zmin
        part_details["BoundingBox.xmax"] = part.BoundingBox().xmax
        part_details["BoundingBox.ymax"] = part.BoundingBox().ymax
        part_details["BoundingBox.zmax"] = part.BoundingBox().zmax

        my_brep_part_details[counter] = part_details

    return my_brep_part_details


def get_part_id(
    brep_part_properties: dict,
    volume: float = None,
    center: Tuple[float, float, float] = None,
    bounding_box: Tuple[Tuple[float, float, float], Tuple[float, float, float]] = None,
    volume_atol: float = 1e-6,
    center_atol: float = 1e-6,
    bounding_box_atol: float = 1e-6,
):
    """Finds the key within a dictionary of parts that matches the user
    specified arguments for volume, center, bounding_box within the provided
    tolerances

    Arguments:
        brep_part_properties: a dictionary with the part id number as the key
            and a dictionary of values for the part properties. For example
            {1: {'Center.x':0, 'Center.y':0, 'Center.z':0, 'Volume':10, ....}}
        volume: the volume of the part to find.
        center: a tuple of x,y,z coordinates
        bounding_box: a tuple of two coordinates where the coordinates are the
            lower left and upper right corners of the bounding box.
        volume_atol: absolute tolerance acceptable on the volume comparision
        center_atol: absolute tolerance acceptable on the center comparision
        bounding_box_atol: absolute tolerance acceptable on the bounding box comparision
    """

    part_ids_matching = {}

    if center:
        part_ids_matching_centers = []
        for key, value in brep_part_properties.items():
            if (
                np.isclose(value["Center.x"], center[0], atol=center_atol)
                and np.isclose(value["Center.y"], center[1], atol=center_atol)
                and np.isclose(value["Center.z"], center[2], atol=center_atol)
            ):
                part_ids_matching_centers.append(key)
        if len(part_ids_matching_centers) == 0:
            warnings.warn(
                "No parts matching the specified center +/- tolerances were found"
            )
        else:
            part_ids_matching["center"] = part_ids_matching_centers

    if volume:
        part_ids_matching_volume = []
        for key, value in brep_part_properties.items():
            if np.isclose(value["Volume"], volume, atol=volume_atol):
                part_ids_matching_volume.append(key)
        if len(part_ids_matching_volume) == 0:
            warnings.warn(
                "No parts matching the specified volume +/- tolerances were found"
            )
        else:
            part_ids_matching["volume"] = part_ids_matching_volume

    if bounding_box:
        part_ids_matching_bounding_box = []
        for key, value in brep_part_properties.items():
            part_bb = (
                value["BoundingBox.xmin"],
                value["BoundingBox.ymin"],
                value["BoundingBox.zmin"],
            ), (
                value["BoundingBox.xmax"],
                value["BoundingBox.ymax"],
                value["BoundingBox.zmax"],
            )
            if (
                np.isclose(part_bb[0][0], bounding_box[0][0], atol=bounding_box_atol)
                and np.isclose(
                    part_bb[0][1], bounding_box[0][1], atol=bounding_box_atol
                )
                and np.isclose(
                    part_bb[0][2], bounding_box[0][2], atol=bounding_box_atol
                )
                and np.isclose(
                    part_bb[1][0], bounding_box[1][0], atol=bounding_box_atol
                )
                and np.isclose(
                    part_bb[1][1], bounding_box[1][1], atol=bounding_box_atol
                )
                and np.isclose(
                    part_bb[1][2], bounding_box[1][2], atol=bounding_box_atol
                )
            ):
                # print('match',key,bounding_box,part_bb)
                part_ids_matching_bounding_box.append(key)
        if len(part_ids_matching_bounding_box) == 0:
            warnings.warn("No parts matching the specified bounding boxes were found")
        else:
            part_ids_matching["bounding_box"] = part_ids_matching_bounding_box

    # print("volume numbers matching search criteria", part_ids_matching)

    lists_of_matching_parts_separate = list(part_ids_matching.values())

    if lists_of_matching_parts_separate == []:
        warnings.warn("No single part found that matches all criteria")
        print("search criteria are:")
        print(" volume", volume)
        print(" center", center)
        print(" bounding_box", bounding_box)
        print(" volume_atol", volume_atol)
        print(" center_atol", center_atol)
        print(" bounding_box_atol", bounding_box_atol)

    lists_of_matching_parts = list(
        set.intersection(*map(set, lists_of_matching_parts_separate))
    )

    if len(lists_of_matching_parts) == 0:
        warnings.warn("No single part found that matches all criteria")

    return lists_of_matching_parts


def get_part_ids(
    brep_part_properties,
    shape_properties: dict,
    volume_atol: float = 1e-6,
    center_atol: float = 1e-6,
    bounding_box_atol: float = 1e-6,
):
    key_and_part_id = []
    for key, value in shape_properties.items():
        matching_part_id = get_part_id(
            brep_part_properties=brep_part_properties,
            volume_atol=volume_atol,
            center_atol=center_atol,
            bounding_box_atol=bounding_box_atol,
            **value,
        )
        key_and_part_id.append((key, matching_part_id))
    return key_and_part_id


def get_dict_of_part_ids(
    brep_part_properties,
    shape_properties: dict,
    volume_atol: float = 1e-6,
    center_atol: float = 1e-6,
    bounding_box_atol: float = 1e-6,
):
    key_and_part_id = {}
    for key, value in shape_properties.items():

        if isinstance(value, dict):
            # check if value is a list of dictionaries or a dictionary
            matching_part_id = get_part_id(
                brep_part_properties=brep_part_properties,
                volume_atol=volume_atol,
                center_atol=center_atol,
                bounding_box_atol=bounding_box_atol,
                **value,
            )
            if len(matching_part_id) > 1:
                raise ValueError(f"multiple matching volumes were found for {key}")
            # todo check that key is not already in use
            key_and_part_id[matching_part_id[0]] = key
        elif isinstance(value, Iterable):
            # assumed to be list
            for entry in value:
                # check if value is a list of dictionaries or a dictionary
                matching_part_id = get_part_id(
                    brep_part_properties=brep_part_properties,
                    volume_atol=volume_atol,
                    center_atol=center_atol,
                    bounding_box_atol=bounding_box_atol,
                    **entry,
                )
                if len(matching_part_id) > 1:
                    raise ValueError(f"multiple matching volumes were found for {key}")
                # todo check that key is not already in use
                key_and_part_id[matching_part_id[0]] = key
        else:
            msg = "dictionary values must be either a dictionary or a list of dictionaries"
            raise ValueError(msg)
    return key_and_part_id
