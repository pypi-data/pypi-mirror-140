# -*- coding: utf-8 -*-
import json
import logging
import os
import time

import requests
from humanize import naturalsize

from transkribus.utils import try_request

logger = logging.getLogger(__name__)

JOB_POLLING_SECONDS = 5


class Model(object):
    def __init__(self, data):
        # Allow instantiating using the ID directly
        if isinstance(data, int):
            data = {self.KEY: data}

        assert isinstance(data, dict)
        self.data = data
        self.id = data[self.KEY]
        self.directory = None

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

    def build_directory(self, base):
        # Check base folder
        base = os.path.realpath(base)
        assert os.path.isdir(base)
        assert os.access(base, os.W_OK | os.X_OK)

        # Init model directory
        self.directory = os.path.join(base, str(self.id))
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        return self.directory

    def write_json(self, name, payload):
        assert self.directory is not None
        with open(os.path.join(self.directory, "{}.json".format(name)), "w") as f:
            json.dump(payload, f, indent=4, sort_keys=True)

    def download_image(self, url, filename=None, retries=3, cooldown=2.0):
        resp = try_request(requests.get, url, stream=True)
        # TODO: check content type

        if not filename:
            return resp.content

        # Get extension from filename
        # and build new file
        assert self.directory is not None
        _, ext = os.path.splitext(filename)
        path = os.path.join(self.directory, "{}{}".format(self.id, ext.lower()))

        with open(path, "wb") as f:
            for chunk in resp:
                f.write(chunk)

        logger.info("Downloaded image {}".format(path))
        return path

    def download_text(self, url, filename=None):
        resp = try_request(requests.get, url)
        # TODO: check encoding for binary

        if not filename:
            return resp.content

        assert self.directory is not None
        path = os.path.join(self.directory, filename)

        with open(path, "wb") as f:
            f.write(resp.content)

        logger.info("Downloaded text {}".format(path))
        return path

    def download(self, api, output_dir):
        raise NotImplementedError


class Collection(Model):
    KEY = "collectionId"

    def get_documents(self, api):
        return [Document(self, d) for d in api.load_collection_documents(self.id)]

    def download(self, api, output_dir):
        self.build_directory(output_dir)
        logger.info("Syncing collection {} to {}".format(self.id, self.directory))

        for doc in self.get_documents(api):
            logger.info("Sync document {}".format(doc))
            doc.download(api, self.directory)

    def export(self, api, export_params={}):
        return Job(api.start_export(self.id, **export_params))


class Document(Model):
    KEY = "docId"

    def __init__(self, collection, data):
        assert isinstance(collection, Collection)
        self.collection = collection
        super().__init__(data)
        self.base_data = self.data.copy()

    def __str__(self):
        return "{docId} - {title}".format(**self.data)

    def load(self, api):
        self.data.update(api.load_document(self.collection.id, self.id))

    def get_pages(self, api):
        if "pageList" not in self.data:
            self.load(api)
        return [Page(self, p) for p in self["pageList"]["pages"]]

    def download(self, api, output_dir):
        self.build_directory(output_dir)

        for page in self.get_pages(api):
            logger.info("Sync page {}".format(page))
            page.download(api, self.directory)

        # Dump payloads
        self.write_json("base", self.base_data)
        self.write_json("full", self.data)


class Page(Model):
    KEY = "pageId"

    def __init__(self, document, data):
        assert isinstance(document, Document)
        self.document = document
        super().__init__(data)

    def __str__(self):
        return "{pageId} - n°{pageNr}".format(**self.data)

    def get_transcript(self):
        # All the transcripts have a timestamp.
        # The transcript with the largest timestamp is the latest version of the transcripts.
        transcripts = self.data["tsList"]["transcripts"]
        last_transcript = max(transcripts, key=lambda tr: tr["timestamp"])
        return Transcript(self, last_transcript)

    def download(self, api, output_dir):
        self.directory = output_dir

        # Download full size image
        self.download_image(self.data["url"], self.data["imgFileName"])

        # Download transcription
        self.get_transcript().download(api, self.directory)


class Transcript(Model):
    KEY = "tsId"

    def __init__(self, page, data):
        assert isinstance(page, Page)
        self.page = page
        super().__init__(data)

    def __str__(self):
        return "{tsId} - {status} - {nbOfLines} lines".format(**self.data)

    def download(self, api, output_dir):
        self.directory = output_dir
        self.download_text(self.data["url"], "{}.xml".format(self.id))


class Job(Model):
    KEY = "jobId"

    def __str__(self) -> str:
        return "{jobId} - {status} - {description}".format(**self.data)

    @property
    def completion(self) -> float:
        if self.data.get("progress") is None or self.data.get("totalWork") is None:
            return
        # Avoid dividing by zero
        if self.data["totalWork"] == 0:
            return 0.0
        return self.data["progress"] / self.data["totalWork"]

    def refresh(self, api) -> None:
        """
        Reload the job's data from the API.
        """
        self.data = api.get_job(self.id)

    def wait_for_result(self, api, timeout=1800) -> None:
        """
        Poll the API every few seconds until the job has a result URL or until a timeout.
        Raises an exception if the timeout is reached.
        """
        start_time = time.time()
        previous_description, previous_completion = (
            self.data.get("description"),
            self.completion,
        )

        while start_time + timeout > time.time() and not self.data.get("result"):
            time.sleep(JOB_POLLING_SECONDS)
            self.refresh(api)

            # Log status changes
            if (
                self.data.get("description") != previous_description
                or self.completion != previous_completion
            ):
                logger.info(
                    f'Job {self.id} ({int(self.completion * 100)}%): {self["description"]}'
                )
                previous_description, previous_completion = (
                    self.data.get("description"),
                    self.completion,
                )

        assert self.data.get(
            "result"
        ), f"Timed out while waiting for a result from job {self.id}"

    def download_result(self, destination) -> None:
        assert self.data.get("result"), "Job has no result URL"
        resp = try_request(requests.get, self.data["result"], stream=True)

        size = int(resp.headers["Content-Length"])
        logger.info(f"Downloading {naturalsize(size)}")

        downloaded, last_percent = 0, 0
        with open(destination, "wb") as f:
            # Save the file in 1MB chunks
            for chunk in resp.iter_content(chunk_size=1024 ** 2):
                f.write(chunk)
                downloaded += len(chunk)

                # Log only when the percentage changes
                percent = int((downloaded / size) * 100)
                if percent != last_percent:
                    last_percent = percent
                    logger.info(
                        f"Downloaded {naturalsize(downloaded)} / {naturalsize(size)} ({percent}%)"
                    )
