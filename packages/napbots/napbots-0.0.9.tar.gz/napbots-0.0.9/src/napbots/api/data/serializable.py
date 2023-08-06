__author__ = "Hugo Inzirillo"

import json
from abc import ABCMeta, abstractmethod
from datetime import datetime, date
from enum import Enum
from functools import singledispatchmethod


class _Encoder(Enum):
    JSON = "JSON"


class Formatter(metaclass=ABCMeta):
    JSON = "JSON"

    @abstractmethod
    def format(self):
        raise NotImplementedError


class _DateTimeObjectFormatter(Formatter):
    @singledispatchmethod
    def format(self, arg):
        pass

    @format.register
    def _(self, arg: date):
        return arg.strftime("%Y-%m-%d")

    @format.register
    def _(self, arg: datetime):
        return arg.strftime("%Y-%m-%dT%H:%M:%S")



    @format.register
    def _(self, arg: str):
        return self.format(datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S"))


class Serializable(_DateTimeObjectFormatter, metaclass=ABCMeta):
    @property
    @abstractmethod
    def json(self):
        raise NotImplementedError

    def __iter__(self):
        iterable = dict((x, y) for x, y in self.__dict__.items() if x[:2] != '__')
        iterable.update(self.__dict__)
        for x, y in iterable.items():
            yield x, y

    def __format__(self, encoder):
        if isinstance(encoder, str):
            if _Encoder(encoder) == _Encoder.JSON:
                return json.dumps(self.json)
            else:
                raise NotImplementedError("Others encoders are not available")
        else:
            raise TypeError(f'encoder should be an instance of {type(_Encoder)}')
