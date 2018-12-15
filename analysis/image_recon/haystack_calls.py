import requests

r = requests.post(
  "https://api.haystack.ai/api/image/analyze?output=json&apikey=61a168d9226cdbe8149673952926a2ff",
  data=open('x.jpeg', 'rb'))
print(r.text)