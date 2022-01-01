import csv, urllib.request
import sys
from io import StringIO
import time
import cx_Oracle

cx_Oracle.init_oracle_client(r"/opt/oracle/instantclient_21_4/")

try:
    #Connection zur DB über localhost, da selbe Maschine
    dsn_tns = cx_Oracle.makedsn('localhost', '1539', service_name='XEPDB1') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    conn = cx_Oracle.connect(user=r'fst5', password='fallstudie5', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'

except:
    print('DB Connection not possible')


def entryTypeDict(row, keys):
    entryTypeDict = dict()
    delimiter = ";"

  
    
    row = row[row.find("'")+1:len(row)-2]
    attributes = row.split(delimiter)
    

    i=0
    for attribute in attributes:
        entryTypeDict[keys[i]] = attribute
        i = i+1
    
    return entryTypeDict



    
def getDictKeys(row):
    delimiter = ";"
    
    row = row[row.find("'")+1:len(row)-2]
    attributes = row.split(delimiter)
    return attributes


def seAttributesNeedSeAnfuerungsDinegens(dingens):
    try:
        dingens = '\''+dingens + '\''
    except:
        dingens = '\''+str(dingens) + '\''

def insertInSeDb(attributes, cursor):
    
    #print('SP_INSERT_LIEGREC('+str(arr_attr)+')')
    cursor.execute("begin SP_INSERT_LIEGREC(\'"+ attributes["KG.Code"]+"\',\'"+
        attributes["Katastralgemeinde"]+"\',\'"+
        attributes["EZ"]+"\',\'"+
        attributes["PLZ"]+"\',\'"+
        attributes["Straße"]+"\',\'"+
        attributes["ON"]+"\',\'"+
        attributes["Gst."]+"\',\'"+
        attributes["Gst.Fl."]+"\',\'"+
        attributes["ErwArt"]+"\',"+
        "to_date(\'"+attributes["Erwerbsdatum"]+"\', \'DD.MM.YYYY\')"+",\'"+
        attributes["Widmung"]+"\',\'"+
        ('0' if attributes["Schutzzone"]=="FALSCH" else '1')+"\',\'"+
        ('0' if attributes["Wohnzone"]=="FALSCH" else '1')+"\',\'"+
        ('0' if attributes["öZ"]=="FALSCH" else '1')+"\',\'"+
        ('0' if attributes["Bausperre"]=="FALSCH" else '1')+"\',"+
        "to_date(\'"+attributes["Erwerbsdatum"]+"\', \'DD.MM.YYYY\')"+",\'"+ #attributes["seit/bis"], Ist als Datum in DB eingetragen, wird zu selten befüllt oder nicht als DATE, wenn dann lieber varchar als Datentyp in DB eintragen
        attributes["zuordnung"].replace('\'','')+"\',\'"+
        ('0' if attributes["Geschoße"] == "" else attributes["Geschoße"])+"\',\'"+
        ('1' if attributes["parz."]=="J" else '0')+"\',\'"+
        ('0' if attributes["BJ"] == "" else attributes["BJ"])+"\',\'"+
        ('0' if attributes["TZ"] == "" else attributes["TZ"])+"\',\'"+
        ('0' if attributes["Kaufpreis \\x80"] == "" else attributes["Kaufpreis \\x80"].replace(',','.').replace(' ','').replace('\'',''))+"\',\'"+
        ('1' if attributes["Baureifgest"]=="WAHR" else '0')+"\',\'"+
        ('1' if attributes["Baurecht"]=="WAHR" else '0')+"\'); end;")
    #cursor.callproc('sp_INSERT_LIEGREC', arr_attr)
    print("Entry written to DB")
    #print(e+" at: "+attributes)
    

    
       
def main():
    url = 'https://go.gv.at/l9kaufpreissammlungliegenschaften'
    response = urllib.request.urlopen(url)
    lines = [l.decode('latin_1') for l in response.readlines()]
    cr = csv.reader(lines)
    
    k = 0
    attributes_dictionary = list(dict())
    fehlerliste = str()
    fehleranzahl = 0
    attributes_Immo = dict()
    cursor = conn.cursor()
    arr_attr = []
    
    for row in cr:
        if(k == 0):
            #print(row)
            keys = getDictKeys(str(row))
            for key in keys:
                #print("\n")
                print(key)
        else:
            try:
                attributes_Immo = entryTypeDict(str(row), keys)
                arr_attr = [
                    attributes_Immo["KG.Code"],
                    attributes_Immo["Katastralgemeinde"],
                    attributes_Immo["EZ"],
                    attributes_Immo["PLZ"],
                    attributes_Immo["Straße"],
                    attributes_Immo["ON"],
                    attributes_Immo["Gst."],
                    attributes_Immo["Gst.Fl."],
                    attributes_Immo["ErwArt"],
                    "to_date(\'"+attributes_Immo["Erwerbsdatum"]+"\', \'DD.MM.YYYY\')",
                    attributes_Immo["Widmung"],
                    ('0' if attributes_Immo["Schutzzone"]=="FALSCH" else '1'),
                    ('0' if attributes_Immo["Wohnzone"]=="FALSCH" else '1'),
                    ('0' if attributes_Immo["öZ"]=="FALSCH" else '1'),
                    ('0' if attributes_Immo["Bausperre"]=="FALSCH" else '1'),
                    "to_date(\'"+attributes_Immo["Erwerbsdatum"]+"\', \'DD.MM.YYYY\')", #attributes_Immo["seit/bis"], Ist als Datum in DB eingetragen, wird zu selten befüllt oder nicht als DATE, wenn dann lieber varchar als Datentyp in DB eintragen
                    attributes_Immo["zuordnung"],
                    ('0' if attributes_Immo["Geschoße"] == "" else attributes_Immo["Geschoße"]),
                    ('1' if attributes_Immo["parz."]=="J" else '0'),
                    ('0' if attributes_Immo["BJ"] == "" else attributes_Immo["BJ"]),
                    ('0' if attributes_Immo["TZ"] == "" else attributes_Immo["TZ"]),
                    ('0' if attributes_Immo["Kaufpreis \\x80"] == "" else attributes_Immo["Kaufpreis \\x80"].replace(',','.').replace(' ','').replace('\'','')),
                    ('1' if attributes_Immo["Baureifgest"]=="WAHR" else '0'),
                    ('1' if attributes_Immo["Baurecht"]=="WAHR" else '0')
                ]
                insertInSeDb(attributes_Immo,cursor)
                attributes_dictionary.append(arr_attr)
            except Exception as e:
                fehlerliste = fehlerliste + "\n" + "Datensatz Nummer " + str(k+1) + " im Oarschloch      Rohdatensatz = " + str(arr_attr)
                fehleranzahl = fehleranzahl + 1
                print(e)
                print(arr_attr)
                #return
                pass
            
        k = k+1

    cursor.close()
    conn.commit()
    conn.close()
    
    #print(attributes_dictionary)
    #print("\n" + "\n")

    #print(str(k+1) + " Datensätze eingelesen     davon " + str(fehleranzahl) + " fehlerhaft")
    #print("Fehler:")
    #print(fehlerliste)
    
    
    filename = "log_" + str(time.time()) + ".log"
    log_file = open("Logs/" + filename, "wt")
    n = log_file.write(fehlerliste)
    log_file.close()
    
sys.exit(main())