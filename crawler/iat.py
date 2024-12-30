from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class IATCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤先进技术研究院"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://iat.ustc.edu.cn/iat/x119/',
            'https://iat.ustc.edu.cn/iat/wdxz/',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://iat.ustc.edu.cn'
        li_list = etree.xpath('/html/body/div[5]/div/div[2]/div[2]/div[1]/ul/li')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("a"):
                continue

            first_url = li.xpath("a")[0].attrib.get('href')
            suffix = Path(first_url).suffix
            
            if suffix == '.html':
                first_ass = self._build_ass(first_url)
                sub_etree = self._request_get(first_ass)
                
                if sub_etree is None:
                    continue
                sub_anchor = sub_etree.xpath(f'/html/body/div[5]/div/div[2]/div[2]/div/div[3]/p')
                if not sub_anchor:
                    continue
                for anchor in sub_anchor:
                    if anchor.xpath('a'):
                        if anchor.xpath('a')[0].attrib.get('title') and anchor.xpath('a')[0].attrib.get('href'):
                            second_name = anchor.xpath('a')[0].attrib.get('title')
                            second_url = anchor.xpath('a')[0].attrib.get('href')
                
                            second_url = base_url + second_url
                            second_ass = self._build_ass(second_url)
                            file_asses.append(second_ass)
                            file_names.append(second_name)
                
        return file_asses, file_names
        