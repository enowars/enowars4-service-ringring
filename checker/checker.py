import enochecker
import random
import json
from requests import exceptions
import string


class RingRingChecker(enochecker.BaseChecker):
    port = 8000

    def __init__(self):
        super().__init__()
        # TODO: only one flag for now, need to add noise and havocs
        port = 8003
        flag_count = 1
        noise_count = 0
        havoc_count = 0
        service_name = "ringring"

    def putflag(self):
        self.logger.debug("Putting Flag...")
        try:
            response = self.http_get(route='/')
            session_id = response.cookies.get('session_id')

            self.logger.debug("Service main page is reachable.")
        except exceptions.RequestException:
            self.logger.debug("Service not reachable.")
            raise enochecker.OfflineException()

        enochecker.assert_equals(200, response.status_code, "Service not reachable")

        try:
            self.http_get(route="/make_me_a_vip")
            self.logger.debug("Session is now a vip.")
        except Exception:
            self.logger.debug("Cannot make the session a vip.")
            raise enochecker.BrokenServiceException()

        # set alarm with flag as text
        payload = {'state': json.dumps(
            {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}",
             'msg': self.flag})}

        try:
            response = self.http_get("/get_bot_response", params=payload)
        except exceptions.RequestException:
            self.logger.debug(f"Could not place flag. \nFlag: {self.flag}. \nPayload: {payload}")
            raise enochecker.BrokenServiceException("/AddAttack failed")

        enochecker.assert_in(self.flag, response.text,
                             "Could not place flag. \nFlag: {self.}. \nPayload: {payload}")
        self.logger.debug("Flag {} up.".format(self.flag))
        self.team_db[self.flag] = (session_id,)

    def getflag(self):
        try:
            (session_id,) = self.team_db[self.flag]
        except KeyError:
            return enochecker.Result.MUMBLE
        cookies = {'session_id': session_id[0]}
        req = self.http_get("/alarm", cookies=cookies)
        enochecker.assert_equals(200, req.status_code, "Alarm page is down.")
        enochecker.assert_equals(self.flag, req.text, "Flas is missing!")

    def putnoise(self):
        self.logger.debug("Putting Noise...")
        try:
            response = self.http_get(route='/')
            session_id = response.cookies.get('session_id')

            self.logger.debug("Service main page is reachable.")
        except exceptions.RequestException:
            self.logger.debug("Service not reachable.")
            raise enochecker.OfflineException()

        enochecker.assert_equals(200, response.status_code, "Service not reachable")

        try:
            assert session_id
        except AssertionError:
            raise enochecker.BrokenServiceException("session_id is not set.")

        alarm_message = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(50)])
        payload = {'state': json.dumps(
            {'mode': 'alarm', 'alarm_time': f"{random.randint(0, 23)}:{random.randint(0, 59)}",
             'msg': alarm_message})}

        try:
            response = self.http_get("/get_bot_response", params=payload)
        except exceptions.RequestException:
            self.logger.debug(f"Could not place flag. \nFlag: {self.flag}. \nPayload: {payload}")
            raise enochecker.BrokenServiceException("/Put noise failed")

        enochecker.assert_in(alarm_message, response.text,
                             "Could not place flag. \nFlag: {self.}. \nPayload: {payload}")
        self.logger.debug("Flag {} up.".format(self.flag))
        # TODO: how to store the noise in the db?
        # TODO: how many noise calls are made per tick?
        # self.team_db[self.flag] = (session_id,)

    def getnoise(self):
        pass

    def havoc(self):
        pass

    def exploit(self):
        pass


app = RingRingChecker.service

if __name__ == "__main__":
    enochecker.run(RingRingChecker)
