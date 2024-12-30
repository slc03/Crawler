from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class CSCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤计算机科学与技术学院"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://cs.ustc.edu.cn/20181/list.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://cs.ustc.edu.cn'
        li_list = etree.xpath('//*[@id="wp_content_w6_0"]/p')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("a/text()") or not li.xpath("a"):
                continue
            
            file_name = li.xpath("a/text()")[0]
            file_url = li.xpath("a")[0].attrib.get('href')
            
            file_url = base_url + file_url
            file_ass = self._build_ass(file_url)
            file_asses.append(file_ass)
            file_names.append(file_name)
                
        return file_asses, file_names
        