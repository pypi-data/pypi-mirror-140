import glob
import os
import json
from bs4 import BeautifulSoup
import requests
import pandas as pd


def info():
    print('how to use this package:')
    print('this package contains: recent news, conferences, and webinars')
    print('auntminnie.News() for recent news')
    print('auntminnie.Conferences() for recent conferences')
    print('auntminnie.Webinar() for recent conferences')
    print('.test for testing connection the web')
    print('.singlepage for scrap data with spesific page. result json, excel & csv file in resultfile. deafult is scrap page 1')
    print('.allpage for scrap data as many pages availabel. result json, excel & csv file per page & all page in file resultfile')
    print('all in file resultfile with file name according to the features used')
    print('Conferences() only has .singlepage')


class Core:
    def __init__(self):
        self.url = 'https://www.auntminnie.com/index.aspx?'
        self.site = 'https://www.auntminnie.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/98.0.4758.82 Safari/537.36'}

        try:
            os.mkdir('resultfile')
            os.mkdir('resultfile/news')
            os.mkdir('resultfile/news/json')
            os.mkdir('resultfile/news/image')
            os.mkdir('resultfile/news/excelcsv')
            os.mkdir('resultfile/conferences')
            os.mkdir('resultfile/webinar')
            os.mkdir('resultfile/webinar/json')
            os.mkdir('resultfile/webinar/image')
            os.mkdir('resultfile/webinar/excelcsv')
        except FileExistsError:
            pass

    def test(self):
        pass

    def singlepage(self):
        pass

    def allpage(self):
        pass


class News(Core):
    def __init__(self, page=1):
        super().__init__()
        params = {
            'sec': 'nws',
            'sub': 'rad',
            'pno': page
        }
        self.page = page
        self.newsweb = requests.get(self.url, params=params, headers=self.headers)
        self.newssoup = BeautifulSoup(self.newsweb.text, 'html.parser')
        self.newssite = self.newssoup.find_all('div', 'MoreNewsItem')

    def test(self):
        try:
            if self.newsweb.status_code == 200:
                print(f"{self.newssoup.find('div', 'siteSubHeader').text}is accsesable")
        except Exception:
            print("Can't accses web")

    def singlepage(self):
        print(f'This is the recent Radiology news in auntminnie on page {self.page}:')

        # scraping
        newslist = []
        for i in self.newssite:
            title = i.find('span', 'Head').text.replace('?', '').replace('/', '')
            date = i.find('span', 'maStartDate').text
            site = self.site + i.find('a')['href']
            img = self.site + i.find('img', 'cntImgRightHeadline')['src']
            print(f"{title}. Published on {date.replace(' -- ', '')}. link: {site}. image:{img} ")

            # sorting & create json file
            newsdict = {
                'title': title,
                'date': date.replace(' -- ', ''),
                'site': site,
                'img': img
            }
            newslist.append(newsdict)

            # download image
            with open(f'resultfile/news/image/{title}.jpg', 'wb') as outfile:
                imgg = requests.get(img)
                outfile.write(imgg.content)

        # create json file
        with open(f'resultfile/news/json/news_list_json_page_{self.page}.json', 'w+') as news_data:
            json.dump(newslist, news_data)

        # create excel & csv file
        df = pd.DataFrame(newslist)
        df.to_csv(f'resultfile/news/excelcsv/news csv page {self.page}.csv', index=False)
        df.to_excel(f'resultfile/news/excelcsv/news excel page {self.page}.xlsx', index=False)

        print('all file created')

    def allpage(self):
        # searh last page
        paginition = self.newssoup.find_all('a', 'prevNextButton')
        end = int(paginition[2].text)
        for i in range(1, end):
            self.__init__(i)
            self.singlepage()

        # create json file for merge
        filejson = sorted(glob.glob('resultfile/news/json/*.json'))
        datas = []
        for i in filejson:
            with open(i) as jsonfile:
                data = json.load(jsonfile)
                datas.extend(data)

        # create merge excel & csv file
        df = pd.DataFrame(datas)
        df.to_csv('resultfile/news/all data csv.csv', index=False)
        df.to_excel('resultfile/news/all data excel.xlsx', index=False)

        # create merge json file
        with open('resultfile/news/all_data_json.json', 'w') as outfile:
            json.dump(datas, outfile)

        print('all file result has merge')


class Conferences(Core):
    def __init__(self):
        super().__init__()
        params = {'sec': 'def'}
        self.conreq = requests.get(self.url, params=params, headers=self.headers)
        self.consoup = BeautifulSoup(self.conreq.text, 'html.parser')
        con = self.consoup.find('div', 'supBoxLoopCtrl')
        self.con = con.findAll('span', 'supBoxHeadLnk')

    def test(self):
        try:
            if self.conreq.status_code == 200:
                print(f"{self.consoup.find('title').string}is accsesable")
        except Exception:
            print("Can't accses web")

    def singlepage(self):
        print('This is the recent Radiology Conferences:')

        # scraping
        conlist = []
        for i in self.con:
            title = i.find('a').text
            date = i.find('br').next_sibling
            site = i.find('a')['href']

            print(f"{title}. held on {date}. link: {site}")

            # sorting & create json file
            condict = {
                'title': title,
                'date': date,
                'site': site
            }
            conlist.append(condict)

        # create json file
        with open('resultfile/conferences/conferences_list_json.json', 'w+') as con_data:
            json.dump(conlist, con_data)

        # create excel & csv file
        df = pd.DataFrame(conlist)
        df.to_csv('resultfile/conferences/conferences csv.csv', index=False)
        df.to_excel('resultfile/conferences/conferences excel.xlsx', index=False)
        print('all file created')


class Webinar(Core):
    def __init__(self, page=1):
        super().__init__()
        params = {
            'sec': 'vendor',
            'sub': 'webinars',
            'pno': page
        }
        self.page = page
        self.webreq = requests.get(self.url, params=params, headers=self.headers)
        self.websoup = BeautifulSoup(self.webreq.text, 'html.parser')
        self.web = self.websoup.find_all('div', 'MoreNewsItem')

    def test(self):
        try:
            if self.webreq.status_code == 200:
                print(f"{self.websoup.find('div', 'siteSubHeader').text} is accsesable")
        except Exception:
            print("Can't accses web")

    def singlepage(self):
        print(f'This is the recent Radiology Webinars in auntminnie on page {self.page}:')

        # scraping
        weblist = []
        for i in self.web:
            title = i.find('span', 'Head').text.replace('?', '').replace(':', '')
            date = i.find('span', 'maStartDate').text
            site = self.site + i.find('a')['href']
            img = self.site + i.find('img', 'cntImgRightHeadline')['src']

            print(f"{title}. held on {date.replace(' -- ', '')}. link: {site}. img: {img} ")

            # sorting & create json file
            webdict = {
                'title': title,
                'date': date.replace(' -- ', ''),
                'site': site,
                'img': img
            }
            weblist.append(webdict)

            # download image
            with open(f'resultfile/webinar/image/{title}.jpg', 'wb') as outfile:
                imgg = requests.get(img)
                outfile.write(imgg.content)

        # create json file
        with open(f'resultfile/webinar/json/webinars_list_page_{self.page}.json', 'w+') as web_data:
            json.dump(weblist, web_data)

        # create excel & csv file
        df = pd.DataFrame(weblist)
        df.to_csv(f'resultfile/webinar/excelcsv/webinars csv page {self.page}.csv', index=False)
        df.to_excel(f'resultfile/webinar/excelcsv/webinars excel {self.page}.xlsx', index=False)

        print('all file created')

    def allpage(self):
        # search last page
        paginition = self.websoup.find_all('a', 'prevNextButton')
        end = int(paginition[2].text)
        for i in range(1, end):
            self.__init__(i)
            self.singlepage()

        # create json file for merge
        filejson = sorted(glob.glob('resultfile/webinar/json/*.json'))
        datas = []
        for i in filejson:
            with open(i) as jsonfile:
                data = json.load(jsonfile)
                datas.extend(data)

        # create merge excel & csv file
        df = pd.DataFrame(datas)
        df.to_csv('resultfile/webinar/all data csv.csv', index=False)
        df.to_excel('resultfile/webinar/all data excel.xlsx', index=False)

        # create merge json file
        with open('resultfile/webinar/all_data_json.json', 'w') as outfile:
            json.dump(datas, outfile)

        print('all file result has merge')

