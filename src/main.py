from json.encoder import JSONEncoder
import os
from os import error
import requests
import datetime
from datetime import date, timedelta, datetime
import json
from colorama import Fore
from decouple import config
from threading import Timer, Thread
import schedule
import time
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "WebUntis API ready"

def run():
  app.run(host='0.0.0.0',port=8080)

t = Thread(target=run)
t.start()

http_session = requests.session()

# Setting URL to Call
url = 'https://stundenplan.hamburg.de/WebUntis/jsonrpc.do?school=' + str(os.getenv('SCHOOL'))
#alerted = False

# Define Headers
headers = {
    'User-Agent': 'WebUntis Nitroapp',
    'Content-Type': 'application/json'
}

# Start Authentication #

def authAPI(user, password):

    try:

        data = {
            'id': str(datetime.now()),
            'method': 'authenticate',
            'params':
            {
                'user': user,
                'password': password,
                'client': 'Nitroapp Untis'
            },
            'jsonrpc': '2.0'
        }

        authenticate = http_session.post(url, data=json.dumps(data), headers=headers)
        print(Fore.CYAN + 'Authentication ' + Fore.RESET + '→ Connection established to: ' + url)

    except (Exception, ArithmeticError) as e:
        template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
        message = template.format(type(e).__name__, e.args)
        print (message)

# End Authentication #

# Start Request #

def postAPI(method, filename, parameters):

    # Try to Execute API Call
    try:

        # Parameter Handler
        if (parameters == None):
            data = {'id': str(datetime.now()), 'method': method, 'params': {}, 'jsonrpc': '2.0'}
        else:
            data = {'id': str(datetime.now()), 'method': method, 'params': parameters, 'jsonrpc': '2.0'}

        # API Call
        request = http_session.post(url, data=json.dumps(data), headers=headers)

        if 'no allowed date' in request.text:
            print(Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception has occured (' + filename + '.json) ' + Fore.LIGHTRED_EX + 'Timespan not allowed')
            return

        elif 'Method not found' in request.text:
            print(Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception has occured (' + filename + '.json) ' + Fore.LIGHTRED_EX + 'Invalid method')
            return  
        
        elif 'error' in request.text:
            print(Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception has occured (' + filename + '.json) ' + Fore.LIGHTBLACK_EX + request.text)
            return

        # Create File
        with open('../out/' + filename + '.json', 'w') as write_file:
            json.dump(json.loads(request.text), write_file, indent=4)

        # Complete API Call
        print(Fore.GREEN + 'Success' + Fore.RESET + '→ Created File: ' + filename + '.json')

    # Catch Error
    except (Exception, ArithmeticError) as e:
        template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
        message = template.format(type(e).__name__, e.args)
        print (message)

# End Request #

# Start GET  #

def getAPI(url):

    # Try to Execute API Call
    try:

        # API Call
        request = http_session.get(url, headers=headers)
        answer = request.text

        with open('../out/' + "timetable" + '.json', 'w') as write_file:
            json.dump(json.loads(request.text), write_file, indent=4)

        def getData(keyword):
            wat = json.load(open("../out/timetable.json"))
            for index_number, dicts in wat["data"]["result"]["data"]["elementPeriods"].items():
                for d in dicts:
                    if d["cellState"] == keyword:
                        #print(d['elements'])
                        elements = d['elements']
                        for data in elements:
                            if data['id'] == 104:
                                #print(data['type'])
                                return "Geschichte"
                            elif data['id'] == 112:
                                return "Seminar"
                            elif data['id'] == 89:
                                return "Spanisch"
                            elif data['id'] == 153:
                                return "Sport"
                            elif data['id'] == 10:
                                return "Biologie"
                            elif data['id'] == 90:
                                return "Psychologie"
                            elif data['id'] == 3:
                                return "Englisch"
                            elif data['id'] == 107:
                                return "Mathematik"
                            elif data['id'] == 115:
                                return "Chor"
                            elif data['id'] == 102:
                                return "Kunst"
                            elif data['id'] == 87:
                                return "Geographie"
                            elif data['id'] == 105:
                                return "Informatik"
                            elif data['id'] == 2:
                                return "Deutsch"
                            elif data['id'] == 87:
                                return "Geographie"
                            elif data['id'] == 3:
                                return "Englisch"
                            elif data['id'] == 87:
                                return "Geographie"
                            elif data['id'] == 103:
                              return "Chemie"
                            elif data['id'] == 84:
                              return "PGW"
                            elif data['id'] == 15:
                              return "Philosophie"
                            elif data['id'] == 11:
                              return "Religion"
                            elif data['id'] == 165:
                              return "Theater"
                            elif data['id'] == 114:
                              return "Klassenlehrerstunde"
            
        if (answer.__contains__('SUBSTITUTION')):
            #print(getData('SUBSTITUTION'))
            print("Vertretung")
            alertWhatsapp("*Vertretung* im Fach " + getData('SUBSTITUTION') + "\nFür weitere Informationen, überprüfen Sie bitte die Untis App.", os.getenv('WPAPI'), "subst")

        if (answer.__contains__('CANCEL')):
            print("Ausfall")
            alertWhatsapp("*Ausfall* im Fach " + getData('CANCEL') + "\nFür weitere Informationen, überprüfen Sie bitte die Untis App.", os.getenv('WPAPI'), "cancel")  


        # Complete API Call
        print(Fore.GREEN + 'Success' + Fore.RESET + '→ Created File: ' + "timetable" + '.json')

    # Catch Error
    except (Exception, ArithmeticError) as e:
        template = Fore.LIGHTRED_EX + 'ErrorE ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
        message = template.format(type(e).__name__, e.args)
        print (message)

# End GET #

# Start Logout #

def logout():

    try:

        data = {
            'id': str(datetime.now()),
            'method': 'logout',
            'params':{},
            'jsonrpc': '2.0'
        }
        print(Fore.CYAN + 'Authentication ' + Fore.RESET + '→ Connection closed')

    except (Exception, ArithmeticError) as e:
        template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
        message = template.format(type(e).__name__, e.args)
        print (message)

# End Logout #

# Start Alert Whatsapp #

def alertWhatsapp(content, auth, type):
    #global alerted

    if (os.path.exists(type + '.txt') == False):
        try:
            #alerted = True
            #$get-recipient
            data = {"content": content, "recipient": "4915734507150-1596723490@g.us", "authorization": auth}
            request = http_session.post('http://wa.constellate.de/v1/post', data=json.dumps(data), headers=headers)
            os.mknod(type + ".txt")

        except (Exception, ArithmeticError) as e:
            template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
            message = template.format(type(e).__name__, e.args)
            print (message)

# End Alert Whatsapp #

# Get Timetable #
def getTimetable():
    #print(alerted)
    authAPI(os.getenv('USER'), os.getenv('PASSWORD'))
    getAPI("https://stundenplan.hamburg.de/WebUntis/api/public/timetable/weekly/data?elementType=1&elementId=183&date=" + getDate() + "&formatId=6")
    logout()
# End Timetable #



# Get Date #
def getDate():
    now = date.today() # current date and time
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    return year + '-' + month + '-' + day


# Start POST Requests #

if (os.getenv('POST') == "True"):
    authAPI(config('USER'), config('PASSWORD'))
    #postAPI('getKlassen', 'classes', None)
    #postAPI('getSubjects', 'subjects', None)
    #postAPI('getRooms', 'rooms', None)
    #postAPI('getTimegridUnits', 'timegrid', None)
    #postAPI('getStatusData', 'status', None)
    #postAPI('getCurrentSchoolyear', 'current-schoolyear', None)
    #postAPI('getSchoolyears', 'all-schoolyears', None)
    postAPI('getTimetable', 'timetable-specific', {"id":183,"type":1,"startDate": 20210816, "endDate": 20210820})
    logout()

else:
    print (Fore.LIGHTYELLOW_EX + 'Info ' + Fore.RESET + '→ All POST requests have been disabled in the config.')

# End POST Requests #

# Start GET Requests #

if (os.getenv('GET') == "True"):
    schedule.every(1).minutes.do(getTimetable)

else:
    print (Fore.LIGHTYELLOW_EX + 'Info ' + Fore.RESET + '→ All GET requests have been disabled in the config.')

# End GET Requests #

def resetAlerted():
    if os.path.exists("../check/subst.txt"):
      os.remove('../check/subst.txt')

    if os.path.exists("../check/cancel.txt"):
      os.remove('../check/cancel.txt')

#schedule.every().day.at("18:23").do(resetAlerted)
schedule.every().day.at("05:10").do(resetAlerted)

while True:
    schedule.run_pending()
    time.sleep(30)
    print(datetime.now())
    print (Fore.GREEN + 'Success ' + Fore.RESET + '→ Schedule refreshed')