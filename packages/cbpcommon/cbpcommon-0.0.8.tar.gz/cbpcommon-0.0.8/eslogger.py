import logging
import threading
import uuid
from datetime import datetime

import jsonpickle as jsonpickle
from elasticsearch import Elasticsearch


class Elastic:
    def __init__(self, component):
        self.es = Elasticsearch(hosts='10.0.0.212', port=9200)
        self.component = component

    def post(self, severity, message, args):
        try:
            body = {"message": message, "@timestamp": datetime.utcnow(), "application": self.component}

            if severity:
                body["severity"] = str(severity)

            if args:
                body["args"] = args

            self.es.index(index="logs-" + '{0:%Y-%m-%d}'.format(datetime.now()), doc_type="_doc", document=body)
            pass
        except Exception as e:
            print("Elasticsearch unavailable")
            print("An exception occurred [" + jsonpickle.encode(e) + " ]")
            pass

    def async_post(self, severity, message, args):
        threading.Thread(target=self.post, args=(severity, message, args)).start()


class Logger:

    def __init__(self, component, _id=None):
        if not _id:
            self.generate_id()
        else:
            self.id = str(_id)
        self.component = component
        log = logging.getLogger('internal')
        log.setLevel(logging.DEBUG)
        self.elastic = Elastic(self.component)
        self.log = log

    def generate_id(self):
        self.id = str(uuid.uuid1().time)

    def info(self, message, *args):
        self.logger(logging.INFO, message, args)

    def debug(self, message, *args):
        self.logger(logging.DEBUG, message, args)

    def warning(self, message, *args):
        self.logger(logging.WARNING, message, args)

    def critical(self, message, *args):
        self.logger(logging.CRITICAL, message, args)

    def error(self, message, *args):
        self.logger(logging.ERROR, message, args)

    def logger(self, level, message, *args):
        args_message = ''

        if args:
            args = jsonpickle.encode(args)
            args_message = " - args:[ " + args + " ]"

        self.log.log(level, self.id + ' - ' + message + args_message)
        self.elastic.async_post(logging.getLevelName(level), message, args)


if __name__ == "__main__":
    logger = Logger('test')
    e = Exception("Test Exception")
    logger.debug("This is a debug")
    logger.info("This is an info")
    logger.error("This is an error", e)
