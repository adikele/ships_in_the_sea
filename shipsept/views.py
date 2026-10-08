#1 Oct 2026
from django.shortcuts import render
from django.http import HttpResponse
import geopandas
import folium

'''
import matplotlib   # by AI
matplotlib.use('Agg') # by AI
import matplotlib.pyplot as plt
'''
import pyproj
from shapely import Point, LineString
import shapely as shapely
import pandas as pd
#import django
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CountrySelectForm
import random
import os
#from django.conf import settings
from  .megastar_helper_bends import *

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def select_country_form(request):
    global x
    global y
    selected_route = '0'
    form = CountrySelectForm()
    if request.method == "POST":
        form = CountrySelectForm(request.POST)
        if form.is_valid():  
            df_meri = pd.read_csv('ship3.csv')
            # Get the selected value       
               #  ('ship2.csv') works fine
            df_meri ['intermediate_points'] = [Point(xy) for xy in zip(df_meri['long'], df_meri['lat'] )]
            gdf_meri = geopandas.GeoDataFrame(df_meri, geometry='intermediate_points', crs="EPSG:4326")
            print (gdf_meri.head())

            gdf_meri["next_lat"] = gdf_meri["lat"].shift(-1)
            gdf_meri["next_long"] = gdf_meri["long"].shift(-1)
            gdf_meri["current_bearing"] = gdf_meri.apply(
                    lambda row: calculate_bearing_2(
                        row.long,
                        row.lat,
                        row.next_long,
                        row.next_lat,
                    ),
                    axis=1,
                )

            gdf_meri["distance"] = gdf_meri.apply(
                    lambda row: calculate_bearing_3(
                        row.long,
                        row.lat,
                        row.next_long,
                        row.next_lat,
                    ),
                    axis=1,
                )

            selected_route  = form.cleaned_data['route']
            if selected_route == '1':
                gdf1_meri = gdf_meri[gdf_meri["ship"]=="Megastar"]  
                gdf1_meri = set_routeline_s_bend_length_new(gdf1_meri)
                print ("Star (Hel to Talinn) AFTER detection...")
                print (gdf1_meri.head())
                map_html = map_plotter (gdf1_meri)

            elif selected_route == '2':  
                gdf2_meri = gdf_meri[gdf_meri["ship"]=="Star"]           
                gdf2_meri = set_routeline_s_bend_length_new(gdf2_meri)
                print ("Star AFTER detection...")
                print (gdf2_meri.head())
                map_html = map_plotter (gdf2_meri)
            return render(request, 'shipsept/map_template.html', {'map_html': map_html})

    else:
        # this is the case when user sees the form for the first time
        form = CountrySelectForm()
    return render(request, "shipsept/select_country_form.html", {"form": form})

def map_plotter(gdf):
    gdf = geopandas.GeoDataFrame(gdf, geometry='intermediate_points', crs="EPSG:4326")
                    #gdf_meri = geopandas.GeoDataFrame(df_meri, geometry='intermediate_points', crs="EPSG:4326")
                           
    API_KEY = "cb1_44x7_1_228b1801b8ba5a23cc98c411"

    # Define the CARTO tile URL template including the key parameter
    # Styles available: voyager, positron, dark_all
    tile_url = f"https://basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}.png?key={API_KEY}"
    attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

    m = folium.Map([60.1, 24.5], zoom_start=10, tiles="cartodbpositron")

    folium.TileLayer(
        tiles=tile_url,
        attr=attribution,
        name="CARTO Voyager",
        max_zoom=20
    ).add_to(m)

    folium.GeoJson(gdf).add_to(m)

    map_html = m._repr_html_()

    return map_html 


def calculate_bearing_2(long1, lat1, long2, lat2):
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    if fwd_azimuth < 0:
        fwd_azimuth += 360
    return (fwd_azimuth)

def calculate_bearing_3(long1, lat1, long2, lat2):
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    return (distance)

