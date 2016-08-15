import os
import re
import sys
import json
import settings
from multiprocessing import Process, Queue, Lock, Manager, cpu_count
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

class FlickrCrawler(BaseCrawler):   

    #def __init__(self, callback = None*args, **kwargs):
    def __init__(self, callback=None):
        super(FlickrCrawler, self).__init__('flickr')
        # example: https://www.flickr.com/photos/parismadrid/2099310718
        self.photos_url = 'https://www.flickr.com/photos/%s/%s'
        self.max_retries = 3
        self.callback = callback
        self.workers = []
        self.queue = Queue()
        self.lock = Lock()
        # for sharing state between processes
        self.shared_data = Manager().dict()
        self.retries = Manager().dict()
        
        if not hasattr(settings, 'NUM_OF_WORKERS'):
            self.num_of_workers = cpu_count()
        else:
            self.num_of_workers = settings.NUM_OF_WORKERS

    def start_workers(self):
        self.logger.info("starting %d worker processes" % self.num_of_workers)
        print "waiting for child processes to finish"
        for idx in range(self.num_of_workers):
            p = Process(target=self.worker_process, args=(self.queue, self.lock))
            self.workers.append(p)
            p.start()

        for child_process in self.workers:
            child_process.join()
        
        print "bye !!"
        self.logger.info("finished crawling process")

    def worker_process(self, queue, lock):
        self.logger.debug("starting worker process: %s" % self.worker_name)
        # keep processing images until done 
        while True:
            lock.acquire()
            if queue.empty() and self.should_stop():
                self.logger.debug("%s :: is stopping" % self.worker_name)
                lock.release()
                self.logger.debug("=========================================================")
                break

            self.logger.debug("%s :: is trying to get object from the queue" % self.worker_name)
            photo_dict = queue.get()
            lock.release()
            
            if photo_dict == None:
                self.mark_done()
                self.logger.debug("%s :: encoutered the last item, marking it done" % self.worker_name)
                break
         
            self.logger.debug("%s :: got the object with photo_id: %s" % (self.worker_name, photo_dict['id']))
            self.logger.debug("=========================================================")

            meta = self.extract_meta(photo_dict)
            self.logger.debug("%s :: extracted meta: %s for photo: %s" % (self.worker_name, meta, self.generate_photo_url(photo_dict)))
            self.logger.debug("=========================================================")

            if self.callback:
                self.callback(meta)

    def set_start_urls(self, urls=[]):
        """
        sets the urls to crawl
        """
        self.start_urls += urls

    def start(self):
        """
        starts the crawling process and worker processes
        """
        self.start_crawling(self.parse)
        self.start_workers()

    def stop_crawling(self):
        """
        marks the crawling process finished by putting None object in the queue
        """
        self.lock.acquire()
        self.queue.put(None)
        self.lock.release()

    def parse(self, response):
        """
        this method gets called when http response is available
        """
        self.logger.info("%s :: starts parsing for photo urls" % self.worker_name)
        for photo_dict in self.extract_photos_list(response):
            self.add_to_queue(photo_dict)

    def extract_photos_list(self, response):
        """
        this method gets called when a http response is available

        it parses the <script> tag from html page and generates a list of photos object having necessary information 
        to construct the URL of photo detail page, from where we can extract GPS data
        """
        soup = BeautifulSoup(response.text, "html.parser")
        # flickr stores it links to photo page under <script> tag with class modelExport
        script = soup.find("script", "modelExport")
        if not script:
            self.logger.error("%s :: couldn't find needed script tag, for url: %s" % (self.worker_name, response.url))
            return []

        # now we have to use regex to find photo ID and username so that we can generate url to photos page
        """
        Example: 
         "photos":{"_data":[
              {"_flickrModelRegistry":"photo-lite-models","pathAlias":"parismadrid","username":"Danny VB","realname":"",
                 "ownerNsid":"21692577@N02","faveCount":146,"commentCount":45,"title":"Paris","description":"Paris","license":0,
                  "sizes" : {}}]}
        """
        match = re.search(r'("photos":{"_data":)(.*)(,"fetchedStart")', script.text)
        if not match:
            self.logger.error("%s :: couldn't find photos list, for url: %s" % (self.worker_name, response.url))
            return []

        # it's a javascript object so we should be able to load it using json
        js_obj = match.group(2).strip()
        try:
            lst = json.loads(js_obj)
            return lst
        except ValueError, e:
            self.logger.error("%s :: invalid object found for photos list, for url: %s" % (self.worker_name, response.url))
            return []

    def sanitize_url(self, url):
        return "%s%s" % ('https://', url.strip())

    def generate_photo_url(self, photo_dict):
        return self.photos_url % (photo_dict['username'], photo_dict['id'])


    def extract_meta(self, photo_dict):
        """
        extracts the metadata for a given photo
        """
        title = photo_dict.get('title', '')
        description = photo_dict.get('description', '')
        username = photo_dict.get('pathAlias', None)
        photo_id = photo_dict.get('id', None) 

        # we can't generate photo url without photo_id
        if not photo_id:
            self.logger.error("%s :: couldn't find photo ID" % self.worker_name)
            return 
        
        # we can't generate photo url without username
        if not username:
            self.logger.error("%s :: couldn't extract username for photo ID: %s" % (self.worker_name, photo_id))
            return 

        url = self.photos_url % (username, photo_id)
        geo = self.extract_geo(url)
        if geo == None:
            self.logger.warn("%s :: couldn't extract GPS data for photo: %s" % (self.worker_name, url))
            return 
            
        latitude = geo[0]
        longitude = geo[1]
        return {
            'username': username,
            'photo_id': photo_id,
            'photo_title': title,
            'description': description,
            'photo_url': url,
            'latitude': latitude,
            'longitude': longitude
        }

    def add_to_queue(self, photo_dict):
        """
        adds an object to shared queue
        """
        self.lock.acquire()
        self.queue.put(photo_dict)
        self.lock.release()

    def retry(self, photo_dict):
        """
        adds an object to queue for retrying purposes
        """
        photo_id = photo_dict['id']
        attempts = self.retries.get(photo_id, 0)
        self.retries[photo_id] = attempts + 1
        self.add_to_queue(photo_dict)

    def num_of_attempts(self, photo_dict):
        """
        returns the number of times given object has been attempted to process
        """
        return self.retries.get(photo_dict['id'], 0)

    def extract_geo(self, photo_url):
        """
        extracts the GPS data from HTML page at given photo_url
        """
        response = self.make_request(photo_url)
        if not response:
            self.logger.error("%s :: error fetching page at url: %s" % (self.worker_name, photo_url))
            return None
         
        # extract lat, long from html page, stored as following example:w
        #[{"_flickrModelRegistry":"photo-geo-models","hasGeo":true,"latitude":48.853187,"longitude":2.350301,"accuracy":15,"isPublic":true,"id":"5238558922"}]
        match = re.search(r'("latitude":)([-\d.]+)(,"longitude":)([-\d.]+)', response.text)
        if match:
            return match.group(2), match.group(4)

        return (None, None)
    
    @property
    def worker_name(self):
        """
        utility method for tagging each worker processs
        """
        return "[Worker:"+str(os.getpid())+"]"

    def mark_done(self):
        """
        marks the entire process as done so that workers can gracefully exit by setting a flag in shared dictionary
        """
        self.shared_data['done'] = True

    def should_stop(self):
        """
        utility method to help workers decide if they should stop or not
        """
        return self.shared_data.get('done', False)
