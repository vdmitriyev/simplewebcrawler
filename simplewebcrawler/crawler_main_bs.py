# coding: utf-8
#!/usr/bin/env python

__author__     = "Viktor Dmitriyev"
__copyright__ = "Copyright 2015, Viktor Dmitriyev"
__credits__ = ["Viktor Dmitriyev"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "-"
__email__     = ""
__status__     = "Test"
__date__    = "23.01.2015"
__description__ = "Simple web crawler that uses beautifulsoup package."


from time import sleep
from crawler_helper import DirectoryHelper
import urllib2
from bs4 import BeautifulSoup
from pprint import pprint

# SLEEP_TIME_IN_SECONDS = 1
class BSCrawler():

    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

    def __init__(self):
        self.helper = DirectoryHelper()
        self.helper.prepare_working_directory()
        self.temp_dir = self.helper.temp_dir

    def crawl(self):
        """
            (obj) -> None

            Method that extracts urls from 'dispatcher' dictionary and process them.
        """

        for url in self.dispatcher:
            print '[i] following url is going to be parsed:\n %s '% (url)
            self.main_url = url
            doc = self.download_document(url)
            self.dispatcher[url](self, doc)

    def download_document(self, url):
        """
            (obj,str) -> (str)

            Downloading html page and storing inside string.
        """
        html = None
        try:
            req = urllib2.Request(url=url, headers={'User-Agent': self.UA})
            hdl = urllib2.urlopen(req)
            html = hdl.read()
        except Exception,ex:
            print '[e] Exception: %s ' % str(ex)

        return html

    def save_images(self, img_list, folder):
        """
            (obj, list, str) -> None

            Saving images to the folders
        """

        img_dir = self.temp_dir + folder + '\\'
        self.helper.create_directory_ondemand(img_dir)
        for img in img_list:
            img_full_url = img['src']
            if img['src'][:4] != 'http':
                img_full_url = self.main_url + img['src']
            img_extention = img_full_url[img_full_url.rfind('.'):]
            image = self.download_document(img_full_url)

            if image is not None:
                gen_img_name = img_dir + self.helper.gen_file_name(extention='')
                self.helper.save_img_file(gen_img_name + img_extention, image)
            else:
                print '[i] this image is not found: %s' % (img_full_url)


    def process_biblio_oldb(self, doc):
        """
            (obj, str) -> None

            Processing given html to extract information about publication rates.
        """

        soup = BeautifulSoup(doc)


        gen_new_name = self.helper.gen_file_name(extention='')

        prettified_html = soup.prettify()
        text_from_html = soup.get_text()

        output = ''
        rows = soup.findAll('tr')
        section = ''
        dataset = {}

        years = ['2010:', '2011:', '2012:', '2013:', '2014:']

        for row in rows:
            if row.attrs:
                section = row.text
                dataset[section] = {}
            else:
                cells = row.findAll('td')
                for cell in cells:

                    if 'Gesamtpunkte' in cell.text:

                        text = cell.text.replace(u'\xa0', u' ')

                        splitted_ = text.split(u' ')
                        filtered_ = filter(lambda a: a != u'', splitted_)
                        filtered_ = filtered_[1:]

                        name = ''

                        def biblio_get_name(_input_list, years):
                            """
                            (obj, list) -> str

                            Building an proper name for the biblio link.
                            """
                            name = ''
                            for value in _input_list:
                                if value in years:
                                    break;
                                name = name + value + ' '

                            name_splitted = name.split(',')
                            name_result = name_splitted[1].rstrip().lstrip() + ' ' + name_splitted[0].rstrip().lstrip()

                            return name_result

                        name = biblio_get_name(filtered_, years)
                        dataset[name] = ''

                        temp_dict = {}

                        for index, value in enumerate(filtered_):
                            if filtered_[index] in years:
                                temp_dict[filtered_[index]] = filtered_[index + 1]

                        dataset[name] = temp_dict

        final_dataset = {}
        for value in dataset:
            years_dict = {}
            for year in years:
                try:
                    years_dict[year[:len(year)-1]] = float(dataset[value][year])
                except:
                    years_dict[year[:len(year)-1]] = float(0.0)
            final_dataset[value] = years_dict

        keyfunc = ''
        for year in years:
            sorted_ = sorted(final_dataset.keys(), key = lambda x: final_dataset[x][year[:len(year)-1]])
            output = output + '-----------------' + year[:len(year)-1] + '-----------------------' + '\n'
            for value in sorted_:
                output = output  + value + ' ' + str(final_dataset[value]) + '\n'

        # text data for debugging, uncomment if needed
        #self.helper.save_file(self.temp_dir + gen_new_name + '.html', prettified_html)
        #self.helper.save_file(self.temp_dir + gen_new_name + '.txt', text_from_html)
        self.helper.save_file(self.temp_dir + gen_new_name + '.output', output)


    dispatcher = {
            'http://diglib.bis.uni-oldenburg.de/hsb/statistik/?page=hsb_institut&jahr=2012&inst=20100': process_biblio_oldb
        }

def main():

    crawler = BSCrawler()
    crawler.crawl()

if __name__ == '__main__':
    main()
