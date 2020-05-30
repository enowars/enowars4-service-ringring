import enochecker
import random
import json
from requests import exceptions
import string


class RingRingChecker(enochecker.BaseChecker):
    port = 7353
    flag_count = 2
    noise_count = 10
    havoc_count = 0
    service_name = "ringring"

    def putflag(self):
        session_id = self.init_user()

        if self.flag_idx % 2 == 0:
            payload = {'state': json.dumps(
                {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}"}),
                'msg': self.flag}
            self.call_bot_response(payload, mode='alarm flag')

            payment_payload = {'state': json.dumps({'mode': 'alarm', 'payment': 'pending'}),
                               'msg': random.choice(['room-bill', 'now'])}
            self.call_bot_response(payment_payload, mode='alarm flag payment', message_in_response=False)

        else:
            payload = {'msg': self.flag,
                       'state': json.dumps({'mode': 'food_order', 'order_step': '2', 'order': 'bred'})}
            self.call_bot_response(payload, mode='invoice flag')

        self.logger.debug("Flag {} up.".format(self.flag))
        self.team_db[self.flag] = (session_id,)

    def getflag(self):
        if self.flag_idx % 2 == 0:
            try:
                session_id = self.team_db[self.flag]
                self.logger.debug(f"Getting flag for session_id {session_id[0]}")
            except KeyError:
                return enochecker.Result.MUMBLE

            self.http_session.cookies.set('session_id', session_id[0])
            self.logger.debug(self.http_session.cookies.get('session_id'))

            req = self.http_get("/alarm")
            self.logger.debug(req.text)
            enochecker.assert_equals(200, req.status_code, "Alarm page is down.")
            enochecker.assert_in(self.flag, req.text, "Flag is missing!")
        else:
            # TODO allow checker to access the / enpoint of the invoice app directly (not through the bot app)
            pass

    def putnoise(self):
        self.logger.debug(self.noise)
        if self.flag_idx % 2 == 0:
            self.logger.debug("Putting Noise...")
            session_id = self.init_user()

            try:
                assert session_id
            except AssertionError:
                raise enochecker.BrokenServiceException("session_id is not set.")

            payload = {'msg': self.noise, 'state': json.dumps(
                {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}"})}

            self.call_bot_response(payload, mode='alarm noise')

            payment_payload = {'state': json.dumps({'mode': 'alarm', 'payment': 'pending'}),
                               'msg': random.choice(['room-bill', 'now'])}
            self.call_bot_response(payment_payload, mode='alarm noise payment', message_in_response=False)
        else:
            session_id = self.init_user()

        self.team_db[self.noise] = (session_id,)

    def getnoise(self):
        pass

    def havoc(self):
        pass

    def exploit(self):
        pass
        # self.team_db[self.flag] = (session_id,)

    def init_user(self):
        self.http_session.cookies.set('session_id', None)
        try:
            response = self.http_get(route='/')
            session_id = response.cookies.get('session_id')
            self.logger.debug("Service main page is reachable.")
        except exceptions.RequestException:
            self.logger.debug("Service not reachable.")
            raise enochecker.OfflineException()
        enochecker.assert_equals(200, response.status_code, "Service not reachable")
        return session_id

    def call_bot_response(self, payload, mode, message_in_response=True):
        self.logger.debug(f"Putting {mode}...")
        try:
            response = self.http_get("/get_bot_response", params=payload)
        except exceptions.RequestException:
            self.logger.debug(f"Could not get bot response. Payload: {payload}")
            raise enochecker.BrokenServiceException("/AddAttack failed")

        if message_in_response:
            enochecker.assert_in(payload['msg'], response.text,
                                 f"Could not find message in bot response. Payload: {payload}. Reponse: {response.text}")


app = RingRingChecker.service

if __name__ == "__main__":
    enochecker.run(RingRingChecker)
