from typing import Callable, Dict, Optional
from secrets import compare_digest
import asyncio
from collections import defaultdict

import boto3

import os.path

from modules import shared, paths  # pylint: disable=import-error
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from scripts.api_modles import S3DownloadResponse, S3DownloadRequest


class Api:
    def __init__(
            self, app: FastAPI, prefix: Optional[str] = None
    ) -> None:

        print("start init s3 download api")
        if shared.cmd_opts.ckpt_dir:
            self.model_path = shared.cmd_opts.ckpt_dir
        else:
            model_dir = "Stable-diffusion"
            self.model_path = os.path.abspath(os.path.join(paths.models_path, model_dir))

        print(f's3 download api destination path: ${self.model_path}')

        if shared.cmd_opts.api_auth:
            self.credentials = {}
            for auth in shared.cmd_opts.api_auth.split(","):
                user, password = auth.split(":")
                self.credentials[user] = password

        self.app = app
        self.queue: Dict[str, asyncio.Queue] = {}
        self.res: Dict[str, Dict[str, Dict[str, float]]] = \
            defaultdict(dict)
        self.tasks: Dict[str, asyncio.Task] = {}

        self.runner: Optional[asyncio.Task] = None
        self.prefix = prefix
        self.running_batches: Dict[str, Dict[str, float]] = \
            defaultdict(lambda: defaultdict(int))

        self.add_api_route(
            'download_checkpoint',
            self.download_checkpoint,
            methods=['POST'],
            response_model=S3DownloadResponse
        )

        print("finish init s3 download api")

    def auth(self, creds: Optional[HTTPBasicCredentials] = None):
        if creds is None:
            creds = Depends(HTTPBasic())
        if creds.username in self.credentials:
            if compare_digest(creds.password,
                              self.credentials[creds.username]):
                return True

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Basic"
            })

    def add_api_route(self, path: str, endpoint: Callable, **kwargs):
        if self.prefix:
            path = f'{self.prefix}/{path}'

        if shared.cmd_opts.api_auth:
            return self.app.add_api_route(path, endpoint, dependencies=[
                Depends(self.auth)], **kwargs)
        return self.app.add_api_route(path, endpoint, **kwargs)

    def download_checkpoint(self, req: S3DownloadRequest):
        s3 = boto3.client('s3')
        s3.download_file(req.bucket, req.prefix, f'{self.model_path}/{req.name}')

        return S3DownloadResponse(result=f'{self.model_path}/{req.name}')


def on_app_started(_, app: FastAPI):
    Api(app, '/s3_download/v1')
