"""_summary_
contains two functions:
(i) set_routeline_s_bend_length_new: finds s-bends and the distance of the line segments of the middle part of the s-bends
(ii) set_routeline_u_bend_length_new: finds u-bends and the distance of the line segments of the middle part of the u-bends
Both these functions use the SAME common functions:
a) find_short_bend
b) find_extended_bend 
"""
import logging
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
#from geopy.point import Point as gPoint  # removing

from shapely.geometry.point import Point
from shapely.geometry.linestring import LineString


def find_short_bend(
            df: gpd.GeoDataFrame, 
            column_name_turn_pattern_1_current: str, 
            column_name_turn_pattern_1_next: str, 
            column_name_turn_pattern_2_current: str, 
            column_name_turn_pattern_2_next: str, 
            column_bend_distance:  str # tried changing --> float # changed 
    )-> gpd.GeoDataFrame:
    """Finds short bends (s-bends and u-bends) in a dataframe.
        Depending on the arguments supplied to the function:
        (i) it detects either s-bends OR u-bends
        (not both in one passing of the function)
        (ii) it calculates the length of the middle portion of the bend
        Passed dataframe needs to have "length" named column.
        Args:
            gdf_nav (gpd.GeoDataFrame): Dataframe containing at least current bearing in degrees.
            column_name_turn_pattern_1_current: string, the column with that name in the df evaluates whether turn is a specified direction
            column_name_turn_pattern_1_next: string
            column_name_turn_pattern_2_current: string
            column_name_turn_pattern_2_next: string
            column_bend_distance: string, name of column existing in the dataframe, will be assigned the value of distance of middle part of a bend
        Returns:
            gdf_nav (gpd.GeoDataFrame): Dataframe containing Bool column "is_middle_of_shortbend"
    """
    df["is_middle_of_shortbend"] = (df[column_name_turn_pattern_1_current] & df[column_name_turn_pattern_1_next]) | (
        df[column_name_turn_pattern_2_current] & df[column_name_turn_pattern_2_next])

    print ("column_bend_distance")
    print (column_bend_distance)
    #df['S_BEND'] = df['S_BEND'].astype(float)
    # for the short s-bends, where the linestring is located, need to give that df also the "length"
    for index, row in df.iterrows():
        if row["is_middle_of_shortbend"]:
            #df.at[index, column_bend_distance] = row["length"]  # changing 19.11.2024
            # BeFra.iloc[0]['geometry']
            print (df.iloc[index]['S_BEND'])
            df.at[index, column_bend_distance] = row["distance"]
    return df

def find_extended_bend(
            df: gpd.GeoDataFrame, 
            column_name_turn_pattern_current: str, 
            direction_end_of_ls: str, 
            direction_invalid_end_of_ls: str, 
            column_sum_bend_portion: str # float  # str
    )-> gpd.GeoDataFrame:
    """ Finds extended bends (s-bends and u-bends) in a dataframe.
        Depending on the arguments supplied to the function:
        (i) it detects either s-bends OR u-bends
        (not both in one passing of the function)
        (ii) it calculates the length of the middle portion of the bend
        Passed dataframe needs to have "length", "direction" amd "direction_next" named columns.
    Args:
        gdf_nav (gpd.GeoDataFrame): Dataframe.
        column_name_turn_pattern_current: string, the column with that name in the df evaluates whether turn is a specified direction
        direction_end_of_ls: string, direction of the end of linestring of a valid bend
        direction_invalid_end_of_ls: string, direction of the end of linesstring of an invalid bend
        column_sum_bend_portion: string, name of column to be assigned to the dataframe for sum of values of middle part of a bend
        Returns:
        gdf_nav (gpd.GeoDataFrame): Dataframe containing:
        (i) Bool column: "is_middle_of_bend", True or False
        (ii) float column with name column_sum_bend_portion: sum of values of middle part of a bend
    """
    for index, row in df.iterrows():
        sum_lengths = 0
        # with this check we have established that we have detected either:
        # (i) a sbend: an extended  right - str - left sbend  or an extended left - str - right sbend
        # OR
        # (ii) an ubend: an extended right - str - right ubend or an extended left - str - left ubend
        if row[column_name_turn_pattern_current] and row["direction_next"] == "straight":
            # sum_lengths --> add the length of the starting linestring of the "middle s-bend" linestrings
            sum_lengths = row["length"]
            starting_row_number = index
            for i in range(index, df.shape[0] - starting_row_number):
                # start checking from the next linestring to end of frame
                # (index, n) where n = number of rows from index position to end of frame.
                # the length for the current index number row is being calculated in the previous iteration
                if (df.iloc[index+i])["direction"] == "straight":  # checking if the linestring is straight
                    sum_lengths = sum_lengths + df.iloc[index+i]["length"]
                elif df.iloc[index+i]["direction"] == direction_end_of_ls:  # do nothing with the next linestring
                    end_of_linestring = i  # row number i is the last of the straight lines
                    for j in range(starting_row_number, end_of_linestring + 1):
                        df.at[j, column_sum_bend_portion] = sum_lengths
                        df.at[j, "is_middle_of_bend"] = True
                    break
                elif df.iloc[index+i]["direction"] == direction_invalid_end_of_ls:  # do nothing with the next current linestring
                    df.at[i, 'is_middle_of_bend'] = False
                    break
    return df

#@time_logging.time_logger
def set_routeline_s_bend_length_new(
    gdf_nav: gpd.GeoDataFrame,
    turn_angle_threshold: int = 5,
) -> gpd.GeoDataFrame:
    """Sets s-bend masks per row in a dataframe. Passed dataframe needs to have "suunta_current" named column.
        Args:
            gdf_nav (gpd.GeoDataFrame): Dataframe containing at least current bearing in degrees.
            turn_angle_threshold (int, optional): Threshold to exclude too small turns as they have virtually no effect on ships. Defaults to 5.
        Raises:
            ValueError: If required columns are missing.
        Returns:
            gpd.GeoDataFrame: Dataframe with added columns [index_next, bearing_next, is_right_next, is_right_following_next, is_s_bend_sequence_start, is_s_bend_middle_line]
    """
    # necessary_columns = ["intermediate_points", "current_bearing", "sade"]
    necessary_columns = ["intermediate_points"]
    if not all(col in gdf_nav.columns for col in necessary_columns):
        '''
        logger.error("Not all necessary columns were found.")
        logger.error(
            "Dataframe has columns %s, but columns %s were required.",
            gdf_nav.columns,
            necessary_columns,
        )
        '''
        raise ValueError("Not all required columns were found")
    # Don"t modfidy input df but take a copy of it instead, reset index and set
    gdf_nav = gdf_nav.copy()
    gdf_nav = gdf_nav.reset_index()

    # Save original index to a column, name it GDO_GID as frontend diagram uses it in x-axis.
    gdf_nav["GDO_GID"] = gdf_nav.index
    #print("gdf_nav input\n", gdf_nav)

    #temp = gdf_nav.loc[gdf_nav["sade"].isna(), necessary_columns + ["GDO_GID"]]

    temp = gdf_nav 
    # above lines from Juha's s-mask progm
    temp["bearing_diff_prev"] = temp["current_bearing"].diff().fillna(0)

    temp["is_right_turn"] = (temp["bearing_diff_prev"].abs() > turn_angle_threshold) & (temp["bearing_diff_prev"] > 0.0)
    temp["is_left_turn"] = (temp["bearing_diff_prev"].abs() > turn_angle_threshold) & (temp["bearing_diff_prev"] < 0.0)

    list_direction = []
    temp["direction"] = ""

    temp["length"] = temp.apply(
        lambda row: row.intermediate_points.length, axis=1)

    temp["S_BEND"] = ""  # 19.11.2024  S_BEND will contain the total "middle" distance of the s-bend
    #df["col"] = df["col"].fillna(0.0). # 
    #temp['S_BEND'] = temp['S_BEND'].fillna(0.0)
    #df['column_name'] = 0.0
    temp['S_BEND'] = 0.0
    #temp['S_BEND'] = temp['S_BEND'].astype(float) # new

    # START DIR fill ["direction"] column of df
    for index, row in temp.iterrows():
        if row["is_right_turn"]:
            list_direction.append("right")
        elif row["is_left_turn"]:
            list_direction.append("left")
        else:
            list_direction.append("straight")

    temp["direction"] = list_direction
    # END DIR

    temp["is_right_turn_next"] = temp["is_right_turn"].shift(-1)
    temp["is_left_turn_next"] = temp["is_left_turn"].shift(-1)

    temp["direction_next"] = temp["direction"].shift(-1)

    #print("gdf_nav before finding short bends \n", temp)
    
    # checking for right-left and left-right
    df_after_find_short_bends = find_short_bend(df=temp, column_name_turn_pattern_1_current="is_right_turn", column_name_turn_pattern_1_next="is_left_turn_next",
                                                column_name_turn_pattern_2_current="is_left_turn", column_name_turn_pattern_2_next="is_right_turn_next", column_bend_distance="S_BEND")

    # for finding extended right-starting s-bends (right - straight - left)
    df_result1_ext_sbend = find_extended_bend(df=df_after_find_short_bends, column_name_turn_pattern_current="is_right_turn",
                                              direction_end_of_ls="left", direction_invalid_end_of_ls="right", column_sum_bend_portion="S_BEND")

    # for finding extended left-starting s-bends (left - straight - right)
    df_result2_ext_sbend = find_extended_bend(df=df_result1_ext_sbend, column_name_turn_pattern_current="is_left_turn",
                                              direction_end_of_ls="right", direction_invalid_end_of_ls="left", column_sum_bend_portion="S_BEND")

    # let us combine the "is_middle_bend" True values:
    if 'is_middle_of_bend' in df_result2_ext_sbend and 'is_middle_of_shortbend' in df_result2_ext_sbend:
        df_result2_ext_sbend["is_s_bend_middle_line"] = df_result2_ext_sbend[[
            'is_middle_of_bend', 'is_middle_of_shortbend']].any(axis='columns')

    pd.set_option('max_colwidth', None)
    pd.set_option('display.max_columns', None)

    # For some reason merged result is converted to plain df so convert it back to gdf
    # logger.info("df_result2_ext_sbend mergen jälkeen %s, %s", df_result2_ext_sbend.columns, type(df_result2_ext_sbend))
    df_result2_ext_sbend = gpd.GeoDataFrame(df_result2_ext_sbend, geometry="intermediate_points", crs="EPSG:3067")

    return df_result2_ext_sbend


#@time_logging.time_logger
def set_routeline_u_bend_length_new(
    gdf_nav: gpd.GeoDataFrame,
    turn_angle_threshold: int = 5,
) -> gpd.GeoDataFrame:
    """Sets u-bend masks per row in a dataframe. Passed dataframe needs to have "suunta_current" named column.
        Args:
            gdf_nav (gpd.GeoDataFrame): Dataframe containing at least current bearing in degrees.
            turn_angle_threshold (int, optional): Threshold to exclude too small turns as they have virtually no effect on ships. Defaults to 5.
        Raises:
            ValueError: If required columns are missing.
        Returns:
            gpd.GeoDataFrame: Dataframe with added columns [index_next, bearing_next, is_right_next, is_right_following_next, is_s_bend_sequence_start, is_s_bend_middle_line]
    """

    necessary_columns = ["intermediate_points", "current_bearing", "sade"]
    if not all(col in gdf_nav.columns for col in necessary_columns):
        '''
        logger.error("Not all necessary columns were found.")
        logger.error(
            "Dataframe has columns %s, but columns %s were required.",
            gdf_nav.columns,
            necessary_columns,
        )
        '''
        raise ValueError("Not all required columns were found")
    # Don"t modfidy input df but take a copy of it instead, reset index and set
    gdf_nav = gdf_nav.copy()
    gdf_nav = gdf_nav.reset_index()

    # Save original index to a column, name it GDO_GID as frontend diagram uses it in x-axis.
    gdf_nav["GDO_GID"] = gdf_nav.index
    print("gdf_nav input\n", gdf_nav)

    temp = gdf_nav.loc[gdf_nav["sade"].isna(), necessary_columns + ["GDO_GID"]]

    # above lines from Juha's s-mask progm
    temp["bearing_diff_prev"] = temp["current_bearing"].diff().fillna(0)

    temp["is_right_turn"] = (temp["bearing_diff_prev"].abs() > turn_angle_threshold) & (temp["bearing_diff_prev"] > 0.0)
    temp["is_left_turn"] = (temp["bearing_diff_prev"].abs() > turn_angle_threshold) & (temp["bearing_diff_prev"] < 0.0)

    list_direction = []
    temp["direction"] = ""

    temp["length"] = temp.apply(
        lambda row: row.intermediate_points.length, axis=1)

    temp["U_BEND"] = ""  # u-bend middle part distance total

    # START DIR fill ["direction"] column of temp
    for index, row in temp.iterrows():
        if row["is_right_turn"]:
            list_direction.append("right")
        elif row["is_left_turn"]:
            list_direction.append("left")
        else:
            list_direction.append("straight")

    temp["direction"] = list_direction
    # END DIR

    temp["is_right_turn_next"] = temp["is_right_turn"].shift(-1)
    temp["is_left_turn_next"] = temp["is_left_turn"].shift(-1)
    temp["direction_next"] = temp["direction"].shift(-1)

    # checking for right-left and left-right
    df_after_find_short_bends = find_short_bend(df=temp, column_name_turn_pattern_1_current="is_right_turn", column_name_turn_pattern_1_next="is_right_turn_next",
                                                column_name_turn_pattern_2_current="is_left_turn", column_name_turn_pattern_2_next="is_left_turn_next", column_bend_distance="U_BEND")

    # for finding extended right-starting u-bends (right - straight - right)
    df_result1_ext_ubend = find_extended_bend(df=df_after_find_short_bends, column_name_turn_pattern_current="is_right_turn",
                                              direction_end_of_ls="right", direction_invalid_end_of_ls="left", column_sum_bend_portion="U_BEND")

    # for finding extended left-starting u-bends (left - straight - left)
    df_result2_ext_ubend = find_extended_bend(df=df_result1_ext_ubend, column_name_turn_pattern_current="is_left_turn",
                                              direction_end_of_ls="left", direction_invalid_end_of_ls="right", column_sum_bend_portion="U_BEND")


    if 'is_middle_of_bend' in df_result2_ext_ubend and 'is_middle_of_shortbend' in df_result2_ext_ubend:
        df_result2_ext_ubend["is_u_bend_middle_line"] = df_result2_ext_ubend[[
            'is_middle_of_bend', 'is_middle_of_shortbend']].any(axis='columns')

    pd.set_option('max_colwidth', None)
    pd.set_option('display.max_columns', None)

    
    # For some reason merged result is converted to plain df so convert it back to gdf
    #logger.info("df_result2_ext_ubend mergen jälkeen %s, %s", df_result2_ext_ubend.columns, type(df_result2_ext_ubend))
    df_result2_ext_ubend = gpd.GeoDataFrame(df_result2_ext_ubend, geometry="intermediate_points", crs="EPSG:3067")

    return df_result2_ext_ubend