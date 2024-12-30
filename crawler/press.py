from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class PRESSCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤出版社"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://press.ustc.edu.cn/tgxz/list.htm',
            'https://press.ustc.edu.cn/xtxxb/list.htm',
            'https://press.ustc.edu.cn/bzgf/list.htm',
            'https://press.ustc.edu.cn/wjfg/list.htm',
            'https://press.ustc.edu.cn/jxzy/list.htm',
            'https://press.ustc.edu.cn/jxzy/list2.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://press.ustc.edu.cn'
        li_list = etree.xpath('//*[@id="wp_news_w5"]/div')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("h2/a/text()") or not li.xpath("h2/a"):
                continue
            
            first_name = li.xpath("h2/a/text()")[0]
            first_url = li.xpath("h2/a")[0].attrib.get('href')
            suffix = Path(first_url).suffix
            
            if suffix == '.htm':
                first_url = base_url + first_url
                first_ass = self._build_ass(first_url)
                sub_etree = self._request_get(first_ass)
                
                if sub_etree is None:
                    continue
                sub_anchor = sub_etree.xpath(f'//*[@id="node-3411"]/div/div/div/div/div[2]/div/p')
                if not sub_anchor:
                    continue
                for anchor in sub_anchor:
                    if anchor.xpath('a/text()') and anchor.xpath('a')[0].attrib.get('href'):
                        second_name = anchor.xpath('a/text()')[0]
                        second_url = anchor.xpath('a')[0].attrib.get('href')
                    elif anchor.xpath('span/a/text()') and anchor.xpath('span/a')[0].attrib.get('href'):
                        second_name = anchor.xpath('span/a/text()')[0]
                        second_url = anchor.xpath('span/a')[0].attrib.get('href')
                    else:
                        continue
                        
                    # part files are too large, so we filter them (such as .mp4 and .rar)
                    sub_suffix = Path(second_url).suffix
                    if sub_suffix in ['.mp4', '.rar']:
                        continue
            
                    second_url = base_url + second_url
                    second_ass = self._build_ass(second_url)
                    file_asses.append(second_ass)
                    file_names.append(second_name)
                
        return file_asses, file_names
        