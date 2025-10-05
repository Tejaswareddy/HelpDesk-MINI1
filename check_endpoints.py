import urllib.request, json
print('health ->')
try:
    print(urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5).read().decode())
except Exception as e:
    print('ERROR', e)
print('tickets ->')
try:
    print(urllib.request.urlopen('http://127.0.0.1:8000/api/tickets', timeout=5).read().decode())
except Exception as e:
    print('ERROR', e)
