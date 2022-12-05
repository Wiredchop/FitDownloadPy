#Adapted from Cyberjunky's example file 

#!/usr/bin/env python3
"""
pip3 install cloudscraper requests readchar pwinput

"""
import datetime
import zipfile
import fitdecode
import json
import logging
import os
import sys
import requests
import pwinput
import readchar

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)
#Load the sessions from the JSON file
from fit_Sessions import fit_sessions

# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api = None

# Example selections and settings
activitytype = ""  # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
activityfile = "MY_ACTIVITY.fit" # Supported file types are: .fit .gpx .tcx


def get_credentials():
    """Get user credentials."""
    email = input("Login e-mail: ")
    password = pwinput.pwinput(prompt='Password: ')

    return email, password

def init_api(email, password):
    """Initialize Garmin API with your credentials."""
    # Had trouble with the saved .json files so requiring password login every time.
    #Maintaining option to store it as a environment variable.
    try:
        ## Try to load the previous session
        with open("session.json") as f:
            saved_session = json.load(f)

            print(
                "Login to Garmin Connect using session loaded from 'session.json'...\n"
            )

            # Use the loaded session for initializing the API (without need for credentials)
            api = Garmin(session_data=saved_session)

            # Login using the
            api.login()

    except (FileNotFoundError, GarminConnectAuthenticationError):
        # Login to Garmin Connect portal with credentials since session is invalid or not present.
        print(
            "Session file not present or turned invalid, login with your Garmin Connect credentials.\n"
            "NOTE: Credentials will not be stored, the session cookies will be stored in 'session.json' for future use.\n"
        )
        try:
                    # Ask for credentials if not set as environment variables
                    if not email or not password:
                        email, password = get_credentials()

                    api = Garmin(email, password)
                    api.login()

                    # Save session dictionary to json file for future use
                    with open("session.json", "w", encoding="utf-8") as f:
                        json.dump(api.session_data, f, ensure_ascii=False, indent=4)
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error("Error occurred during Garmin Connect communication: %s", err)
            return None
    return api

def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-"*20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-"*len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)

def display_text(output):
    """Format API output for better readability."""
    dashed = "-"*60
    header = f"{dashed}"
    footer = "-"*len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)

sessions = fit_sessions()
if sessions.number_of_sessions() == 0:
    print("No stored sessions")
    print("You can load existing sessions by putting the zip files in the FITzip folder")
    # No sessions stored can do something here if need be
    latest_session = datetime.date.today() - datetime.timedelta(days=7) # Select past week
else:
    # Find last recorded session in list    
    list_of_session_dates = [i["date"] for i in sessions.sessions]
    latest_session = max(list_of_session_dates) + datetime.timedelta(days=1) #Add one day to avoid recapturing session
    latest_session_display = latest_session.strftime("%x")
    
    print(f"Loaded sessions, {sessions.number_of_sessions()} stored in file")
    print(f"The last recorded session was on: {latest_session}")
    today = datetime.date.today()
    today_display = today.strftime("%x")

menu_options = {
    "1": "Update stored sessions from .fit files",
    "2": f"Get sessions from api between {latest_session_display} and {today_display}",
    "3": "Attempt to get all sessions from api",
    "q": "Quit menu"
}
def print_menu():
    """Print examples menu."""
    print("====--- MAIN MENU ---====")
    for key in menu_options.keys():
        print(f"{key} -- {menu_options[key]}")
    print("=========================")
    print("Make your selection: ", end="", flush=True)

api = init_api(email,password)    


def add_activity_to_sessions(activity: fit_sessions) -> bool:
    start_date_time = datetime.datetime.fromisoformat(activity["startTimeLocal"])
    session_type = activity["activityType"]["typeKey"]
    session_duration = activity["duration"]
    session_distance = activity["distance"]
    return sessions.add_sesssion(start_date_time,session_type,session_duration,session_distance)

def update_log_from_zips():
    directory_contents = os.listdir('./FITzips')
    for this_file in directory_contents:
        if this_file.endswith('.zip'):
            print(f'opening {this_file}')
            full_file = os.path.join('.\\FITzips',this_file)
            with zipfile.ZipFile(full_file,mode='r') as archive:
                archive_contents = archive.namelist()
                for fitfile in archive_contents:
                    if os.path.splitext(fitfile)[1] != '.fit':
                        continue
                    print(f'opening {fitfile}')
                    with archive.open(fitfile) as fitstream:
                        with fitdecode.FitReader(fitstream) as fit:
                            for frame in fit:
                                if frame.frame_type == fitdecode.FIT_FRAME_DATA:        
                                    # Here, frame is a FitDataMessage object.
                                    # A FitDataMessage object contains decoded values that
                                    # are directly usable in your script logic.
                                    if frame.name == "session":
                                        start_time = datetime.MINYEAR
                                        session_type = ""
                                        session_distance = 0
                                        session_elapsed_time = 0
                                        for field in frame:                  
                                            
                                            if field.name == "start_time":
                                                start_time = field.value
                                                print(f'start time: {field.value}')
                                            if field.name == "total_distance":
                                                session_distance = field.value                                    
                                                print(f'session distance: {field.value}')
                                            if field.name == "sport":
                                                session_type = field.value                                    
                                                print(f'session type: {field.value}')
                                            if field.name == "total_elapsed_time":
                                                session_elapsed_time = field.value                                    
                                                print(f'session elapsed time: {field.value}')                                         
                                        if not sessions.add_sesssion(start_time,session_type,session_elapsed_time,session_distance):
                                            print('Session duplicate, not added')
                print(f'Added {sessions.number_of_sessions()} to archive')
                sessions.write_as_json()
                print('Session file written')


def switch(api, i):
    
    """Run selected API call."""
    # Exit example program
    if i == "q":
        print("Bye!")
        sys.exit()
    
    # Skip requests if login failed
    if api:
        if i == "1":
            update_log_from_zips()
        if i == "2":    
            # Get activities data from startdate 'YYYY-MM-DD' to enddate 'YYYY-MM-DD', with (optional) activitytype
            # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
            activities = api.get_activities_by_date(
                latest_session.isoformat(), today.isoformat(), activitytype
            )
            
            added = 0
            # Download activities
            for activity in activities:

                activity_id = activity["activityId"]
                if add_activity_to_sessions(activity):
                    added += 1
                display_text(activity)

                print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)")
                zip_data = api.download_activity(
                    activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL
                )
                output_file = f"./FITzips/{str(activity_id)}.zip"
                with open(output_file, "wb") as fb:
                    fb.write(zip_data)
                print(f"Activity data downloaded to file {output_file}")
            sessions.write_as_json()
            print(f'added {added} activities to session file')
        if i == '3':
            start = 0
            limit = 100
            activities = api.get_activities(start, limit) # 0=start, 1=limit
            added = 0
            for activity in activities:

                activity_id = activity["activityId"]
                if add_activity_to_sessions(activity):
                    added += 1            
                display_text(activity)

                print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)")
                zip_data = api.download_activity(
                    activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL
                )
                output_file = f"./FITzips/{str(activity_id)}.zip"
                with open(output_file, "wb") as fb:
                    fb.write(zip_data)
                print(f"Activity data downloaded to file {output_file}")
            sessions.write_as_json()
            print(f'added {added} activities to session file')
while True:
    print_menu()
    option = readchar.readkey()
    switch(api, option)