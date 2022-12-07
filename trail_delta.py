import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

f = open("requestContent.txt", "rb")
mountainReport = f.read()
f.close
soup = BeautifulSoup(mountainReport, 'html.parser')


mountainReport = requests.get('https://www.sugarloaf.com/mountain-report')
soup = BeautifulSoup(mountainReport.content, 'html.parser')

dbConn = sqlite3.connect('SL_TRAILS.db')
dbCursor = dbConn.cursor()

def create_table():
    dbCursor.execute('CREATE TABLE IF NOT EXISTS SL_TRAILS (time TEXT, trail TEXT, status TEXT, difficulty TEXT, grooming TEXT, making TEXT)')

def data_entry(runTime,trail,status,difficulty,grooming,making):
    dbCursor.execute("INSERT INTO SL_TRAILS (time,trail,status,difficulty,grooming,making) VALUES(?, ?, ?, ?, ?, ?)", (runTime,trail,status,difficulty,grooming,making))
    dbConn.commit()
    
def icon_key(imageSrc):
    switch = {
        'Icon-open.png' : {"status": "Open"},
        'Icon-closed.png' : {"status":  "Closed"},
        'circle.svg' : {"difficulty": "Green"},
        'square.svg' : {"difficulty": "Blue"},
        'black-diamond.svg' : {"difficulty": "Black"},
        'double-black.svg' : {"difficulty": "Expert"},
        'bh-icon-groomer.png' : {"grooming": "Grooming"},
        'snow-making.svg' : {"making": "Snow Making"}
    }
    return switch.get(imageSrc,1)

       

create_table()
status = difficulty = grooming = making = 'NULL'
now = datetime.now()
runTime = now.strftime("%Y%m%d-%H:%M-EST")

for item in soup.find_all("div", class_="breakInsideAvoid js-trail"):
  trail = item.text.replace('\n','').strip()  
  element = {}
  for image in item.find_all('img'):
    imageSrc = re.search(r"[\w-]+\.[ps][nv]g",image.get('src')).group()
    element = icon_key(imageSrc)
    column = [*element].pop()
    if column == 'status':
        status = [*element.values()].pop()
    elif column == 'difficulty':
        difficulty = [*element.values()].pop()
    elif column == 'grooming':
        grooming = [*element.values()].pop()
    elif column == 'making':
        making = [*element.values()].pop()
    else:
        print("ERROR parsing data for trail:" + trail)
  #print("Trail:" + trail + ", status=" + status + ", difficulty=" + difficulty + ", grooming=" + grooming + ", making=" + making)
  data_entry(runTime,trail,status,difficulty,grooming,making)
  status = difficulty = grooming = making = 'NULL'

dbCursor.execute("SELECT DISTINCT time FROM SL_TRAILS ORDER BY time DESC")
dbConn.commit()
availTimes = dbCursor.fetchall()
secondDate = availTimes[0][0]
firstDate = availTimes[1][0]

dbCursor.execute("SELECT trail,status FROM SL_TRAILS WHERE time = '" + firstDate + "'")
dbConn.commit()
firstList = dbCursor.fetchall()
dbCursor.execute("SELECT trail,status FROM SL_TRAILS WHERE time = '" + secondDate + "'")
dbConn.commit()
secondList = dbCursor.fetchall()

print("----- TRAIL DELTA:  " + firstDate + " --> " + secondDate)
print(list(set(secondList) - set(firstList)))
print("-----\n")

dbCursor.execute("SELECT trail, status FROM SL_TRAILS WHERE status = 'Open' AND time = '" + secondDate + "'")
dbConn.commit()
print("----- OPEN TRAILS:")
count = 0
for i in dbCursor.fetchall():
    print(i)
    count = count + 1
print("----- TOTAL OPEN: (%d) \n" % count)
dbCursor.execute("SELECT trail, grooming FROM SL_TRAILS WHERE grooming = 'Grooming' AND time = '" + secondDate + "'")
dbConn.commit()
print("----- GROOMING TRAILS:")
count = 0
for i in dbCursor.fetchall():
    print(i)
    count = count + 1
print("----- TOTAL GROOMING: (%d) \n" % count)
dbCursor.execute("SELECT trail, making FROM SL_TRAILS WHERE making = 'Snow Making' AND time = '" + secondDate + "'")
dbConn.commit()
print("----- SNOW MAKING TRAILS:")
count = 0
for i in dbCursor.fetchall():
    print(i)
    count = count + 1
print("----- TOTAL SNOW MAKING: (%d) \n" % count)
                 
dbCursor.close()
dbConn.close()
    
