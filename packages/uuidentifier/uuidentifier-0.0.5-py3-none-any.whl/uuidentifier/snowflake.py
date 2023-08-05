#!/usr/bin/env python
import operator
import os
import time
import warnings
from datetime import datetime
from functools import reduce
from typing import List, Tuple
import uuid
import datetime
import string
import re


class IntConv(object):
    def __init__(self, N: int = 32) -> None:
        chars = string.digits + string.ascii_letters + '_@'
        self.BASE_LIST = chars[:N]
        self.BASE_DICT = dict((c, i) for i, c in enumerate(self.BASE_LIST))

    def decode_from(self, n_str: str):
        length = len(self.BASE_DICT)
        ret = 0
        for i, c in enumerate(n_str[::-1]):
            ret += (length ** i) * self.BASE_DICT[c]
        return ret

    def encode_to(self, integer: int) -> str:
        if integer == 0:
            return self.BASE_LIST[0]
        length = len(self.BASE_LIST)
        ret = ''
        while integer != 0:
            ret = self.BASE_LIST[integer % length] + ret
            integer //= length
        return ret

class UUID2(object):
    SEQUENCE_ID = 0
    WORKER_ID = None
    IC = IntConv(62)
    RETRY_LIMIT = 100

    @classmethod
    def get_worker_id(cls) -> str:
        if cls.WORKER_ID is None:
            macs = os.popen(
                "ifconfig | awk '/ether/{print $2}'").read().strip().split('\n')
            mac_id = int(uuid.getnode())
            if macs:
                mac_id = re.match('^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$',
                                  macs[0].lower()).group(0).replace(':', '')
                mac_id = int(mac_id, 16)
            cls.WORKER_ID = cls.IC.encode_to(mac_id).rjust(8, '0')
        return cls.WORKER_ID

    @classmethod
    def get_timestamp_string(cls) -> str:
        return datetime.datetime.now().strftime('%Y%m%d-%H%M%S%f')[:-3]

    @classmethod
    def task_type(cls) -> str:
        """ 预留扩展位 (4bits)，可以用于区分任务类型或者嵌入其他信息
        """
        return '0000'

    @classmethod
    def produce_id(cls) -> str:
        cls.SEQUENCE_ID = (cls.SEQUENCE_ID + 1) % 1000
        _sequence_id = str(cls.SEQUENCE_ID).rjust(3, '0')
        _timestamp = cls.get_timestamp_string()
        _worker_id = cls.get_worker_id()
        _task_type = cls.task_type()
        return '{}-{}-{}-{}'.format(_timestamp, _worker_id, _sequence_id, _task_type)

    @classmethod
    def produce_unique_id(cls) -> str:
        return cls.produce_id()


class Worker(object):
    def __init__(self) -> None:
        self.all_macs = []

    def get_mac(self, ifname: str) -> str:
        """ Get MAC address corresponding to the given interface """
        cmd = "ifconfig | grep -A5 {} | grep ether".format(ifname)
        resp = os.popen(cmd).read().strip()
        if not resp:
            warnings.warn(
                'No MAC address found for interface {}'.format(ifname))
            return self.get_first_valid_mac()
        return resp.split()[1]

    def get_all_macs(self) -> list:
        """ Get all MAC addresses of all interfaces """
        if not self.all_macs:
            self.all_macs = os.popen("ifconfig | awk '/ether/{print $2}'"
                                     ).read().strip().split('\n')
        return self.all_macs

    def get_first_valid_mac(self) -> str:
        """ Get the first valid MAC address of the all interfaces """
        return self.get_all_macs()[0]


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SnowFlake(metaclass=SingletonMeta):
    """Generate a uuid"""

    def __init__(self, interface: str = '') -> None:
        """ A valid interface must be given """
        self._starting_date = '2021-01-01 00:00:00,000'
        self.__interface = interface
        self.__sequence = 0
        self.__worker_id = None

    @property
    def interface(self) -> str:
        return self.__interface

    @interface.setter
    def interface(self, new_interface: str) -> str:
        self.__interface = new_interface
        return self.__interface

    @property
    def timestamp(self) -> int:
        cur_time = time.time() * 1000
        start_time = datetime.strptime(
            self._starting_date, "%Y-%m-%d %H:%M:%S,%f").timestamp() * 1000
        self.__timestamp = int(cur_time - start_time)
        return self.__timestamp

    @property
    def worker_id(self):
        if self.__worker_id is None:
            if self.__interface:
                mac = Worker().get_mac(self.__interface)
            else:
                mac = Worker().get_first_valid_mac()
            nums = [int(h, 16) for h in mac.split(':')]
            acc = reduce(lambda n, acc: n * 16+acc, nums[1:], nums[0])
            self.__worker_id = acc % 1024
        return self.__worker_id

    @property
    def datacenter_id(self) -> int:
        raise NotImplementedError

    @property
    def sequence(self) -> int:
        self.__sequence = (self.__sequence + 1) % 4096
        return self.__sequence

    def uuid2(self)->str:
        return UUID2.produce_unique_id()

    def uuid(self) -> int:
        timestamp = self.timestamp
        worker_id = self.worker_id
        sequence = self.sequence
        return ((timestamp << 22) | (worker_id << 12) | sequence)

    def reverse(self, uuid: int) -> Tuple[str]:
        """
        Reverse the uuid to a tuple of (timestamp, worker_id, sequence)
        """
        timestamp = uuid >> 22
        start_time = datetime.strptime(
            self._starting_date, "%Y-%m-%d %H:%M:%S,%f").timestamp() * 1000
        cur_time = start_time+timestamp
        _date = datetime.fromtimestamp(
            cur_time/1000).strftime("%Y-%m-%d %H:%M:%S,%f")

        worker_id = (uuid >> 12) & 0x3ff
        macs = Worker().get_all_macs()
        used_mac = None
        for mac in macs:
            nums = [int(h, 16) for h in mac.split(':')]
            acc = reduce(lambda n, acc: n * 16+acc, nums[1:], nums[0])
            if acc % 1024 == worker_id:
                used_mac = mac
                break

        sequence = uuid & 0xfff
        return (_date, used_mac, sequence)


if __name__ == '__main__':
    snowflake = SnowFlake('enp34s0')
    for i in range(10):
        print(snowflake.uuid())
