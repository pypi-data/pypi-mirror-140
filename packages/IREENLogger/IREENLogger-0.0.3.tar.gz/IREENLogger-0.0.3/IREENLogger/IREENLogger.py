import sys
import redis
from uuid import uuid4
from typing import Literal
from datetime import datetime


class LogBase:
    def __init__(self):
        self.category = base_category
        self.service = base_service
        self.project = base_project
        self.run_mode = base_mode
        self.server = base_server


class Log(LogBase):
    def __init__(self):
        super().__init__()
        dt = datetime.utcnow()
        self.id = str(uuid4())[:8]
        self.dt = dt.strftime("%d:%m:%YT%H:%M:%S")
        self.timestamp = datetime.timestamp(dt)
        self.level = str
        self.message = str
        self.code = int
        self.context = str


class logger:
    def __init__(self, redis_host, redis_port, category, service, project, mode, server):
        global base_category, base_service, base_project, base_mode, base_server
        base_category = category
        base_service = service
        base_project = project
        base_mode = mode
        base_server = server
        sys.tracebacklimit = -1
        try:
            self.RServer = redis.Redis(host=redis_host, port=redis_port, db=0)
        except Exception as err:
            raise Exception('Error on connecting to server', err)

    def push(self, log: Log):
        try:
            print(log.__dict__, flush=True)
            self.RServer.set(log.id, str(log.__dict__))
        except Exception as err:
            raise Exception('Error on pushing log to server', err)
        finally:
            del log

    def append_log(self, text: str, code: int, context: dict, level: Literal['error', 'info']):
        log = Log()
        log.message = text
        log.code = code
        log.level = level
        log.context = context
        self.push(log)

    def info(self, text: str, code: int, context: dict):
        return self.append_log(text, code, context, 'info')

    def error(self, text: str, code: int, context: dict):
        return self.append_log(text, code, context, 'error')
