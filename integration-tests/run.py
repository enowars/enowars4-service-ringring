import requests
import json
import os

def run_test_suite():
    url = f"http://{os.environ['SERVICE_HOST']}:7353"
    params = {'state': json.dumps({'mode': 'alarm'}) }
    r = requests.get(url, params)
    print(r.status_code)

if __name__ == "__main__":
    run_test_suite()