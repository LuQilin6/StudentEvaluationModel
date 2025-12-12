import time
import requests
import json
import threading
import re

# Replace this string with the specific API address provided by your institution or service.
url = "YOUR_API_ENDPOINT_HERE"

headers = {
    "Content-Type": "application/json",
    "Authorization": "YOUR_ACCESS_TOKEN_HERE" # Replace the string below with your unique access token/API key.
}

data = {
    "model": "gpt-4-0613",
    "messages": [{"role": "system", "content": "Hello"},
                 {"role": "user", "content": "Hello"}],
    "max_tokens": 2048,
    "temperature": 0.0
}

new_data = []

def request():
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data)).json()
        response = response['choices'][0]['message']['content']
        print(response)
    except Exception as e:
        print(e)
        time.sleep(3)

if __name__ == "__main__":
    threads = []
    for i in range(3):
        thread = threading.Thread(target=request)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
