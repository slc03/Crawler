from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class ISPCCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤信息科学实验中心"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://ispc.ustc.edu.cn/6299/list.htm',
            'https://ispc.ustc.edu.cn/6298/list.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://ispc.ustc.edu.cn'
        li_list = etree.xpath('//*[@id="wp_news_w6"]/li')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("a/text()") or not li.xpath("a"):
                continue
            
            first_name = li.xpath("a/text()")[0]
            first_url = li.xpath("a")[0].attrib.get('href')
            suffix = Path(first_url).suffix
            
            if suffix == '.htm':
                first_url = base_url + first_url
                first_ass = self._build_ass(first_url)
                sub_etree = self._request_get(first_ass)
                
                if sub_etree is None:
                    continue
                sub_anchor = sub_etree.xpath('/html/body/table[4]/tr/td[2]/div[2]/table/tr[4]/td/span/div/a')
                if sub_anchor and sub_anchor[0].attrib.get('href'):
                    second_name = sub_anchor[0].xpath('text()')[0]
                    second_url = sub_anchor[0].attrib.get('href')
            
                    second_url = base_url + second_url
                    second_ass = self._build_ass(second_url)
                    file_asses.append(second_ass)
                    file_names.append(second_name)
                
        return file_asses, file_names
        