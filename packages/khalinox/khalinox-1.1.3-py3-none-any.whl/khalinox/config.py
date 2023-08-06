"""Store and retrieve credentials and configuration

Handle serialization, deserialization and encryption for password.
"""

import getpass
import json
import os
from pathlib import Path
from typing import Callable

import requests
import urllib3
from loguru import logger
from urllib3.exceptions import InsecureRequestWarning
from pydantic import BaseSettings, HttpUrl, validator
from pathlib import Path
from typing import Union, TYPE_CHECKING
from khalinox import utils


# hacky for autocomplete in vscode
# https://github.com/microsoft/python-language-server/issues/1898

if TYPE_CHECKING:  # pragma: no cover
    import dataclasses

    static_check_init_args = dataclasses.dataclass
else:

    def static_check_init_args(cls):
        return cls


@static_check_init_args
class WebHDFS(BaseSettings):
    # where to write/read by default
    default_dir: Path


@static_check_init_args
class HiveJDBC(BaseSettings):
    trust_store: Path
    store_password: str
    hive_vars: dict
    driver_class: str = "org.apache.hive.jdbc.HiveDriver"


@static_check_init_args
class Config(BaseSettings):
    """Configuration to interact with hive & hdfs using knox

    user/password are asked using interactive inputs if they are not provided
    """

    knox_url: HttpUrl
    # passed verbatim to python requests
    verify: Union[None, bool, str]
    user: str = ""
    # encrypt/decrypt
    _key: str
    # encrypted password with key
    password: str = ""
    path: Path
    webhdfs: WebHDFS
    hive_jdbc: HiveJDBC

    def __init__(self, **data):
        super().__init__(**data)
        # this could also be done with default_factory
        try:
            self._key = os.environ["KNOX_KEY"]
        except KeyError as k:
            raise KeyError("fernet key should exist in env as `KNOX_KEY`")

    @validator("knox_url")
    def port_must_be_present(cls, url):
        if not url.port:
            raise ValueError(
                f"{url} should provide a specific port (e.g. https://myhost.me:8888)"
            )
        return url

    @validator("password")
    def encrypt_password(cls, password):
        if password:
            return password
        else:
            raw = getpass.getpass("password")
            return utils.encrypt(os.environ["KNOX_KEY"], raw)

    @validator("user")
    def non_empty_user(cls, user):
        if user:
            return user
        else:
            raw = input("user")
            return raw

    class Config:
        env_prefix = "knox_"
        underscore_attrs_are_private = True

    def save(self):
        self.path.write_text(self.json(), encoding="utf8")
