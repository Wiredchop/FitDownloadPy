# FitDownloadPy
This is a relatively simple script I wrote to manage .FIT files downloaded from Garmin Connect. I recently got into [Golden Cheetah](https://www.goldencheetah.org/) and liked the fact you could have the software watch a folder to add any new files automatically. However, I was frustrated that it didn't provide a simple means to automatically (or at least, quickly) downloaded new exercises from Garmin and this would have to be done manually via the Garmin Connect website.
I noticed that [CyberJunky](https://github.com/cyberjunky/python-garminconnect) had written python code that allowed you to access and download FIT files using the Garmin API so I have taken some of the example code the provide to create my own script. This wasn't, however until I'd downloaded my entire history directly from Garmin via an information request (have a look here: https://www.garmin.com/en-US/account/datamanagement/)

For that reason I have added the following functionality:
* Simple JSON database of all sessions in system (date of exercise, type of exercise, duration of exercise, distance of exercise)
* Query Garmin API to download exercises occuring after last date in database
* Ability to add existing exercises to database stored as zipped .fit files (If you have already have some downloaded)
* Ability to ask Garmin API for all stored exercises (not sure what time limit is on this query)

## Operation
The main script is stored in *Get_Fit_files.py*, the class defining previously saved sessions is in *fit_sessions.py*. The **fit_sessions** class stores some simple data about previously stored exercises as a list of a dictionary object, saving it as *.json*.

On running *Get_Fit_files.py* you will be prompted for your Garmin username and password on the first use. It also has the ability to save these as environment variables if you are happy to do so. CyberJunky's original code also saves the login session in Json so you can log back in without prompt for a day or so. On successful login (I had issues with 403 errors from my home WiFi for some reason but a VPN sorted this) you will be greeted with a menu
```python
menu_options = {
    "1": "Update stored sessions from .fit files",
    "2": f"Get sessions from api between {latest_session_display} and {today_display}",
    "3": "Attempt to get all sessions from api",
    "q": "Quit menu"
    }
```
### Update stored sessions from .fit files
If you have any existing *.fit* files (stored as a zip file) you can put them in the **FITzips** folder, you can have multiple *.fit* files in a single zip. When I downloaded all data from Garmin, many *.fit* files were empty so the  **fit_sessions** will automatically skip empty files and it will also skip exercise sessions already in the database (those that occured at same date-time as one already present).

###Get sessions from api between {latest_session_display} and {today_display}
This will query the API from the last date (+1 day) in the database to today, downloading any new sessions as zip files in the **FITzips** folder, also adding them to the local database.
If there are no existing exercises, this function will query one week prior to today.

### Attempt to get all sessions from api
Query API with maximum possible timeframe, in case you don't have any existing files. I reccomend you try to download all your data from Garmin, I am not sure how far back exercises are accessible via the api.

## Pre-Requisites
The script requires a couple of additional libraries
* [garminconnect](https://pypi.org/project/garminconnect/) -- this has it's own requirements, check the [github repo](https://github.com/cyberjunky/python-garminconnect)
* [fitdecode](https://pypi.org/project/fitdecode/) a library that allows parsing of the .fit files (for adding details to local database)


## sessions.json and session.json
Two *.json* files are saved with this code, the *sessions.json* is the local database of exercises. The *session.json* stored the saved credentials for the Garmin API
