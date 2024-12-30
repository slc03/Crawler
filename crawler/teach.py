from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple

import re


class TEACHCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤教务处"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            f'https://www.teach.ustc.edu.cn/download/all/page/{i}'
            for i in range(1, 16)
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        file_asses, file_names = list(), list()
        
        anchor = etree.xpath(f'/html/body/div[6]/div/main/section/div[1]/ul/li')
        for anc in anchor:
            matches = re.search(r'post-(\d+)', anc.attrib.get('class'))
            if not matches:
                continue
            
            attachment_id = matches.group(1)
            first_url = f'https://www.teach.ustc.edu.cn/?attachment_id={attachment_id}'  
            first_ass = self._build_ass(first_url)
            sub_etree = self._request_get(first_ass)
            
            if sub_etree is None:
                continue
            sub_anchor = sub_etree.xpath(f'//*[@id="post-{attachment_id}"]/a')
            if sub_anchor:
                file_name = sub_anchor[0].attrib.get('download')
                second_url = sub_anchor[0].attrib.get('href')
                second_ass = self._build_ass(second_url)
                
                file_asses.append(second_ass)
                file_names.append(file_name)
        
        return file_asses, file_names