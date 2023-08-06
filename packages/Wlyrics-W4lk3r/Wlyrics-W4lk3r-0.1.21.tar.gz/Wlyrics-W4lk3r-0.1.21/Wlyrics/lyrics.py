import json
import requests

def ly(singer, song):
    r = requests.get("https://api.lyrics.ovh/v1/" + singer + "/" + song)
    j = json.loads(r.text)
    if str(j['lyrics']):
       print(str(j['lyrics']))
    else:
        print("Unknown singer or song name!!")

