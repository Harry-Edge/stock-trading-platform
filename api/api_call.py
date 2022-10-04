import requests
import time

url = 'http://localhost:8000/api/v1/generate-dummy-stock-data/'


def call_api_to_update():
    response = requests.get(url)
    print(response.json())


while True:
    call_api_to_update()
    time.sleep(2)
