import os
import logging
import sys
import requests
from time import sleep


log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname).4s %(name)s: \
                            %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class CircuitStates:
    OPEN = "open"
    CLOSED = "closed"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, http_client, error_threshold, time_window):
        """
        Description:


        Args:
            http_client (string): _description_
            error_threshold (int): treshold of failed attempts to identify the circuit as opened
            time_window (int): time window between remote calls
        """

        self.http_client = http_client
        self.error_threshold = error_threshold
        self.time_window = int(time_window)
        self.state = CircuitStates.CLOSED
        self._failure_count = 0
        self._success_count = 0

        if ACCEPT_CLIENT_ERRORS == True:
            self.ERROR_LIMIT = 499
        else:
            self.ERROR_LIMIT = 399

    def set_state(self, state):
        previous_state = self.state
        self.state = state
        if previous_state != state:
            log.info(f"Circuit changed from {previous_state} to {self.state}")

    def get_statuscode(self, HTTP_CLIENT):
        try:
            response = s.get(f"http://{HTTP_CLIENT}").status_code
            return response
        except requests.exceptions.ConnectionError:
            response = requests.codes.unavailable
            return response

    def closed_state(self, *args, **kwargs):

        response = self.get_statuscode(HTTP_CLIENT)

        if response in range(200, self.ERROR_LIMIT):
            log.info("Remote Call Succeded")
            log.debug(f"Connection to {HTTP_CLIENT} returned status code {response}")
            self._failure_count = 0
            return response

        else:
            log.debug(f"Connection to {HTTP_CLIENT} returned status code {response}")
            self._failure_count += 1
            log.error(
                f"Circuit Open Error - Remote Call has failed for {self._failure_count} consecutive times."
            )
            if self._failure_count >= self.error_threshold:
                self.set_state(CircuitStates.OPEN)

    def open_state(self, *args, **kwargs):

        try:
            response = self.get_statuscode(HTTP_CLIENT)
            if response in range(200, self.ERROR_LIMIT):
                self.set_state(CircuitStates.HALF_OPEN)
                self._success_count += 1
                log.info(
                    f"Remote Call has succeeded for {self._success_count} consecutive times."
                )
                if self._success_count > self.error_threshold:
                    self._success_count = 0
                    self.set_state(CircuitStates.CLOSED)
                    return response
            else:
                self._failure_count += 1
                log.error(
                    f"Circuit Open Error - Remote Call has failed for {self._failure_count} consecutive times."
                )
                self.set_state(CircuitStates.OPEN)
                return response
        except Exception as e:
            log.error(e)

    def do_request(self, *args, **kwargs):
        if self.state == CircuitStates.CLOSED:
            return self.closed_state(*args, **kwargs)
        else:
            return self.open_state(*args, **kwargs)


if __name__ == "__main__":

    try:
        HTTP_CLIENT = os.environ["HTTP_CLIENT"]
        ERROR_THRESHOLD = os.getenv("ERROR_THRESHOLD", 3)
        TIME_WINDOW = os.getenv("TIME_WINDOW", 10)
        ACCEPT_CLIENT_ERRORS = os.getenv("ACCEPT_CLIENT_ERRORS", False)

    except KeyError as e:
        log.error(f"The Environment Variable {e} is not set")
        sys.exit(1)

    s = requests.session()
    log.info("starting")
    breaker = CircuitBreaker(HTTP_CLIENT, ERROR_THRESHOLD, TIME_WINDOW)

    while True:
        breaker.do_request(HTTP_CLIENT)
        log.debug(f"Retrying in {TIME_WINDOW} seconds.")
        sleep(int(TIME_WINDOW))
