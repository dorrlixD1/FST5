from flask import Flask, request, jsonify
import csv, urllib.request
import sys
from io import StringIO
import time
import requests
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
