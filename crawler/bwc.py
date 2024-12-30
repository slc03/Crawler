from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class BWCCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤保卫与校园管理处"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://bwc.ustc.edu.cn/5655/list.htm',
            'https://bwc.ustc.edu.cn/5655/list2.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://bwc.ustc.edu.cn'
        li_list = etree.xpath('//*[@id="article"]/div/div[1]/ul/li')
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
                for end in ['div/a', 'div/p/a']:
                    sub_anchor = sub_etree.xpath(f'/html/body/section[2]/div/div[1]/div[2]/div/p/span/{end}')
                    if not sub_anchor:
                        continue
                    for anchor in sub_anchor:
                        second_name = anchor.xpath('text()')[0]
                        second_url = anchor.attrib.get('href')
                        second_url = base_url + second_url
                    
                        second_ass = self._build_ass(second_url)
                        file_asses.append(second_ass)
                        file_names.append(second_name)
                
        return file_asses, file_names
        