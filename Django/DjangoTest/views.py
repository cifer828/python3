# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
import json
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import re
import photo_geo as pg
import base64
import os
# Create your views here.
from django.http import HttpResponse, JsonResponse

# filename = 'test.jpg'
@csrf_exempt  #avoid CSRF problem
def index(request):
    """
    response to js
    """
    # response to onload request
    # request: none
    # response: main page
    if request.body == '':
          return render(request, 'click_map.html')

    # response to uoloadImage() request,
    # request json: {'name': filename, 'imgData': base64}
    # response json: {'GPSInfo': YES/No, 'lng': longitude, 'lat': latitude}=}
    elif len(request.body) > 100:
        retrieveData = json.loads(request.body)
        imgData = retrieveData['imgData']
        # decode base64 to jpg without heading
        imgData_b64 = base64.b64decode(re.findall(',(.*)',imgData)[0])
        filename = retrieveData['name'][0]
        # write to file
        with open('photos/' + filename, 'wb') as f:
            f.write(imgData_b64)
        GPSinfo = pg.check_location('photos/' + filename)
        if GPSinfo != (0, 0):
             gps_dict = {'GPSInfo': 'YES', 'lng': GPSinfo[0], 'lat': GPSinfo[1]}
        else:
             gps_dict = {'GPSInfo': 'No', 'lng': 0, 'lat': 0}
        # post json to js
        return HttpResponse(json.dumps(gps_dict),  content_type="application/json")

    # response to displayOnMap() request
    # request string: photo name
    # response json: {'base64':base64, 'lng': longitude, 'lat': 'latitude'}
    elif request.body[:3] == '{"f':
        retrieveData = json.loads(request.body)
        filename = retrieveData['filename']
        # with open( 'test.txt','w') as f:
        #     f.write(ph2base64(filename))
        GPSInfo = pg.check_location('photos/' + filename)
        gpsDicts = {'base64': ph2base64('photos/' + filename), 'lng': GPSInfo[0], 'lat': GPSInfo[1]}
        if GPSInfo != (0, 0):
             gpsDicts['GPSInfo'] = 'YES'
        else:
             gpsDicts['GPSInfo'] = 'NO'
        return HttpResponse(json.dumps(gpsDicts),  content_type="application/json")
        # cannot use json unknown reason
        # json_receive = json.loads(request.body)
        # lat = json_receive['lat']
        # lng = json_receive['lng']

    # response to submitgps()request
    # request json: {filename, lng, lat}
    # response string:  'YES'
    else:
        retrieveData = json.loads(request.body)
        # print gps
        lng = float(retrieveData['longitude'])
        lat = float(retrieveData['latitude'])
        filename = retrieveData['name']
        # avoid list type problem
        if isinstance(filename, list) :
            filename = filename[0]
        # add/edit gps info
        pg.set_gps_location('photos/' + filename, lat, lng)
        return HttpResponse('yes')

def check(request):
    """
    check if the photo has gps info
    NOT USED
    """
    filename = ''
    GPSinfo = pg.check_location('photos/' + filename)
    if GPSinfo != (0, 0):
        gps_dict = {'GPSInfo': 'YES', 'lng': GPSinfo[0], 'lat': GPSinfo[1]}
    else:
         gps_dict = {'GPSInfo': 'No', 'lng': 0, 'lat': 0}
    # post json to js
    return JsonResponse(gps_dict)

def addPhotos(request):
    """
    post all photo names to js
    """
    photo_names = []
    for (dirpath, dirname, filename) in os.walk('photos'):
        photo_names.append(filename)
    return JsonResponse(photo_names, safe=False)

def home(request):
    return render(request, 'home.html')

def ph2base64(filename):
    """
    encode .jpg to string(base64)
    """
    with open(filename, 'rb') as f:
        imgData = base64.b64encode(f.read())
    return str('data:image/jpg;base64,') + imgData