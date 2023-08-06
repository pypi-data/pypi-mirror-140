"""Module for creating data clients."""

import os
import typing as typ
from abc import ABC, abstractmethod
from dataclasses import dataclass

import yaml
from pymongo import MongoClient

ClientConnection = typ.Union[MongoClient]


@dataclass
class Auth:
    user: str
    password: str


@dataclass
class AtlasAuth(Auth):
    pass


class Client(ABC):
    """Base class for creating a client connection to a datasource."""

    @abstractmethod
    def conn(self) -> ClientConnection:
        raise NotImplementedError()


class PerfAtlasClient(Client):
    """Client connection to perf atlas db."""

    def __init__(self) -> None:
        with open(os.path.expanduser("~/credentials.yml"), "r") as f:
            doc = yaml.safe_load(f)
            user = doc["PERF_DB_READ_USER"]
            password = doc["PERF_DB_READ_PASS"]
        self.auth = AtlasAuth(user=user, password=password)

    def conn(self) -> ClientConnection:
        """Return client connection."""
        conn_str = f"mongodb+srv://{self.auth.user}:{self.auth.password}@performancedata-g6tsc.mongodb.net/expanded_metrics?readPreference=secondary&readPreferenceTags=nodeType:ANALYTICS&readConcernLevel=local"
        client = MongoClient(conn_str)

        return client
