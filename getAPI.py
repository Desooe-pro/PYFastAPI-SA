import requests

URL = "http://127.0.0.1:8000/search"

res = requests.get(URL)

print('status : ', res.text)