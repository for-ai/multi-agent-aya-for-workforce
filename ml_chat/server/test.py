import requests
import json

post_url = "http://localhost:8000/process"
get_url = "http://localhost:8000/"

# Sends the message from a given user to the workflow
headers = {'Content-Type': 'application/json'}
data = {"sender": "TeamA","message":"Hey there! is everything good"}

response = requests.post(post_url, data=json.dumps(data), headers=headers)
print(response.json())


# Retrieves the latest message sent to all users
response= requests.get(get_url) 

print(response.json())
