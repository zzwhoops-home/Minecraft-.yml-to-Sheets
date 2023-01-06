from __future__ import print_function
import shutil
import regex
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint
from googleapiclient import discovery

# source and destination location for to copy stats file.
src = "C:\\Users\\Zachary Deng\\Desktop\\Servers\\Factions Server\\plugins\\KitPvP\\stats.yml"
dst = "C:\\Users\\Zachary Deng\\Desktop\\Zach's Stuff\\Python\\Projects\\Factions Server"
#classes = ["Knight","Archer","Assassin","Tank","Pyromancer","Strongman","AquaticWarrior","IceMage","Heavy","CrossbowMaster","Lumberjack","Elementalist","Medic","Pirate"]
players = {}

# copy stats file from faction server directory to current directory
shutil.copy(src, dst)

# open stats file
stats = open((dst + "\\stats.yml"), "r+").read()

# generate list of users, kills, and deaths
users = regex.findall("(?:Username: )\\K\\w+", stats)
kills = regex.findall("(?:Kills: )\\K\\w+", stats)
deaths = regex.findall("(?:Deaths: )\\K\\w+", stats)

# sheet ID and edit range
sheetID = ''
sheetRange = 'Leaderboard Data!A2:D'

# create dictionary of player stats
for x in range(len(users)):
    try:
        players[users[x]] = [kills[x], deaths[x], round(float(kills[x]) / float(deaths[x]), 2)]
    except ZeroDivisionError:
        players[users[x]] = [kills[x], 0, 0]
"""
with open("stats_extracted.txt", "w") as new_stats:
    for x in range(len(players)):
        new_stats.writelines("Player: " + str(players.keys()[x]) + " Kills: " + str(players.values()[x][0]) + " Deaths: " + str(players.values()[x][1]) + " K/D: " + str(players.values()[x][2]) + "\n")
"""

# generate credentials or something
def main():
    for x in range(2):
        try:
            creds = None
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            # return credentials
            return creds
        except:
            print("Invalid credentials or some stupid shit with Sheets API, try again")
            os.remove("token.pickle")
            main()
        x += 1

# write player stats to google sheets
def write_stats(creds, stats):
    service = discovery.build('sheets', 'v4', credentials=creds)

    values = [
        # Additional rows
    ]
    for x in stats:
        values.append([x, stats[x][0], stats[x][1], stats[x][2]])
    data = [
        {
            'range': sheetRange,
            'values': values
        }
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': "USER_ENTERED",
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(spreadsheetId=sheetID, body=body).execute()
    values = result.get('values', [])
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


if __name__ == '__main__':
    main()

write_stats(main(), players)