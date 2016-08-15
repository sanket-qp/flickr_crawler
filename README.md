# flickr_crawler
Simple Flickr Crawler

This is a simple library for crawling flickr.com 

## Quick Start 
```python
from crawlers import FlickrCrawler
flickr = FlickrCrawler()
flickr.set_start_urls(['https://www.flickr.com/search/?text=paris'])
flickr.start()
```

## Installation
```python
pip install -r requirement.txt
```

## Demo Application 
I've provided a demo application showing the usage of library. it provides a callback which saves the data in to sqlite database.
you can change the database settings in settings.py
```python
python app.py
```
