import logging

import requests

logger = logging.getLogger(__name__)


class SlackPostMessageError(Exception):
    pass


class Slack:
    def __init__(self, host: str, channel: str):
        self.host = host
        self.channel = channel

    def alert(self, messages: str):
        try:
            requests.post(url=f"{self.host}/{self.channel}", data=messages)
        except Exception as e:
            msg = f"could not send slack alert: {str(e)}"
            logger.exception(msg)
            raise SlackPostMessageError(msg)
