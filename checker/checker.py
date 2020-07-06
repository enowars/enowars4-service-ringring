import enochecker
import random
import json
from requests import exceptions
import re

AVAILABLE_FOOD = ['pizza', 'bred', 'fish']


class RingRingChecker(enochecker.BaseChecker):
    port = 7353
    flag_count = 2
    noise_count = 2
    havoc_count = 0
    service_name = "ringring"

    def putflag(self):
        session_id = self.init_user(make_vip=True)

        if self.flag_idx % 2 == 0:
            payload = {'state': json.dumps(
                {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}"}),
                'msg': self.flag}
            self.call_bot_response(payload, mode='alarm flag')

            payment_payload = {'state': json.dumps({'mode': 'alarm', 'payment': 'pending'}),
                               'msg': random.choice(['room-bill', 'now'])}
            self.call_bot_response(payment_payload, mode='alarm flag payment')
            self.team_db[self.flag] = (session_id,)

        else:
            payload = {'msg': self.flag,
                       'state': json.dumps({'mode': 'food_order', 'order_step': '2', 'order': 'bred'})}
            message = self.call_bot_response(payload, mode='invoice flag')
            invoice_number = re.findall('invoice number is (\d*)', message)
            if len(invoice_number) != 1:
                return enochecker.Result.MUMBLE
            else:
                invoice_number = invoice_number[0]
            self.team_db[self.flag] = (session_id, invoice_number)

        self.logger.debug("Flag {} up.".format(self.flag))

    def getflag(self):
        try:
            db_row = self.team_db[self.flag]
            self.logger.debug(f"Getting flag for session_id {db_row[0]}")
        except KeyError:
            return enochecker.Result.MUMBLE

        if self.flag_idx % 2 == 0:
            self.check_alarm(self.flag, db_row[0])
        else:
            self.check_invoice_number(db_row[1], db_row[0], self.flag)

    def putnoise(self):
        self.logger.debug(f"Putting Noise {self.noise} ...")
        session_id = self.init_user()

        try:
            assert session_id
        except AssertionError:
            raise enochecker.BrokenServiceException("session_id is not set.")

        if self.flag_idx % 2 == 0:
            payload = {'msg': self.noise, 'state': json.dumps(
                {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}"})}

            self.call_bot_response(payload, mode='alarm noise')

            payment_payload = {'state': json.dumps({'mode': 'alarm', 'payment': 'pending'}),
                               'msg': random.choice(['room-bill', 'now'])}
            self.call_bot_response(payment_payload, mode='alarm noise payment')
            self.team_db[self.noise] = (session_id,)

        else:
            payload = {'msg': self.noise,
                       'state': json.dumps(
                           {'mode': 'food_order', 'order_step': '2', 'order': random.choice(AVAILABLE_FOOD)})}
            message = self.call_bot_response(payload, mode='invoice noise')
            invoice_number = re.findall('invoice number is (\d*)', message)
            if len(invoice_number) != 1:
                return enochecker.Result.MUMBLE
            else:
                invoice_number = invoice_number[0]
            self.team_db[self.noise] = (session_id, invoice_number)

    def getnoise(self):
        try:
            db_row = self.team_db[self.noise]
            self.logger.debug(f"Getting noise for session_id {db_row[0]}")
        except KeyError:
            return enochecker.Result.MUMBLE

        if self.flag_idx % 2 == 0:
            self.check_alarm(self.noise, db_row[0])
        else:
            self.check_invoice_number(db_row[1], db_row[0], self.noise)

    def havoc(self):
        pass

    def exploit(self):
        pass

    def init_user(self, make_vip=False):
        self.http_session.cookies.set('session_id', None)
        try:
            response = self.http_get(route='/')
            session_id = response.cookies.get('session_id')
            self.logger.debug("Service main page is reachable.")
        except exceptions.RequestException:
            self.logger.debug("Service not reachable.")
            raise enochecker.OfflineException()
        enochecker.assert_equals(200, response.status_code, "Service not reachable")

        if make_vip:
            self.http_post(route='/make_me_a_vip')

        return session_id

    def call_bot_response(self, payload, mode):
        self.logger.debug(f"Putting {mode}...")
        try:
            response = self.http_get("/get_bot_response", params=payload)
        except exceptions.RequestException:
            self.logger.debug(f"Could not get bot response. Payload: {payload}")
            raise enochecker.BrokenServiceException("/AddAttack failed")

        return response.text

    def check_alarm(self, alarm_text, session_id):
        self.http_session.cookies.set('session_id', session_id)

        req = self.http_get("/alarm")
        enochecker.assert_equals(200, req.status_code, "Alarm page is down.")
        enochecker.assert_in(alarm_text, req.text, f"Cannot find alarm text {alarm_text} in resonse.")

    def check_invoice_number(self, invoice_number, session_id, expected_text):
        self.http_session.cookies.set('session_id', session_id)
        payload = {'state': json.dumps({'mode': 'invoice_info'}),
                   'msg': invoice_number}
        try:
            req = self.http_get('/get_bot_response', params=payload)
        except exceptions.RequestException:
            self.logger.debug(f"Could not get bot response. Payload: {payload}")
            raise enochecker.BrokenServiceException("/AddAttack failed")
        enochecker.assert_equals(200, req.status_code, "Could not get invoice information.")
        data = req.json()
        enochecker.assert_in(expected_text, data['response'].replace('\\u200d', '\u200d'),
                             f"Could not find expected invoice text {expected_text} in response {data['response']}.")


app = RingRingChecker.service

if __name__ == "__main__":
    enochecker.run(RingRingChecker)
