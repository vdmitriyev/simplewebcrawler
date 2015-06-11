# coding: utf-8
#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__copyright__   = "Copyright 2015, Viktor Dmitriyev"
__credits__     = ["Viktor Dmitriyev"]
__license__     = "MIT"
__version__     = "1.0.0"
__maintainer__  = "-"
__email__       = ""
__status__      = "Test"
__date__        = "08.06.2015"
__description__ = "Simple web crawler that iterates one domain, save as html and forms and graph of the it."

import os
import uuid
import json
import Queue
import urllib2
import collections
from bs4 import BeautifulSoup
from time import sleep
from pprint import pprint

# importing custom libraries
try:
    from helper_directory import DirectoryHelper
except:
    import urllib
    target_path = 'https://raw.githubusercontent.com/vdmitriyev/sourcecodesnippets/master/python/helper_directory/helper_directory.py'
    target_name = 'helper_directory.py'
    urllib.urlretrieve (target_path, target_name)
    from helper_directory import DirectoryHelper
finally:
    import helper_directory
    if helper_directory.__version__ != '1.0.0':
        print 'Wrong version of the library {0}. Check the version'.format(helper_directory.__file__)

# time of the delay
SLEEP_TIME_IN_SECONDS = 2

# other content types will be ingnored
ACCEPTABLE_CONTENT_TYPE = 'text/html'

class SetQueue(Queue.Queue):

    def _init(self, maxsize):
        Queue.Queue._init(self, maxsize)
        self.all_items = set()

    def _put(self, item):
        if item not in self.all_items:
            Queue.Queue._put(self, item)
            self.all_items.add(item)

    def _get(self):
        item = Queue.Queue._get(self)
        self.all_items.remove(item)
        return item

class BSCrawler():

    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

    def __init__(self, start_url, domain):
        """
            initial method:
                - initiates helper class;
                - checks the temp directory existance
        """

        self.helper = DirectoryHelper()
        #self.helper.prepare_working_directory()

        try:
            self.work_dir = self.helper.work_dir
        except:
            self.work_dir = '__temp__'

        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        if start_url is None:
            print '[e] specify start URL'

        start_url = BSCrawler.adjust_url(start_url)

        self.urls = SetQueue()
        self.urls.put(start_url)
        self.domain = domain
        self.website_graph = {}

        print '[i] files will be saved into folder "{0}"'.format(self.work_dir)

    def download_document(self, url):
        """
            (obj,str) -> (str)

            Downloading html page and storing inside string.
        """

        html = None
        try:
            req = urllib2.Request(url=url, headers={'User-Agent': self.UA})
            hdl = urllib2.urlopen(req)

            content_type = hdl.info().dict['content-type']

            if  ACCEPTABLE_CONTENT_TYPE in content_type:
                html = hdl.read()
            else:
                print '[i] ignored content-type was {0}'.format(content_type)

        except Exception as ex:
            print '[e] exception: {0}, arguments: {1}'.format(ex.message, ex.args)

        return html

    @staticmethod
    def adjust_url(url):
        """
            Removing the last slash if presented
        """

        if url[-1:] == '/':
            url = url[:-1]

        return url

    def crawl(self):
        """
            (obj) -> None

            Method that extracts urls from 'dispatcher' dictionary and process them.
        """

        visited = set()

        while not self.urls.empty(): # iterating over queue

            url = self.urls.get()
            print '[i] parsing following url {0}'.format(url)

            visited.add(url)
            html = self.download_document(url)

            if html is None:
                continue

            soup = BeautifulSoup(html)

            # extracting additional links
            for line in soup.findAll('a'):
                url_potential = line.get('href')
                if url_potential != '#' and \
                   url_potential is not None:

                   url_potential = BSCrawler.adjust_url(url_potential)

                   self.update_website_graph(from_link=url, to_link=url_potential)

                   if  url_potential not in visited and \
                        self.domain in url_potential:
                            self.urls.put(url_potential) #adding to the queue

            def proper_filename(url):
                html_file_name = url.replace('https://', '')
                html_file_name = html_file_name.replace('http://', '')
                html_file_name = html_file_name.replace(':', '')
                #h_file_name = h_file_name.replace('/', os.path.sep) + str(uuid.uuid1())
                html_file_name = html_file_name.replace('/', '-') + str(uuid.uuid1())

                return self.work_dir + os.path.sep + html_file_name + '.html'


            # saving html to a file
            full_file_name = proper_filename(url)
            self.helper.save_file(full_file_name, html)
            print '[i] html was saved to the {}'.format(full_file_name)

    def update_website_graph(self, from_link, to_link):
        """
            (obj, str) -> None

            Updating graph of a web site
        """

        if not from_link in self.website_graph:
            self.website_graph[from_link] = []

        self.website_graph[from_link] += [to_link]

def main():

    crawler = BSCrawler(start_url='http://vdmitriyev.github.io/', domain='vdmitriyev.github.io')
    crawler.crawl()

    pprint(crawler.website_graph)

if __name__ == '__main__':

    # setting system default encoding to the UTF-8
    import sys
    reload(sys)
    sys.setdefaultencoding('UTF8')

    main()
