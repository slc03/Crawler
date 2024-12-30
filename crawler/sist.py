from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class SISTCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤信息科学技术学院"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://sist.ustc.edu.cn/5111/list.htm',
            'https://sist.ustc.edu.cn/5111/list2.htm',
            'https://sist.ustc.edu.cn/5111/list3.htm',
            'https://sist.ustc.edu.cn/5104/list.htm',
            'https://sist.ustc.edu.cn/5128/list.htm',
            'https://sist.ustc.edu.cn/5095/list.htm',
            'https://sist.ustc.edu.cn/5095/list2.htm',
            'https://sist.ustc.edu.cn/5079/list.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://sist.ustc.edu.cn'
        li_list = etree.xpath('//*[@id="recent-posts"]/div/div[2]/div[1]/div')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("div/div[2]/h5/a/text()") or not li.xpath("div/div[2]/h5/a"):
                continue
            
            first_name = li.xpath("div/div[2]/h5/a/text()")[0]
            first_url = li.xpath("div/div[2]/h5/a")[0].attrib.get('href')
            suffix = Path(first_url).suffix
            
            if suffix == '.htm':
                first_url = base_url + first_url
                first_ass = self._build_ass(first_url)
                sub_etree = self._request_get(first_ass)
                
                if sub_etree is None:
                    continue
                sub_anchor = sub_etree.xpath(f'//*[@id="blog"]/div/div/div[1]/article/div[2]/div')
                if not sub_anchor:
                    continue
                anchor = sub_anchor[0]
                target_list = ['a', 'p/a', 'p/a[2]']
                for target in target_list:
                    if anchor.xpath(f'{target}/text()') and anchor.xpath(f'{target}')[0].attrib.get('href'):
                        second_name = anchor.xpath(f'{target}/text()')[0]
                        second_url = anchor.xpath(f'{target}')[0].attrib.get('href')
                        
                        sub_suffix = Path(second_url).suffix
                        if sub_suffix in ['', 'gif']:
                            continue
                
                        second_url = base_url + second_url
                        second_ass = self._build_ass(second_url)
                        file_asses.append(second_ass)
                        file_names.append(second_name)
                
        return file_asses, file_names
        