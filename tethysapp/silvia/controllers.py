from django.shortcuts import render
from django.http import JsonResponse
from tethys_sdk.permissions import login_required
from tethys_sdk.routing import controller
from .app import Silvia as app
import pandas as pd
from requests import Request
import geopandas as gpd
from .model import FloodExtent
from sqlalchemy.orm import sessionmaker
from rest_framework.decorators import api_view,authentication_classes, permission_classes
import json
import os
Persistent_Store_Name = 'flooded_addresses'

@controller(name='home',url='silvia')
def home(request):
    """
    Controller for the app home page.
    """


    context = {

    }

    return render(request, 'silvia/home.html', context)

@controller(name='floods',url='silvia/floods')
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def floodAtributes(request):
    geojson_flood_extent = {}
    date_to_ask = request.data.get('date')
    if(date_to_ask is not ''):

        SessionMaker = app.get_persistent_store_database(Persistent_Store_Name, as_sessionmaker=True)
        session = SessionMaker()

        # flood_extents = session.query(FloodExtent.geom.ST_AsGeoJSON(), FloodExtent.comid).all()

        # print(flood_extents)
        # print("here",date_to_ask)
        csv_file = app.get_custom_setting('flood_info')
        df = pd.read_csv(csv_file)
        sum_df = pd.DataFrame()
        sum_df['date'] = df['date']
        cols = df.columns.to_numpy()

        sum_df["4"] = [cols[x].tolist() for x in df.eq(4).to_numpy()]
        sum_df["3"] = [cols[x].tolist() for x in df.eq(3).to_numpy()]
        sum_df["2"] = [cols[x].tolist() for x in df.eq(2).to_numpy()]
        sum_df["1"] = [cols[x].tolist() for x in df.eq(1).to_numpy()]

        loc_date = sum_df.loc[sum_df['date'] == date_to_ask]
        # print(loc_date["3"].values.tolist())
        
        # sum_df = sum_df.set_index('date')
        # response_obj = sum_df.to_dict('index')

        # list_1 = loc_date["1"].values.tolist()[0]
        list_4 = []
        list_3 = []
        list_2 = []

        if(len(loc_date["4"].values.tolist()) > 0):
            list_4 = loc_date["4"].values.tolist()[0]
        if(len(loc_date["3"].values.tolist()) > 0):
            list_3 = loc_date["3"].values.tolist()[0]
        if(len(loc_date["2"].values.tolist()) > 0):
            list_2 = loc_date["2"].values.tolist()[0]

        flood_events_comids = list_2 +list_3 +list_4

        only_events= session.query(FloodExtent).filter(FloodExtent.comid.in_(flood_events_comids)).all()
        
        for only_event in only_events:
            # print(only_event.comid)
            if(str(only_event.comid)in list_2):
                only_event.flood = 2
            if(str(only_event.comid) in list_3):
                only_event.flood = 3
            if(str(only_event.comid) in list_4):
                only_event.flood = 4
            session.commit()
        only_events_features= session.query(FloodExtent.geom.ST_AsGeoJSON(), FloodExtent.comid, FloodExtent.flood).filter(FloodExtent.comid.in_(flood_events_comids)).all()
        # print(only_events_features)
        session.close()
        features = []
        for only_events_feature in only_events_features:
            flood_extent_feature = {
                'type': 'Feature',
                'geometry': json.loads(only_events_feature[0]),
                # 'geometry': len(only_events_feature[0]),
                'properties':{
                    'flood': only_events_feature[2],
                    'comid':only_events_feature[1]
                }

            }
            features.append(flood_extent_feature)

        geojson_flood_extent = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': features
        }
        # print(geojson_flood_extent)
    else:
        geojson_flood_extent = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': []
        }
    
    return JsonResponse(geojson_flood_extent)

@controller(name='dates',url='silvia/dates')
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def floodDates(request):

    csv_file = app.get_custom_setting('flood_info')
    df = pd.read_csv(csv_file)
    list_dates = df["date"].values.tolist()
    list_dates = list_dates[::-1]
    return JsonResponse({"dates":list_dates})


@controller(name='departments',url='silvia/departments', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getDepartaments(request, app_workspace):
    
    aw_path = app_workspace.path
        # Select Region
    region_index = json.load(open(os.path.join(aw_path, 'geojson', 'index.json')))
    dp=[region_index[opt]['name'] for opt in region_index]
    return JsonResponse({"departments":dp})

@controller(name='departments-json',url='silvia/departments-json', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getDepartmentJson(request,app_workspace):
    print(request.data.get('department'))
    if request.data.get('department') != "Peru":
        print("hey")
        department = request.data.get('department').upper().replace(" ","_")
    else:
        print("asfgasg")
        department =request.data.get('department')
    print(department)
    aw_path = app_workspace.path
    try:
        region_json = json.load(open(os.path.join(aw_path, 'geojson', f'{department}.json')))
    except:
        region_json = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': []
        }
    
    return JsonResponse(region_json)


@controller(name='provincias',url='silvia/provincias', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getProvinces(request, app_workspace):
    
    aw_path = app_workspace.path
        # Select Region
    region_index = json.load(open(os.path.join(aw_path, 'geojson2', 'index2.json')))
    dp=[region_index[opt]['name'] for opt in region_index]
    return JsonResponse({"provinces":dp})

@controller(name='provincias-json',url='silvia/provincias-json', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getProvincesJson(request,app_workspace):
    print(request.data.get('provincia'))
    if request.data.get('provincia') != "Peru":
        province = request.data.get('provincia').upper().replace(" ","_")
    else:
        province =request.data.get('provincia')
    print(province)
    aw_path = app_workspace.path
    try:
        region_json = json.load(open(os.path.join(aw_path, 'geojson2', f'{province}.json')))
    except:
        region_json = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': []
        }
    
    return JsonResponse(region_json)


@controller(name='basins',url='silvia/basins', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getBasins(request, app_workspace):
    
    aw_path = app_workspace.path
        # Select Region
    region_index = json.load(open(os.path.join(aw_path, 'geojson3', 'index3.json')))
    dp=[region_index[opt]['name'] for opt in region_index]
    return JsonResponse({"basin":dp})

@controller(name='basin-json',url='silvia/basin-json', app_workspace=True)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def getBasinsJson(request,app_workspace):
    print(request.data.get('basin'))
    if request.data.get('basin') != "Peru":
        basin = request.data.get('basin').replace(" ","_")
    else:
        basin =request.data.get('basin')
    print(basin)
    aw_path = app_workspace.path
    try:
        region_json = json.load(open(os.path.join(aw_path, 'geojson3', f'{basin}.json')))
    except:
        region_json = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': []
        }
    
    return JsonResponse(region_json)