from django.shortcuts import render
from django.http import JsonResponse
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import Button
from .app import Silvia as app
import pandas as pd
from requests import Request
import geopandas as gpd
from .model import FloodExtent
from sqlalchemy.orm import sessionmaker
from rest_framework.decorators import api_view,authentication_classes, permission_classes
import json
Persistent_Store_Name = 'flooded_addresses'
@login_required()
def home(request):
    """
    Controller for the app home page.
    """


    context = {

    }

    return render(request, 'silvia/home.html', context)

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

@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def floodDates(request):

    csv_file = app.get_custom_setting('flood_info')
    df = pd.read_csv(csv_file)
    list_dates = df["date"].values.tolist()
    list_dates = list_dates[::-1]
    return JsonResponse({"dates":list_dates})
