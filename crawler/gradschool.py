from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class GRADSCHOOLCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤研究生院"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            f'https://gradschool.ustc.edu.cn/column/{i}'
            for i in range(1, 256)
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://gradschool.ustc.edu.cn'
        li_list = etree.xpath('/html/body/div[1]/div/section/div/div[2]/ul/li')
        file_asses, file_names = list(), list()
        
        for li in li_list:
            if not li.xpath("a/text()") or not li.xpath("a"):
                break
            
            raw_filename = li.xpath("a/text()")[0]
            raw_fileurl = li.xpath("a")[0].attrib.get('href')
            
            suffix = Path(raw_fileurl).suffix
            
            # because fileurl with no suffix is mainly .html
            if suffix:
                file_name = raw_filename + suffix
                file_url = base_url + raw_fileurl
                
                file_ass = self._build_ass(file_url)
                
                file_asses.append(file_ass)
                file_names.append(file_name)
                
        return file_asses, file_names
        