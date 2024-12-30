from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple

import re


class SSECrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤软件学院"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            # 'https://sse.ustc.edu.cn/zcwj/list.htm',
            'https://sse.ustc.edu.cn/19878/list.htm',
            'https://sse.ustc.edu.cn/19879/list.htm',
            'https://sse.ustc.edu.cn/19880/list.htm',
            'https://sse.ustc.edu.cn/19882/list.htm',
            'https://sse.ustc.edu.cn/19884/list.htm',
            'https://sse.ustc.edu.cn/19885/list.htm',
            'https://sse.ustc.edu.cn/19740/list.htm',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://sse.ustc.edu.cn'
        page_count = int(etree.xpath(f'//*[@id="wp_paging_w6"]/ul/li[1]/span[2]/em/text()')[0])
        file_asses, file_names = list(), list()
        
        for i in range(1, page_count+1):
            anchor = etree.xpath(f'//*[@id="wp_news_w6"]/ul/li[{i}]/div[1]/span[2]/a')
            if anchor:
                file_name = anchor[0].attrib.get('title')
                clean_filename = re.sub(r'\s*\[\d{4}-\d{2}-\d{2}\]\s*$', '', file_name)
                
                href = anchor[0].attrib.get('href')
                file_url = base_url + href
                file_ass = self._build_ass(file_url)
                
                file_asses.append(file_ass)
                file_names.append(clean_filename)
        
        return file_asses, file_names