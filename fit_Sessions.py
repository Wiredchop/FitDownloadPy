import os
import pytz
import datetime
import shutil
import json

class fit_sessions:
    
    def __init__(self) -> list:
        if os.path.exists('sessions.json'):
            self.load_from_json()
        else:
            self.sessions = []
    def add_sesssion(self,date_of_session: datetime,type_of_session: str,elapsed_time_of_session,distance_of_session):
        # Going to check for duplication before adding, if session on same date and same length, then don't add
        
         #Find dictionary matching value in list
         #Localize all times so every datetime is timezone aware
        matching_session = next((session for session in self.sessions if session['date'] == date_of_session and session['elapsed_time'] == elapsed_time_of_session), None)
        if matching_session == None:
            if date_of_session.tzinfo == None:
                date_of_session = pytz.utc.localize(date_of_session)
            self.sessions.append({"date":date_of_session,"type":type_of_session,"elapsed_time":elapsed_time_of_session,"distance":distance_of_session})
            return True
        else:
            return False
    def number_of_sessions(self) -> int:
        return len(self.sessions)
    
    def json_serial(self,obj):
        """JSON serializer for objects not serializable by default json code"""
        "Nice bit of code from Stackoverflow to deal with"
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    def write_as_json(self) -> None:
        #Backup file if already exists
        if os.path.exists('sessions.json'):
            shutil.copy('./sessions.json','./session.bak')
        json_obj = json.dumps(self.sessions, indent=2,default=self.json_serial)
        with open('sessions.json','w') as jsonfile:
            jsonfile.write(json_obj)
    
    def convert_date_in_dictionary(self,dct) -> dict:
        #This is a static converter for the specific structure created in this class, so is lazy and doesn't generalise
        dct['date'] = datetime.datetime.fromisoformat(dct['date'])
        return dct
        
    def load_from_json(self) -> None:
        with open('sessions.json') as jsonfile:            
            self.sessions = json.load(jsonfile,object_hook=self.convert_date_in_dictionary)
        