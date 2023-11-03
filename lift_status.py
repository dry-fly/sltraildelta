#Sugarloaf Lift Status
import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

#f = open("requestContent_lifts.txt", "rb")
#mountainReport = f.read()
#f.close()
#soup = BeautifulSoup(mountainReport, 'html.parser')


mountainReport = requests.get('https://www.sugarloaf.com/mountain-report')
soup = BeautifulSoup(mountainReport.content, 'html.parser')

dbConn = sqlite3.connect('SL_TRAILS.db')
dbCursor = dbConn.cursor()

def create_table():
    dbCursor.execute('CREATE TABLE IF NOT EXISTS SL_LIFTS (time TEXT, lift TEXT, status TEXT, detailStatus TEXT)')

def data_entry(runTime,liftName,status,detailStatus):
    dbCursor.execute("INSERT INTO SL_LIFTS (time,lift,status,detailStatus) VALUES(?, ?, ?, ?)", (runTime,liftName,status,detailStatus))
    dbConn.commit()
    
def icon_key(imageSrc):
    switch = {
        'Icon-open.png' : {"status": "Open"},
        'Icon-closed.png' : {"status":  "Closed"},
        'sl_icon_blue-clock_100x.jpg' : {"status": "Scheduled"},
        'yellow-caution.png' : { "status": "Hold"}
    }
    return switch.get(imageSrc,1)

       

create_table()
status = detailStatus = 'NULL'
now = datetime.now()
runTime = now.strftime("%Y%m%d-%H:%M-EST")

for item in soup.find("section", class_="conditionsLifts").find_all("div", class_="breakInsideAvoid"):
  lift = item.text.replace('^\n','').strip()
  #print(lift)
  liftName = lift.split("\n")[0]
  detailStatus = '/'.join(item.strip() for item in lift.split("\n")[1:])
  for image in item.find_all('img'):
    imageSrc = re.search(r"[\w-]+\.[psj][nvp]g",image.get('src')).group()
    element = icon_key(imageSrc)
    column = [*element].pop()
    if column == 'status':
        status = [*element.values()].pop()
    else:
        print("ERROR parsing data for trail:" + trail)
  
  #print("Lift:" + liftName + ", status=" + status + ", detailStatus=" + detailStatus)
  data_entry(runTime,liftName,status,detailStatus)
  status = detailStatus = 'NULL'

dbCursor.execute("SELECT DISTINCT time FROM SL_LIFTS ORDER BY time DESC")
dbConn.commit()
availTimes = dbCursor.fetchall()
secondDate = availTimes[0][0]
firstDate = availTimes[1][0]

dbCursor.execute("SELECT * FROM SL_LIFTS WHERE time = '" + secondDate + "'")
dbConn.commit()
for item in dbCursor.fetchall():
    print(item)
              
dbCursor.close()
dbConn.close()
    
