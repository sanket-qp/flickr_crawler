import unittest
import requests
from flickr_crawler import FlickrCrawler

class TestCases(unittest.TestCase):

    def setUp(self):
        self.flickr_crawler = FlickrCrawler()

    def test_geo(self):
        expected = ('-33.703937', '150.374755')
        self.assertEquals(expected, self.flickr_crawler.extract_geo('https://www.flickr.com/photos/karen_od/494682581'))
        self.assertEquals((None, None), self.flickr_crawler.extract_geo('https://www.flickr.com/search/?text=paris'))
        self.assertEquals(None, self.flickr_crawler.extract_geo('xyz'))

    def test_extract_meta(self):
        expected = {'username': 'karen_od', 'photo_id': '494682581', 'description': '', 
                    'longitude': u'150.374755', 'photo_title': '', 'latitude': u'-33.703937', 'photo_url': 'https://www.flickr.com/photos/karen_od/494682581'}
        self.assertEquals(expected, self.flickr_crawler.extract_meta({'pathAlias': 'karen_od', 'id': '494682581'}))
        self.assertEquals(None, self.flickr_crawler.extract_meta({'pathAlias': 'karen_od'}))
        self.assertEquals(None, self.flickr_crawler.extract_meta({'id': '494682581'}))
 
    def test_extract_photos_list(self):
        response = requests.get('https://www.flickr.com/search/?text=paris')
        photos_list = self.flickr_crawler.extract_photos_list(response)
        self.assertEquals(25, len(photos_list))

if __name__ == "__main__":
    unittest.main()
