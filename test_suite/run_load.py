import threading
import grequests
from service_handler import call_bot_response, init_user, get_invoices
import random
import string
import json

MIN_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD = 100
MAX_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD = 200
NUMBER_OF_THREADS = 10


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def thread_run(number_of_items):
    init_requs = []
    put_requests = []
    sessions = []
    for _ in range(number_of_items):
        request, session = init_user()
        init_requs.append(request)
        sessions.append(session)
    responses = grequests.map(init_requs)

    for index, response in enumerate(responses):
        payload = {'msg': get_random_string(50),
                   'state': json.dumps({'mode': 'food_order', 'order_step': '2', 'order': 'bred'})}
        put_requests.append(call_bot_response(payload, sessions[index]))
    responses = grequests.map(put_requests)

    get_requests = []
    for index, response in enumerate(responses):
        get_requests.append(get_invoices(sessions[index]))

    responses = grequests.map(get_requests)


if __name__ == '__main__':
    threads = []
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
