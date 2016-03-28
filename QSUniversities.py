import urllib
import sqlite3
import json
import time
import ssl
import codecs
from bs4 import *

uh = urllib.urlopen('https://en.wikipedia.org/wiki/QS_World_University_Rankings#Results')
data=uh.read()
soup=BeautifulSoup(data,'html.parser')
tbl=soup.find('table',{'class':"sortable wikitable"})
sch=tbl.findAll('tr')[1:]
print 'Retrieved', len(sch), 'universities'

top=[]
for univ in sch :
    name=univ.findAll('a')[1].text
    rank=univ.findAll('td')[6].text
    N=name.encode('ascii','ignore')
    R=str(rank)
    top.append((N,R))

serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"


scontext = None

conn = sqlite3.connect('qs.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

count = 0
for line in top:
    address = line
    print ''
    cur.execute("SELECT geodata FROM Locations WHERE address= ?", (buffer(address), ))

    try:
        data = cur.fetchone()[0]
        print "Found in database ",address
        continue
    except:
        pass

    print 'Resolving', address
    url = serviceurl + urllib.urlencode({"sensor":"false", "address": address})
    print 'Retrieving', url
    uh = urllib.urlopen(url, context=scontext)
    data = uh.read()
    print 'Retrieved',len(data),'characters',data[:20].replace('\n',' ')
    count = count + 1
    try: 
        js = json.loads(str(data))
        # print js  # We print in case unicode causes an error
    except: 
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print '==== Failure To Retrieve ===='
        print data
        break

    cur.execute('''INSERT INTO Locations (address, geodata) 
            VALUES ( ?, ? )''', ( buffer(address),buffer(data) ) )
    conn.commit() 
    time.sleep(1)


cur.execute('SELECT * FROM Locations')
fhand = codecs.open('where.js','w', "utf-8")
fhand.write("myData = [\n")
count = 0
for row in cur :
    data = str(row[1])
    try: js = json.loads(str(data))
    except: continue

    if not('status' in js and js['status'] == 'OK') : continue

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]
    if lat == 0 or lng == 0 : continue
    where = js['results'][0]['formatted_address']
    where = where.replace("'","")
    try :
        print where, lat, lng

        count = count + 1
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+where+"']"
        fhand.write(output)
    except:
        continue

fhand.write("\n];\n")
cur.close()
fhand.close()
print count, "records written to where.js"
print "Open where.html to view the data in a browser"

