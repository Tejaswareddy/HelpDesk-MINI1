import urllib.request, json
print('health')
print(urllib.request.urlopen('http://127.0.0.1:8000/api/health').read().decode())
print('tickets')
print(urllib.request.urlopen('http://127.0.0.1:8000/api/tickets').read().decode())
