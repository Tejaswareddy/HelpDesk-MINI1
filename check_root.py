import urllib.request, time
for i in range(6):
    try:
        print('root', urllib.request.urlopen('http://127.0.0.1:8000/').status)
        print('health', urllib.request.urlopen('http://127.0.0.1:8000/api/health').read().decode())
        break
    except Exception as e:
        print('wait', i, e)
        time.sleep(1)
