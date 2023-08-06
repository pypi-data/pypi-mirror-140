# -*- coding: utf-8 -*-
import logging
import os

import requests

from transkribus.utils import try_request

logger = logging.getLogger(__name__)


def options_from_env():
    options = {}
    if "TRANSKRIBUS_API_URL" in os.environ:
        options["base_url"] = os.environ["TRANSKRIBUS_API_URL"]
    if "TRANSKRIBUS_EMAIL" in os.environ:
        options["email"] = os.environ["TRANSKRIBUS_EMAIL"]
    if "TRANSKRIBUS_PASSWORD" in os.environ:
        options["password"] = os.environ["TRANSKRIBUS_PASSWORD"]
    return options


class TranskribusAPI(object):
    def __init__(
        self,
        base_url="https://transkribus.eu/TrpServer/rest",
        email=None,
        password=None,
    ):
        self.base_url = base_url
        assert not self.base_url.endswith("/")
        assert self.base_url.startswith("https://")
        self.session = requests.Session()
        if email and password:
            self.login(email, password)

    def request(
        self,
        method,
        endpoint,
        params=None,
        accept="json",
        send="html",
        retries=3,
        cooldown=2.0,
        **data,
    ):
        assert not endpoint.startswith("/")
        assert accept in ("html", "json")
        assert send in ("html", "json")
        url = "{}/{}".format(self.base_url, endpoint)
        headers = {
            "User-Agent": "Arkindex/1.0",
        }

        if accept == "json":
            headers["Accept"] = "application/json"
        elif accept == "html":
            headers["Accept"] = "text/html, text/plain"
        else:
            raise Exception("Unsupported accept {}".format(accept))

        payload = {
            "headers": headers,
            "params": params,
            "data": send == "html" and data,
            "json": send == "json" and data,
        }

        resp = try_request(method, url, **payload)

        content_type = resp.headers.get("Content-Type")
        if content_type is not None and content_type.startswith("application/json"):
            return resp.json()

        return resp.content

    def get(self, *args, **kwargs):
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request(self.session.post, *args, **kwargs)

    def login(self, email, password):
        user = self.post("auth/login", user=email, pw=password)
        logger.info("Logged as {userName} #{userId}".format(**user))
        return user

    def get_collection(self, collection_id):
        return self.get("collections/{}/metadata".format(collection_id))

    def create_collection(self, name):
        assert isinstance(name, str)
        col_id = self.post(
            "collections/createCollection", accept="html", params={"collName": name}
        )
        return col_id.decode("utf-8")

    def update_collection(self, collection_id, name=None, description=None):
        payload = self.get_collection(collection_id)
        if name is not None:
            assert isinstance(name, str)
            payload["colName"] = name
        if description is not None:
            assert isinstance(description, str)
            payload["description"] = description
        return self.post(
            "collections/{}/metadata".format(collection_id), send="json", **payload
        )

    def list_collections(self):
        return self.get("collections/list")

    def load_collection_documents(self, collection_id):
        return self.get("collections/{}/list".format(collection_id))

    def load_document(self, collection_id, document_id):
        return self.get("collections/{}/{}/fulldoc".format(collection_id, document_id))

    def list_user_collection(self, collection_id):
        return self.get("collections/{}/userlist".format(collection_id))

    def start_export(self, collection_id, **payload):
        return int(
            self.post(f"collections/{collection_id}/export", send="json", **payload)
        )

    def get_job(self, job_id):
        return self.get(f"jobs/{job_id}")
