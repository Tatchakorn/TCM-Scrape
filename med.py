import json
import re
from typing import Dict
import requests
import random
import time
from pathlib import Path
from bs4 import BeautifulSoup

com_med_links_path = Path('./json/com_med_links.json')
single_med_links_path = Path('./json/single_med_links.json')
com_med_bop_links_path = Path('./json/com_med_bop_links.json')
single_med_bop_links_path = Path('./json/single_med_bop_links.json')
com_meds_path = Path('./json/com_meds.json')
single_meds_path = Path('./json/single_meds.json')
test_json = Path('./json/test_json.json')
temp_json_path = Path('./json/temp.json')


def get_links_from_char(dst_json: Path, sub_url:str) -> None:
    '''
    sub_url: "yao" or "fang"
    '''
    url = f'http://yibian.hopto.org/{sub_url}/?mn=bop'
    soup = BeautifulSoup(get_html(url), 'html.parser')

    s = soup.find('td', attrs={'class':'db_lft_mnu_board'})
    s = s.findAll('font', attrs={'class':'db_lft_mnu_fnt'})
    s = (i.parent for i in s)

    ch_links = {i.font.getText(): i['href'] for i in s}
    with open(dst_json, 'w', encoding='utf-8') as f:
        json.dump(ch_links, indent=4, sort_keys=True, fp=f, ensure_ascii=False)


def new_get_links_from_char(dst_json: Path, sub_url:str) -> None:
    '''
    sub_url: "yao" or "fang"
    '''
    url = f'http://yibian.hopto.org/{sub_url}/?mn=bop'
    soup = BeautifulSoup(get_html(url), 'html.parser')

    links = [link for link in soup.findAll('a') if '?fno' in str(link)]
    ch_links = {l.get_text(): l.get('href') for l in links}
    with open(dst_json, 'w', encoding='utf-8') as f:
        json.dump(ch_links, indent=4, sort_keys=True, fp=f, ensure_ascii=False)



def get_meds(sub_url: str, sub_url_2: str) -> Dict[str, str]:
    '''
    sub_url: "yao" or "fang"
    url: .?mn=bop&sn=9
    '''
    url = f'http://yibian.hopto.org/{sub_url}/{sub_url_2}'
    soup = BeautifulSoup(get_html(url), 'html.parser')
    links = [link for link in soup.findAll('a') if '?fno' in str(link)]
    parent_links = [link.parent for link in soup.findAll('a') if '?fno' in str(link)]
    return  {pl.get_text(): l.get('href') for pl, l in zip(parent_links, links)}


def get_med_data(sub_url: str, sub_url_2: str) -> Dict[str, str]:
    '''
    sub_url: "yao" or "fang"
    url: .?mn=bop&sn=9
    '''
    med_info = {}
    url = f'http://yibian.hopto.org/{sub_url}/{sub_url_2}'
    soup = BeautifulSoup(get_html(url), 'html.parser')
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


def get_html(url: str) -> str:
    with requests.Session() as s:
        content = s.get(url).content
    return content


def links_to_bop(src_json: Path, dst_json: Path, sub_url: str) -> None:
    '''
    sub_url: "yao" or "fang"
    '''
    
    with open(src_json, 'r', encoding='utf-8') as f:
        meds_links = dict(json.loads(f.read()))
        med_bop_links = {}
        for key, val in meds_links.items():
            med_bop_links.update({key: get_meds(sub_url, val)})
            print(f'[GET] {key} {val}')
            time.sleep(random.randint(30,60))
        with open(dst_json, 'w', encoding='utf-8') as f:
            json.dump(med_bop_links, indent=4, sort_keys=True, fp=f, ensure_ascii=False)


def json_med_data(src_json: Path, dst_json: Path, sub_url: str) -> None:
     '''
    sub_url: "yao" or "fang"
    '''
     with open(src_json, 'r', encoding='utf-8') as f:
        meds_links = dict(json.loads(f.read()))
        
        for key, val in meds_links.items():
            print(f'{key}: {len(val.items())}')
            # for _key, _val in val.items():
            #     ...

def man_links_to_bop(dst_json: Path, sub_url: str, sub_url_1: str, key: str) -> None:
    '''
    sub_url: "yao" or "fang"
    '''


    with open(dst_json, 'w', encoding='utf-8') as f:
        json.dump({key: get_meds(sub_url, sub_url_1)}, indent=4, sort_keys=True, fp=f, ensure_ascii=False)


def man_json_med_data():
    # KEY = 'ㄅ'
    # KEY = 'ㄆ'
    # KEY = 'ㄇ'
    # KEY = 'ㄈ'
    # KEY = 'ㄉ'
    # --- FIXED KEYS
    # KEY = 'ㄊ'
    # KEY = 'ㄋ'
    # KEY = 'ㄍ'
    # KEY = 'ㄐ'
    # _url_ = '.?mn=bop&sn=12'
    links = read_json(com_med_links_path)
    for key, val in links.items():
        print(key, val)
        KEY = key
        _url_ = val
        # ---------- SWITCH ----------
        # ---------- RECORD ----------
        man_links_to_bop(temp_json_path, 'fang', _url_, KEY)
        # ---------- SWITCH ----------
        time.sleep(3)
        WAIT_FOR_IT = True
        WAIT_FOR_SEC = 100
        with open(temp_json_path, 'r', encoding='utf-8') as f:
            l_dict = dict(json.loads(f.read()))
            for key, val in l_dict.items():
                med_data = {}
                THREE_TIMES = 0
                for _key, _val in val.items():
                    med_data.update({_key: get_med_data('fang', _val)})
                    print(_key)
                    if THREE_TIMES == 3 and WAIT_FOR_IT:
                        THREE_TIMES = 0
                        time.sleep(20)
                        time.sleep(random.randint(30,60))
                    THREE_TIMES += 1
                    
                with open(test_json, 'w', encoding='utf-8') as f:
                    json.dump({key: med_data}, indent=4, sort_keys=True, fp=f, ensure_ascii=False)
                    update_json('./test_com_db.json', KEY, med_data)
        time.sleep(WAIT_FOR_SEC)
                
def read_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        j = dict(json.loads(f.read()))
    return j

def update_json(path: Path, key: str, val: any):
    with open(path, 'r', encoding='utf-8') as f:
        data = dict(json.loads(f.read()))

    data[key] = val

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, indent=4, sort_keys=True, fp=f, ensure_ascii=False)

def read_char():
    char_d = read_json(test_json)
    for key, val in char_d.items():
        for _key, _val in val.items():
            print(_key)

if __name__ == '__main__':
    man_json_med_data()
    # read_char()
    # json_links_(single_med_links_path, single_med_bop_links_path, 'yao')



# def super_scrape_medicine():
#     url = 'http://yibian.hopto.org/fang/?mn=bop'
#     soup = BeautifulSoup(get_html(url), 'html.parser')

#     s = soup.find('td', attrs={'class':'db_lft_mnu_board'})
#     s = s.findAll('font', attrs={'class':'db_lft_mnu_fnt'})

#     s_ch_parent = [i.parent for i in s] # each key is nested    
#     bapomofo_urls = (i['href'] for i in s_ch_parent)
#     bapomofo_chars = (i.font.getText() for i in s_ch_parent)
    
#     zh_medicine = {}
#     for url, bpmf_char in zip(bapomofo_urls, bapomofo_chars):
#         zh_medicine_data = {}
#         try: 
#             med_names = get_meds(url)
#         except:
#             continue
#         for name, sub_url in med_names.items():
#             try:
#                 zh_medicine_data.update({name: get_med_data(sub_url)})
#             except:
#                 continue
#         zh_medicine.update({bpmf_char: zh_medicine_data})
#         break

#     with open('./json/temp.json', 'w', encoding='utf-8') as f:
#         json.dump(zh_medicine, indent=4, sort_keys=False, fp=f, ensure_ascii=False)