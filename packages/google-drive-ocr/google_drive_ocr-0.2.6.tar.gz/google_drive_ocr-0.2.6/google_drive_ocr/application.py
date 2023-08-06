#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google OCR Application
======================

Create a project on Google Cloud Platform
-----------------------------------------

Wizard: https://console.developers.google.com/start/api?id=drive

**Instructions**:

* https://cloud.google.com/genomics/downloading-credentials-for-api-access
* Select application type as "Installed Application"
* Create credentials OAuth consent screen --> OAuth client ID
* Save client_secret.json

References
----------

* https://developers.google.com/api-client-library/python/start/get_started
* https://developers.google.com/drive/v3/reference/
* https://developers.google.com/drive/v3/web/quickstart/python
"""

###############################################################################


import io
import os
import time
import enum
import logging
import mimetypes
import multiprocessing as mp
from dataclasses import dataclass, field

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from natsort import natsorted

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

###############################################################################

from .errors import retry

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################

SCOPES = ["https://www.googleapis.com/auth/drive"]

###############################################################################


class Status(enum.Enum):
    SUCCESS = "Done!"
    ALREADY = "Already done!"
    ERROR = "Something went wrong!"

###############################################################################


@dataclass
class GoogleOCRApplication:
    """
    Google OCR Application

    Perform OCR using Google-Drive API v3
    """
    client_secret: str
    upload_folder_id: str = field(default=None)
    ocr_suffix: str = field(default=".google.txt")
    temporary_upload: bool = field(default=False)

    credentials_path: str = field(default=None, repr=False)
    scopes: str = field(default=None)

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = SCOPES

        if self.credentials_path is None:
            self.credentials_path = os.path.join(
                os.path.expanduser("~"), ".credentials", "token.json"
            )
        if self.upload_folder_id is None:
            self.upload_folder_id = "root"
        creds = self.get_credentials()
        self.drive_service = build("drive", "v3", credentials=creds)

    def get_output_path(self, img_path: str) -> str:
        """Get the output path

        Output path is constructed by replacing the extension
        in :code:`img_path` with :code:`ocr_suffix`

        Parameters
        ----------
        img_path : str
            Path to the input image file

        Returns
        -------
        str
            Output path
        """
        _img_path, _ = os.path.splitext(img_path)
        return f"{_img_path}{self.ocr_suffix}"

    def get_credentials(self) -> Credentials:
        """Get valid user credentials

        If no (valid) credentials are available,
        * Log the user in
        * Store the credentials for future use

        Returns
        -------
        Credentials or None
            Valid user credentials
        """
        if os.path.isfile(self.credentials_path):
            creds = Credentials.from_authorized_user_file(
                self.credentials_path, self.scopes
            )
        else:
            credential_dir = os.path.dirname(self.credentials_path)
            os.makedirs(credential_dir, exist_ok=True)
            creds = None

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file=self.client_secret,
                    scopes=self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            LOGGER.info(f"Storing credentials to {self.credentials_path}")
            with open(self.credentials_path, "w") as token:
                token.write(creds.to_json())

        return creds

    # ----------------------------------------------------------------------- #
    # Drive Actions

    @retry()
    def upload_image_as_document(self, img_path: str) -> str:
        """Upload an image file as a Google Document

        Parameters
        ----------
        img_path : str
            Path to the image file

        Returns
        -------
        str
            ID of the uploaded Google document
        """
        img_filename = os.path.basename(img_path)
        mimetype, _encoding = mimetypes.guess_type(img_path)

        if mimetype is None:
            LOGGER.warning("MIME type of the image could not be inferred.")
            mimetype = "image/png"

        file_metadata = {
            "name": img_filename,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [self.upload_folder_id],
        }

        media = MediaFileUpload(img_path, mimetype=mimetype)
        file = self.drive_service.files().create(
            body=file_metadata, media_body=media, fields="id, name"
        ).execute()
        file_id = file.get("id")
        file_name = file.get("name")
        LOGGER.info(f"File uploaded: '{file_name}' (id: '{file_id}')")
        return file_id

    @retry()
    def download_document_as_text(self, file_id: str, output_path: str):
        """Download a Google Document as text

        Parameters
        ----------
        file_id : str
            ID of the Google document
        output_path : str
            Path to where the document should be downloaded
        """
        request = self.drive_service.files().export_media(
            fileId=file_id, mimeType="text/plain"
        )
        fh = io.FileIO(output_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        LOGGER.info(f"Document downloaded: '{output_path}'.")

    @retry()
    def delete_file(self, file_id: str):
        """Delete a file from Google Drive

        Parameters
        ----------
        file_id : str
            ID of the file on Google Drive to be deleted
        """
        self.drive_service.files().delete(fileId=file_id).execute()
        LOGGER.info(f"File '{file_id}' deleted from Google Drive.")

    def perform_ocr(self, img_path: str, output_path: str = None) -> Status:
        """
        Perform OCR on a single image

        * Upload the image to Google Drive as google-document
        * [Google adds OCR layer to the image]
        * Download the google-document as plain text

        Parameters
        ----------
        img_path: str or Path
            Path to the image file
        output_path: str or Path, optional
            Path where the OCR text should be stored
            If None, a new file will be created beside the image
            The default is None.

        Returns
        -------
        status: Status
            Status of the OCR operation
        """
        if output_path is None:
            output_path = self.get_output_path(img_path)

        if os.path.isfile(output_path):
            return Status.ALREADY

        try:
            file_id = self.upload_image_as_document(img_path)
            if file_id:
                self.download_document_as_text(file_id, output_path)

                if self.temporary_upload:
                    self.delete_file(file_id)
            else:
                LOGGER.error(f"Could not upload '{img_path}'.")
                return Status.ERROR
        except Exception:
            LOGGER.exception("An error occurred while performing OCR.")
            return Status.ERROR

        return Status.SUCCESS

    def _worker_ocr_batch(self, worker_arguments: dict) -> float:
        """Worker to perform OCR on multiple files

        Parameters
        ----------
        worker_arguments : dict
            Arguments for the worker

        Returns
        -------
        float
            Time taken in seconds
        """
        process = mp.current_process()
        worker_id = worker_arguments["worker_id"]
        image_files = worker_arguments["image_files"]
        disable_tqdm = worker_arguments.get("disable_tqdm")
        LOGGER.info(f"Process started. (PID: {process.pid})")
        t_start = time.perf_counter()
        with logging_redirect_tqdm():
            for image_file in tqdm(
                natsorted(image_files),
                desc=f"(PID:{process.pid})",
                position=worker_id,
                disable=disable_tqdm
            ):
                status = self.perform_ocr(image_file)
                if status == Status.ERROR:
                    LOGGER.info(f"{status.value} ('{image_file}')")

        t_finish = time.perf_counter()
        t_total = (t_finish - t_start)
        LOGGER.info(f"Process complete. (PID: {process.pid})")
        return t_total

    def perform_ocr_batch(
        self,
        image_files: list,
        workers: int = 1,
        disable_tqdm: bool = None
    ):
        """Perform OCR on multiple files

        Parameters
        ----------
        image_files : list
            List of paths to image files
        workers : int, optional
            Number of workers
            The default is 1.
        disable_tqdm : bool, optional
            If True, the progress bars from :code:`tqdm` will be disabled.
            The default is None.
        """
        image_files = natsorted(image_files)
        file_count = len(image_files)

        t_start = time.perf_counter()

        workload, extra = divmod(file_count, workers)
        if workers > 1:
            print(f"Total {file_count} files "
                  f"distributed among {workers} workers.")
            print(f"Workload: {workload}-{workload + 1} per worker")

        worker_arguments = []
        _start = 0
        for idx in range(workers):
            _workload = workload + (idx < extra)
            worker_arguments.append({
                "worker_id": idx,
                "image_files": image_files[_start:_start+_workload],
                "disable_tqdm": disable_tqdm
            })
            _start = _start + _workload

        # ------------------------------------------------------------------- #

        mp.freeze_support()
        tqdm.set_lock(mp.RLock())
        with mp.Pool(
            workers,
            initializer=tqdm.set_lock,
            initargs=(tqdm.get_lock(),)
        ) as p:
            t_workers = p.map(self._worker_ocr_batch, worker_arguments)

        # ------------------------------------------------------------------- #

        t_final = time.perf_counter()
        t_total = t_final - t_start
        tqdm.write(f"Total Time Taken: {t_total:.2f} seconds")
        if workers > 1:
            tqdm.write(f"Time Saved: {sum(t_workers) - t_total:.2f} seconds")

###############################################################################
