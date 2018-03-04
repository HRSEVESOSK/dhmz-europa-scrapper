#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json,pgsql,calendar,urllib
from urllib.request import urlopen,Request,quote

from datetime import datetime
import xml.etree.ElementTree as ET

print("****** Scrapper process started on '%s' \n" % datetime.now().isoformat())
connection = pgsql.PGSql()
xmlUrl = "http://vrijeme.hr/europa_e.xml"
response = urlopen(xmlUrl)
tree = ET.parse(response)
root = tree.getroot()
date = root[0][0].text.split(" ")
month=date[2].split(',')[0]
months = dict((v,k) for k,v in enumerate(calendar.month_name))
if month in months:
    dateMonth = str(months[month]).zfill(2)
else:
    print("Cannot parse month value from element datum, exiting process")
    exit()
timeCheck = root[0][1].text
dateTimeString = date[3] + "-" + dateMonth + "-" + date[0][:2] + "T" + timeCheck + ":00:00"
print("Processing observations for datetime: '%s'" % dateTimeString)
for foi in root.findall('Grad'):
    foiId = (foi.find('GradIme').text).replace(" ","_").replace("(","").replace(")","")
    foiName = foi.find('GradIme').text
    sql="SELECT oid FROM foi WHERE id='%s'" % foiId
    connection.connect()
    foiExists = connection.query(sql, False)
    connection.close()
    if not foiExists:
        osmCity = 'http://nominatim.openstreetmap.org/search?q=&format=json&city=%s' % quote(foiName.encode('utf-8'))
        request = (osmCity)
        response = urlopen(request)
        str_response = response.read().decode('utf-8')
        respData = json.loads(str_response)
        #respData = response.json()
        if not respData:
            osmQuery = 'http://nominatim.openstreetmap.org/search?q=%s&format=json' % quote(foiName.encode('utf-8'))
            request = Request(osmQuery)
            response = urlopen(request)
            str_response = response.read().decode('utf-8')
            respData = json.loads(str_response)
            #respData = json.load(response)
        if not respData:
            print("FOI name '%s' not found in openstreetmap nominatim service" % foiName.encode('utf-8'))
            continue
        foiLon = respData[0]['lon']
        foiLat = respData[0]['lat']
        metadata = ''
        sql = "INSERT INTO foi (id,geom) VALUES ('%s', ST_SetSRID(ST_MakePoint(%s, %s),4326)) RETURNING OID" % (foiId,foiLon,foiLat)
        connection.connect()
        insertFoi = connection.query(sql,False)
        connection.close()
        foiOID = insertFoi[0][0]
        print("Inserting new FOI:'%s'" % foiOID)
    else:
        sql = "SELECT oid FROM foi WHERE id='%s'" % foiId
        connection.connect()
        selectFoi = connection.query(sql, False)
        connection.close()
        foiOID = selectFoi[0][0]
    if foiOID:
        sql = 'SELECT time::timestamp from observation where foi_ref = %s order by time desc' % foiOID
        connection.connect()
        lastObsDateTime = connection.query(sql, False)
        connection.close()
        if not lastObsDateTime or (lastObsDateTime[0][0]).isoformat() != dateTimeString:
            print("Inserting Observations for foi '%s' and time '%s'" % (foiOID,(dateTimeString)))
            data = {}
            for obs in root.findall(".//Grad[GradIme='%s']/Podatci/*" % foi.find('GradIme').text):
                table = 'obs'
                data[obs.tag] = obs.text
            json_data = json.dumps(data, ensure_ascii=False)
            sql="INSERT INTO observation (time,foi_ref,data) VALUES ('%s',%s,'%s')" % (dateTimeString, foiOID, json_data)
            connection.connect()
            insertObservation = connection.query(sql, False)
            connection.close()
            if(insertObservation):
                print("Observations '%s' succesfully inserted for time '%s' and FOI '%s'" % (json_data.encode('utf-8'),dateTimeString,foiOID))
            else:
                print("Failed insert for observations '%s' succesfully inserted for time '%s' and FOI '%s'" % (json_data, dateTimeString, foiOID))
        else:
            print("Observations for foi '%s' and time '%s' are already stored in the database" % (foiOID,(lastObsDateTime[0][0]).isoformat()))
            continue
    else:
        print("Process could not get/insert FOI for '%s'" % foiId)
print("\n****** Scrapper process finished on '%s' \n" % datetime.now().isoformat())
