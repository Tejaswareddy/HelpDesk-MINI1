import time, urllib.request
for i in range(10):
    try:
        r=urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)
        print('OK', r.read().decode())
        break
    except Exception as e:
        print('wait', i, e)
        time.sleep(1)
