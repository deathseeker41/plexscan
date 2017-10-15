import requests
import urllib3
import sys
import argparse
import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = ConfigParser.ConfigParser()
config.read('plexscan.ini')

PLEX_SERVER=config.get('global', 'server').strip('"')
API_TOKEN=config.get('global', 'token').strip('"')

HD_FORMATS=('1080', '720')

parser = argparse.ArgumentParser()
parser.add_argument('library', type=str)
parser.add_argument('action', type=str, choices=['hdscan'])
args = parser.parse_args()

headers = {'Accept': 'application/json',
           'X-Plex-Token': API_TOKEN}

r = requests.get("{}/library/sections".format(PLEX_SERVER), headers=headers, verify=False)
library_list = []
for library in r.json()['MediaContainer']['Directory']:
    if args.library in library['title']:
        print "Found Library: {}".format(library['title'])
        library_list.append(library['key'])

if not library_list:
    print "No matching libraries found."
    sys.exit(1)

for library_id in library_list:
    r2 = requests.get("{}/library/sections/{}/all".format(PLEX_SERVER,library_id), headers=headers, verify=False)
    if r2.json()['MediaContainer']['viewGroup'] == "show":
        for show in r2.json()['MediaContainer']['Metadata']:
            r3 = requests.get("{}{}".format(PLEX_SERVER,show['key']), headers=headers, verify=False)
            for season in r3.json()['MediaContainer']['Metadata']:
                r4 = requests.get("{}{}".format(PLEX_SERVER,season['key']), headers=headers, verify=False)
                for episode in r4.json()['MediaContainer']['Metadata']:
                    if episode['Media'][0]['videoResolution'] not in HD_FORMATS:
                        print "{} - S{}E{} is not HD: {}".format(show['title'], str(season['index']).zfill(2), str(episode['index']).zfill(2), episode['Media'][0]['videoResolution'])
    elif "movie":
        for movie in r2.json()['MediaContainer']['Metadata']:
            if movie['Media'][0]['videoResolution'] not in HD_FORMATS:
                print "{} is not HD: {}".format(movie['title'], movie['Media'][0]['videoResolution'])
    else:
        print "Unknown library type"
