"""Purpose: Pydantic models for the API."""
from typing import List, Dict

from modules.api import models as sd_models  # pylint: disable=E0401
from pydantic import BaseModel, Field


class S3DownloadRequest(sd_models.InterrogateRequest):
    """Interrogate request model"""
    bucket: str = Field(
        title='bucket',
        description='s3 bucket',
    )

    prefix: str = Field(
        title='prefix',
        description='s3 object path',
    )

    name: str = Field(
        title='name',
        description='s3 object name',
    )


class S3DownloadResponse(BaseModel):
    """Interrogate response model"""
    result: str = Field(
        title='result',
        description='result of the download process'
    )
