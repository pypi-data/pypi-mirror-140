import json
import requests

def get_data() -> dict:
    # First we get the IP using a simple request
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    # Then we use that ip to get info about the user
    location: dict = requests.get(f'https://ipinfo.io/{ip}?token=0685828d875309').json()

    return location
