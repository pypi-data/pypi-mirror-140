# -*- coding: utf-8 -*-
import logging
import time

from requests import HTTPError, RequestException

logger = logging.getLogger(__name__)


def try_request(method, *args, retries=3, cooldown=2.0, **kwargs):
    try:
        resp = method(*args, **kwargs)
        resp.raise_for_status()
        return resp
    except RequestException as e:
        if isinstance(e, HTTPError):
            msg = "HTTP error {}: {}".format(
                e.response.status_code,
                e.response.content.decode("utf-8"),
            )
        else:
            msg = str(e)

        if retries <= 1:
            raise Exception(msg)

        logger.warning(msg)
        logger.debug("Waiting for {:.2f} seconds before retrying".format(cooldown))
        time.sleep(cooldown)
        return try_request(
            method, *args, retries=retries - 1, cooldown=cooldown * 2, **kwargs
        )
