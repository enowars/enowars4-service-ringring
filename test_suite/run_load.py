import threading
import grequests
from service_handler import call_bot_response, init_user, get_invoices, make_vip
import random
import string
import json
import time
import logging

MIN_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD = 5
MAX_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD = 10
NUMBER_OF_THREADS = 80

logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("grequests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("gevent").setLevel(logging.CRITICAL)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def thread_run(number_of_items):
    try:
        init_requs = []
        put_requests = []
        sessions = []
        for _ in range(number_of_items):
            request, session = init_user()
            init_requs.append(request)
            sessions.append(session)
        responses = grequests.map(init_requs)

        vip_requests = []
        for index, response in enumerate(responses):
            if response.status_code != 200:
                print("###############")
                print("request did not return successfully")
                print(response.text)

            vip_requests.append(make_vip(sessions[index]))
        responses = grequests.map(vip_requests)


        for index, response in enumerate(responses):
            if response.status_code != 200:
                print("###############")
                print("request did not return successfully")
                print(response.text)

            payload = {'msg': get_random_string(50),
                    'state': json.dumps({'mode': 'food_order', 'order_step': '2', 'order': 'bred'})}
            put_requests.append(call_bot_response(payload, sessions[index]))
        responses = grequests.map(put_requests)

        get_requests = []
        for index, response in enumerate(responses):
            if response.status_code != 200:
                print("###############")
                print("request did not return successfully")
                print(response.text)

            get_requests.append(get_invoices(sessions[index]))

        responses = grequests.map(get_requests)


    except Exception as e:
        print("##################################")
        print(str(e))


if __name__ == '__main__':
    while True:
        threads = []
        print('---------------------')
        print("NEW ROUND")
        print('---------------------')
        try:
            for _ in range(NUMBER_OF_THREADS):
                number_of_requests = random.choice(
                    range(MIN_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD, MAX_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD))
                print(f"starting thread with {number_of_requests} requests")
                thread = threading.Thread(target=thread_run, args=(number_of_requests,))
                print("started thread")
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            break

