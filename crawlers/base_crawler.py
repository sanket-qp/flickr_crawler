import logging
import requests
import settings
from abc import ABCMeta, abstractmethod

class BaseCrawler:  
    __metaclass__ = ABCMeta
    name = None
    settings = None
    
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must set attribute: name" % type(self).__name__)

        if not hasattr(self, 'start_urls'):
            self.start_urls = []

        log_file = '%s.log' % self.name
        log_level = logging.DEBUG

        if hasattr(settings, 'LOG_FILE'):
            log_file = settings.LOG_FILE

        if hasattr(settings, 'LOG_LEVEL'):
            log_level = settings.LOG_LEVEL

        self.logger = self.get_logger(log_file, log_level)
        self.num_processes = len(self.start_urls) if self.start_urls else 1
        self.visited = set()

    def get_logger(self, log_file, log_level):
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger = logging.getLogger(self.name)
        logger.setLevel(log_level)  
        logger.addHandler(fh)
        return logger

    def start_crawling(self, callback):
        for url in self.start_urls:
            if url in self.visited:
                continue

            self.visited.add(url)
            resp = self.make_request(url)
            if resp: callback(resp)

        self.stop_crawling()

    def make_request(self, url):
        try:
            resp = requests.get(url)
            return resp
        except Exception, e:
            self.logger.error("Error requesting url: %s, error: %s" % (url, e))
            
    @abstractmethod
    def set_start_urls(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop_crawling(self):
        pass
