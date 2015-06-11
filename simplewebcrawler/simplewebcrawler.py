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

import os
import uuid
import json
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

SLEEP_TIME_IN_SECONDS = 2
class BSCrawler():

    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

    def __init__(self):
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

        print '[i] files will be saved into folder "{0}"'.format(self.work_dir)

    def crawl(self):
        """
            (obj) -> None

            Method that extracts urls from 'dispatcher' dictionary and process them.
        """

        for url in self.dispatcher:
            print '[i] following url is going to be parsed:\n {0}'.format(url)
            self.main_url = url
            doc = self.download_document(url)
            self.dispatcher[url](self, doc)

    def crawl_dynamic(self):
        """
            (obj) -> None

            Method that extracts urls from 'dispatcher' in a dynamic way.
            It means that the initial URL patter should contain '%s' string patter to be formatted.
        """

        for url in self.dispatcher_dynamic:
            print '[i] following url is going to be parsed in a dynamic way:\n {0}'.format(url)
            self.dynamic_url = url
            tag = self.dispatcher_dynamic[url][1]
            self.dispatcher_dynamic[url][0](self, tag)

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
        except Exception as ex:
            print '[e] exception: {0}, arguments: {1}'.format(ex.message, ex.args)

        return html

    def save_images(self, img_list, folder):
        """
            (obj, list, str) -> None

            Saving images to the folders
        """

        img_dir = self.work_dir + folder + '\\'
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
                print '[i] this image is not found: {0}'.format(img_full_url)


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
        #self.helper.save_file(self.work_dir + gen_new_name + '.html', prettified_html)
        #self.helper.save_file(self.work_dir + gen_new_name + '.txt', text_from_html)
        self.helper.save_file(self.work_dir + os.path.sep + gen_new_name + '.output', output)


    def process_tutiempo_weather(self, tag):
        """
            (obj) -> None

            Processing weather data of the city from the tutiempo.

            KRASNOYARSK: http://en.tutiempo.net/climate/ws-284935.html
            NOVOSIBIRSK: http://en.tutiempo.net/climate/ws-296340.html
        """

        delimeter = ';'

        def internal_parser(html):
            """
                (str) -> dict

                Internal parser that parses given html accoding to it's structure.
            """

            soup = BeautifulSoup(html)
            data = []
            table = soup.find('table', attrs={'class':'medias mensuales'})
            rows = table.findAll('tr')
            for row in rows:
                cols = row.findAll('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele]) # Get rid of empty values

            daily_weather = {}
            for row in data:
                if len(row) > 3:
                    try:
                        day = int(row[0])
                        if day >= 1 and day <= 31:
                            daily_weather[day] = [row[2], row[3]]
                    except:
                        pass
                        #print '[e] exception: {}'.format(str(ex))

            # sorting values to have them in order
            daily_weather = collections.OrderedDict(sorted(daily_weather.items()))
            return daily_weather

        #params for testing
        years = ['1999']
        months = ['01']

        #params for real processing
        #years = ['1999', '2000', '2001', '2002']
        #months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        try:
            if years is None or len(years) < 1:
                raise Exception('years should be defined')
            if months is None or len(months) < 1:
                raise Exception('months should be defined')
        except Exception as ex:
            print '[e] exception: {0}, arguments: {1}'.format(ex.message, ex.args)
            return

        result_csv = list()
        for year in years:
            for month in months:
                month_year = '{0}-{1}'.format(month,year)
                url_to_download = self.dynamic_url % (month_year)

                # priting info about url to download
                print '[i] url to download {}'.format(url_to_download)

                month_weather = internal_parser(self.download_document(url_to_download))
                for key in month_weather:
                    tmp_time = '{}-{}-{}'.format(str(year), str(month), str(key))
                    tmp_max = str(month_weather[key][0])
                    tmp_min = str(month_weather[key][1])
                    result_csv.append([tmp_time, tmp_max, tmp_min])

                # setting the main script to sleep for some seconds
                sleep(SLEEP_TIME_IN_SECONDS)

        # generating new file name
        _new_file_name = str(uuid.uuid1())

        # converting to the csv
        csv_output = ''

        # setting header of the csv
        prefix = tag[0:3]
        csv_output =  prefix + 'Time' + delimeter + prefix + 'MaxTemp' + delimeter + prefix + 'MinTemp' + '\n'

        for row in result_csv:
            tmp = ''
            for value in row:
                tmp += value + delimeter
            csv_output += tmp[:-1*len(delimeter)] + '\n'

        # saving csv output to in the file
        csv_full_path = self.work_dir + os.path.sep + tag + '-' + _new_file_name + '.csv'
        self.helper.save_file(csv_full_path, csv_output)
        print '[i] data in csv saved to the {}'.format(csv_full_path)

    # dispatchers for extract and parsing one single web page
    dispatcher = {
            'http://diglib.bis.uni-oldenburg.de/hsb/statistik/?page=hsb_institut&jahr=2012&inst=20100': process_biblio_oldb,
        }

    # dispatchers for extract and parsing multiple web pages
    dispatcher_dynamic = {
            'http://en.tutiempo.net/climate/%s/ws-284935.html': [process_tutiempo_weather, "KRASNOYARSK"],
            'http://en.tutiempo.net/climate/%s/ws-296340.html': [process_tutiempo_weather, "NOVOSIBIRSK"],
        }

def main():

    crawler = BSCrawler()
    #crawler.crawl()
    crawler.crawl_dynamic()

if __name__ == '__main__':
    main()
