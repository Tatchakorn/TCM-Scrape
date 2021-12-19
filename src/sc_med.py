'''
Data from http://yibian.hopto.org
'''
import re
import random
import time
from typing import Dict
from pathlib import Path

from requests_cache.session import CachedSession
from bs4 import BeautifulSoup

from .json_handler import JsonHandler


class BaseMedScrape:
    '''
    Bopomofo links -> Medicine links -> Medicine data
    '''
    

    def __init__(self, med_type: str) -> None:
        '''med_type: "yao" or "fang"'''
        self.temp_file = Path('./json/temp.json') # Handy...
        self.med_type = med_type
        self.base_url = 'http://yibian.hopto.org'
        self._session = CachedSession('http_cache', backend='sqlite')
    
    
    def get_html(self, url: str) -> str:
        response = self._session.get(url)
        self._session.close()
        return response.content
    

    def get_bopomofo_links(self, dst: Path) -> None:
        '''
        get links from a bopomofo page
        >> save it to json file
        '''
        a_tag_attr = 'sn'
        url = f'{self.base_url}/{self.med_type}/?mn=bop'
        soup = BeautifulSoup(self.get_html(url), 'html.parser')
        
        links = [link for link in soup.findAll('a') if a_tag_attr in str(link)]
        bop_links = {l.get_text(): l.get('href') for l in links}

        assert soup is not None,  f'Err: Could not find the Webpage!'
        assert links != False, 'Err: No links!'
        JsonHandler(dst).write(bop_links)
    

    def get_med_links(self, dst: Path, bop: str, url: str) -> None:
        '''
        depends on bopomofo links
        scrape medicine links from each bopomofo page.

        :param bop: bopomofo
        :param url: .?mn=bop&sn=9
        :rtype: None
        '''
        url = f'{self.base_url}/{self.med_type}/{url}'
        soup = BeautifulSoup(self.get_html(url), 'html.parser')
        a_tag_attr = '?fno' if self.med_type == 'fang' else '?yno'
        links = [link for link in soup.findAll('a') if a_tag_attr in str(link)]
        parent_links = [link.parent for link in soup.findAll('a') if a_tag_attr in str(link)]
        med_links = {pl.get_text(): l.get('href') for pl, l in zip(parent_links, links)}
        JsonHandler(dst).write({bop: med_links})
        assert soup is not None,  'Err: Could not find the Webpage!'
        assert links != False, 'Err: No links!'


    def get_med_data(self) -> Dict[str, str]:
        '''Get medicine data'''
        pass


class ScFangMedicine(BaseMedScrape):


    def __init__(self) -> None:
        super().__init__('fang')
        self.fang_med_links_file = Path('./json/fang_med_links.json')
        self.fang_bop_links_file = Path('./json/fang_bop_links.json')
        self.fang_data_file = Path('./json/fang_data.json')


    def get_med_data(self, url: str) -> Dict[str, str]:
        '''
        url: .?mn=bop&sn=9
        '''
        med_info = {}
        url = f'{self.base_url}/{self.med_type}/{url}'
        soup = BeautifulSoup(self.get_html(url), 'html.parser')
        s = soup.find('td', attrs={'class':'content_board'})
        head = s.find('table')
        head = [i.getText() for i in head.find('tr').findAll(('td', 'th'))]
        
        med_info.update({head[0]: head[1]})
        med_info.update({head[3]: head[4]})
    
        titles = re.findall(r'【.*?】',  s.text.strip())
        text_infs = re.split(r'【.*?】', s.text.strip())[1:]

        for title, info in zip(titles, text_infs):
            title = title[1:-1] 
            if title == '主治':
                info = info.split('2017')[0] # Exclude an ad..
            elif title == titles[-1][1:-1]: # strip bottom text
                info = info.split('頁首')[0].strip()
            med_info.update({title: info})
        return med_info

    
    def get_data(self):
        '''Run this before you sleep!'''
        bop_links = JsonHandler(self.fang_bop_links_file).read()
        if not bop_links: # Empty
            self.get_bopomofo_links(self.fang_bop_links_file)
            bop_links = JsonHandler(self.fang_bop_links_file).read()
        
        for key, val in bop_links.items():
            self.get_med_links(self.fang_med_links_file, key, val)
            
            time.sleep(3) # ---- Wait a bit
            WAIT_FOR_IT = True # --- Wait >> Avoid blocking 
            WAIT_FOR_SEC = 100 # --- Wait
            l_dict = JsonHandler(self.fang_med_links_file).read()
            for key, val in l_dict.items():
                med_data = {}
                WAIT_FOR_THIS = 0
                for _key, _val in val.items():
                    med_data.update({_key: self.get_med_data(_val)})
                    print(_key)
                    if WAIT_FOR_THIS == 3 and WAIT_FOR_IT:
                        WAIT_FOR_THIS = 0
                        time.sleep(random.randint(20,60))
                    WAIT_FOR_THIS += 1
                JsonHandler(self.fang_data_file).update(key, med_data)
            if WAIT_FOR_IT:
                time.sleep(WAIT_FOR_SEC)


class ScYaoMedicine(BaseMedScrape):
    
    def __init__(self) -> None:
        super().__init__('yao')
        self.yao_med_links_file = Path('./json/yao_med_links.json')
        self.yao_bop_links_file = Path('./json/yao_bop_links.json')
        self.yao_data_file = Path('./json/yao_data.json')
    

    def get_med_data(self, url: str) -> Dict[str, str]:
        '''
        url: .?mn=bop&sn=9
        '''

        med_info = {}
        url = f'{self.base_url}/{self.med_type}/{url}'
        
        soup = BeautifulSoup(self.get_html(url), 'html.parser')
        s = soup.find('td', attrs={'class':'content_board'})
        head = s.find('table')
        head = [i.getText() for i in head.find('tr').findAll(('td', 'th'))]
        med_info.update({head[0]: head[1].split()[0]})
        try:
            med_info.update({head[2]: head[3]})
        except IndexError as e:
            pass
        finally:
            titles = re.findall(r'【.*?】',  s.text.strip())
            text_infs = re.split(r'【.*?】', s.text.strip())[1:]

            for title, info in zip(titles, text_infs):
                title = title[1:-1] 
                if title == '主治':
                    info = info.split('2017')[0] # Exclude an ad..
                elif title == titles[-1][1:-1]: # strip bottom text
                    info = info.split('頁首')[0].strip()
                med_info.update({title: info})
            return med_info


    def get_data(self):
        '''Run this before you sleep!'''
        bop_links = JsonHandler(self.yao_bop_links_file).read()
        if not bop_links: # Empty
            self.get_bopomofo_links(self.yao_bop_links_file)
            bop_links = JsonHandler(self.yao_bop_links_file).read()
        
        for key, val in bop_links.items():
            self.get_med_links(self.yao_med_links_file, key, val)
            time.sleep(3) # ---- Wait a bit
            WAIT_FOR_IT = True # --- Wait >> Avoid blocking 
            WAIT_FOR_SEC = 100 # --- Wait
            l_dict = JsonHandler(self.yao_med_links_file).read()

            for key, val in l_dict.items():
                med_data = {}
                WAIT_FOR_THIS = 0
                for _key, _val in val.items():
                    med_data.update({_key: self.get_med_data(_val)})
                    if WAIT_FOR_THIS == 3 and WAIT_FOR_IT:
                        WAIT_FOR_THIS = 0
                        time.sleep(random.randint(20,60))
                    WAIT_FOR_THIS += 1
                JsonHandler(self.yao_data_file).update(key, med_data)
            if WAIT_FOR_IT:
                time.sleep(WAIT_FOR_SEC)
    
    def test(self):
        print('[Running Test...]')
        from pprint import pprint
        pprint(self.get_med_data('.?yno=639'))
        


if __name__ == '__main__':
    pass