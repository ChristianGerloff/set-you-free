import os
from random import choice

import requests
from requests import Response

from set_you_free.backend.findpapers.data.user_agents import USER_AGENTS
from set_you_free.backend.findpapers.utils.common_utils import ThreadSafeSingletonMetaclass


class DefaultSession(requests.Session, metaclass=ThreadSafeSingletonMetaclass):
    def __init__(self, *args, **kwargs) -> None:
        super(DefaultSession, self).__init__()

        proxy = os.getenv("FINDPAPERS_PROXY")

        if proxy:
            self.proxies = {"http": proxy, "https": proxy}

        self.headers.update({"User-Agent": choice(USER_AGENTS)})
        self.default_timeout = 20

    def request(self, method: str, url: str, **kwargs) -> Response:
        kwargs["timeout"] = kwargs.get("timeout", self.default_timeout)

        try:
            response: Response = super().request(method, url, **kwargs)
        except Exception:
            response = requests.Response()
            response.status_code = 500

        if not response.ok and ("http" in self.proxies or "https" in self.proxies):
            # if the response is not ok using proxies,
            # let's try one more time without using them
            kwargs["proxies"] = {
                "http": None,
                "https": None,
            }
            response = super().request(method, url, **kwargs)

        return response
