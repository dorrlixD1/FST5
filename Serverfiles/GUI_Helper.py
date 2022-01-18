from requests.models import Response
from flask import Flask, request, jsonify
import csv, urllib.request
import sys
from io import StringIO
import time
import datetime
import requests
import json
import cx_Oracle

cx_Oracle.init_oracle_client(r"/opt/oracle/instantclient_21_4/")

try:
    #Connection zur DB über localhost, da selbe Maschine
    dsn_tns = cx_Oracle.makedsn('localhost', '1539', service_name='XEPDB1') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    conn = cx_Oracle.connect(user=r'fst5', password='fallstudie5', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'

except:
    print('DB Connection not possible')

from flask import Flask
  
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
  
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/coordinates')
# ‘/’ URL is bound with hello_world() function.
def getCoords():
    address = request.args.get("address")
    result = requests.get("https://nominatim.openstreetmap.org/search?q="+urllib.parse.quote_plus(address)+"&format=json&polygon=1&addressdetails=1")
    result = result.json()
    print(result[0])
    CoordsDict = dict()
    CoordsDict['lat']=result[0]['lat']
    CoordsDict['lon']=result[0]['lon']
    res = [result[0]['lat'], result[0]['lon']]
    return CoordsDict


@app.route('/filterplz')
# ‘/’ URL is bound with hello_world() function.
def getPLZ():
    sql = "Select * from PLZVIEW"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    plzdict = dict()
    i = 0
    for row in result:
        plzdict[i]=row
        i+=1
    cursor.close()
    return plzdict

@app.route('/filterkg')
# ‘/’ URL is bound with hello_world() function.
def getKG():
    plz = request.args.get("plz")
    sql =""
    if plz == "":
        sql = "Select * from KGVIEW"
    else:
        sql = "Select * from KGVIEW WHERE PLZ_CODE="+str(plz)
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    plzdict = dict()
    i = 0
    for row in result:
        plzdict[i]=row
        i+=1
    cursor.close()
    return plzdict
  

@app.route('/filterwidmung')
# ‘/’ URL is bound with hello_world() function.
def getWidmung():
    sql = "Select * from WIDMUNGENVIEW"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    plzdict = dict()
    i = 0
    for row in result:
        plzdict[i]=row
        i+=1
    cursor.close()
    return plzdict

@app.route('/searchID')
def getLiegHistory():
    id = request.args.get("id")
    cursor = conn.cursor()
    refCursorVar = cursor.var(cx_Oracle.CURSOR)
    cursor.callproc('sp_READ_LIEG_HISTORY', [id, refCursorVar])
    print("Procedure called")
    refCursor = refCursorVar.getvalue()
    columns = [i[0] for i in refCursor.description]
    new_list = []
    for row in refCursor:
        row_dict = dict()
        for col in columns:
            # Create a new dictionary with field names as the key, 
            # row data as the value.
            #if (isinstance(row_dict[col], datetime.datetime)):
            #    row_dict[col]= row[columns.index(col)].strftime("%d.%m.%Y")
            # Then add this dictionary to the new_list
            #else:
            row_dict[col] = str(row[columns.index(col)])

        new_list.append(row_dict)
    #print(new_list)

    return json.dumps(new_list)


@app.route('/search', methods=['POST'])
def getLieg():
    cursor = conn.cursor()
    refCursorVar = cursor.var(cx_Oracle.CURSOR)

    attributes = request.get_json(force=True)
    
    if (attributes["plz"] == ""):
        attributes["plz"]=-1
    if (attributes["kg"] == ""):
        attributes["kg"]=None
    if (attributes["straße"] == ""):
        attributes["straße"]=None
    if (attributes["widmLang"] == ""):
        attributes["widmLang"]=None
    if (attributes["zuordnung"] == ""):
        attributes["zuordnung"]=None
    if (attributes["preisVon"] == ""):
        attributes["preisVon"]=0
    if (attributes["preisBis"] == ""):
        attributes["preisBis"]=0
    if (attributes["flaecheVon"] == ""):
        attributes["flaecheVon"]=0
    if (attributes["flaecheBis"] == ""):
        attributes["flaecheBis"]=0
    if (attributes["baujahrVon"] == ""):
        attributes["baujahrVon"]=0
    if (attributes["baujahrBis"] == ""):
        attributes["baujahrBis"]=0
    if (attributes["erwDatumVon"] == ""):
        attributes["erwDatumVon"]=None
    if (attributes["erwDatumBis"] == ""):
        attributes["erwDatumBis"]=None
    if (attributes["bausperre"] == ""):
        attributes["bausperre"]=-1
    if (attributes["baurecht"] == ""):
        attributes["baurecht"]=-1
    if (attributes["schutzzone"] == ""):
        attributes["schutzzone"]=-1
    if (attributes["parzelliert"] == ""):
        attributes["parzelliert"]=-1
    if (attributes["oezwecke"] == ""):
        attributes["oezwecke"]=-1
    if (attributes["baureifgest"] == ""):
        attributes["baureifgest"]=-1

    print(attributes)
#    print(f'sp_Search_LIEGREC(\'{attributes["plz"]}\',\'{attributes["kg"]}\',\'{attributes["straße"]}\',NULL,\'{attributes["zuordnung"]}\',\'{attributes["preisVon"]}\',\'{attributes["preisBis"]}\',\'{attributes["flaecheVon"]}\',\'{attributes["flaecheBis"]}\',\'{attributes["baujahrVon"]}\',\'{attributes["baujahrBis"]}\',\'{attributes["erwDatumVon"]}\',\'{attributes["erwDatumBis"]}\',\'{attributes["bausperre"]}\',\'{attributes["baurecht"]}\',\'{attributes["schutzzone"]}\',\'{attributes["parzelliert"]}\',\'{attributes["oezwecke"]}\',\'{attributes["baureifgest"]}\',{[refCursorVar]}); end;')
#    cursor.execute(f'sp_Search_LIEGREC(\'{attributes["plz"]}\',\'{attributes["kg"]}\',\'{attributes["straße"]}\',NULL,\'{attributes["zuordnung"]}\',\'{attributes["preisVon"]}\',\'{attributes["preisBis"]}\',\'{attributes["flaecheVon"]}\',\'{attributes["flaecheBis"]}\',\'{attributes["baujahrVon"]}\',\'{attributes["baujahrBis"]}\',\'{attributes["erwDatumVon"]}\',\'{attributes["erwDatumBis"]}\',\'{attributes["bausperre"]}\',\'{attributes["baurecht"]}\',\'{attributes["schutzzone"]}\',\'{attributes["parzelliert"]}\',\'{attributes["oezwecke"]}\',\'{attributes["baureifgest"]}\',{[refCursorVar]}); end;')
    cursor.callproc('sp_Search_LIEGREC', [attributes['plz'], attributes['kg'],attributes["straße"],attributes["widmLang"],attributes["zuordnung"],attributes["preisVon"],attributes["preisBis"],attributes["flaecheVon"],attributes["flaecheBis"],attributes["baujahrVon"],attributes["baujahrBis"],attributes["erwDatumVon"],attributes["erwDatumBis"],attributes["bausperre"],attributes["baurecht"],attributes["schutzzone"],attributes["parzelliert"],attributes["oezwecke"],attributes["baureifgest"], refCursorVar])
    print("Procedure called")
    refCursor = refCursorVar.getvalue()
    columns = [i[0] for i in refCursor.description]
    new_list = []
    for row in refCursor:
        row_dict = dict()
        for col in columns:
            # Create a new dictionary with field names as the key, 
            # row data as the value.
            #if (isinstance(row_dict[col], datetime.datetime)):
            #    row_dict[col]= row[columns.index(col)].strftime("%d.%m.%Y")
            # Then add this dictionary to the new_list
            #else:
            row_dict[col] = str(row[columns.index(col)])

        new_list.append(row_dict)
    #print(new_list)

    return json.dumps(new_list)
#    for res in refCursor:
#        print(res)
#    print(json.dumps(refCursor))
#    cursor.execute(f"begin SP_Search_LIEGREC(\'"+ 
#        ("-1" if attributes["plz"]=="" else attributes["plz"])+"\',\'"+
#        (None if attributes["kg"]=="" else attributes["kg"])+"\',\'"+
#        attributes["straße"]+"\',\'"+
#        attributes["widmLang"]+"\',\'"+
#        attributes["zuordnung"]+"\',\'"+
#        attributes["preisVon"]+"\',\'"+
#        attributes["preisBis"]+"\',\'"+
#        attributes["flaecheVon"]+"\',\'"+
#        attributes["flaecheBis"]+"\',"+
#        attributes["baujahrVon"]+",\'"+
#        attributes["baujahrBis"]+"\',\'"+
#        ('0' if attributes["erwDatumVon"]=="FALSCH" else attributes["erwDatumVon"])+"\',\'"+
#        ('0' if attributes["erwDatumBis"]=="FALSCH" else attributes["erwDatumBis"])+"\',\'"+
#        ('0' if attributes["bausperre"]=="FALSCH" else attributes["bausperre"])+"\',\'"+
#        ('0' if attributes["baurecht"]=="FALSCH" else attributes["baurecht"])+"\',"+
#        attributes["schutzzone"]+",\'"+ #attributes["seit/bis"], Ist als Datum in DB eingetragen, wird zu selten befüllt oder nicht als DATE, wenn dann lieber varchar als Datentyp in DB eintragen
#        attributes["parzelliert"]+"\',\'"+
#        ('0' if attributes["oezwecke"] == "" else attributes["oezwecke"])+"\',\'"+
#        ('1' if attributes["baureifgest"]=="J" else attributes["baureifgest"])+"\',\'"+refCursorVar+"\'); end;")
    return "OK"
    

@app.route('/filterzuordnung')
# ‘/’ URL is bound with hello_world() function.
def getZuordnung():
    sql = "Select * from ZUORDNUNGVIEW"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    plzdict = dict()
    i = 0
    for row in result:
        plzdict[i]=row
        i+=1
    cursor.close()
    return plzdict

# main driver function
if __name__ == '__main__':
  
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(host='192.168.188.33', port=5000)