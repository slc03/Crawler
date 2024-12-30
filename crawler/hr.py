from .crawler import BaseCrawl

from lxml import etree
from typing import List, Tuple
from pathlib import Path

import re


class HRCrawl(BaseCrawl):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    @property
    def name(self):
        return "中科⼤人力资源部"
    
    @property
    def target_urls(self) -> List[str]:
        return [
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333201875000015',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333312031250019',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333402187500023',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333571562500035',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=635920107585781004',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333745781250043',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=635465475215000082',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=638294129081856011',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=637824241762067020',
            'https://hr.ustc.edu.cn/cn/wendang.aspx?infotypeid=841333910000000051',
        ]
        
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        base_url = 'https://hr.ustc.edu.cn/cn/'
        li_list = etree.xpath('//*[@id="oInfoContent"]/table/tr')
        file_asses, file_names = list(), list()

        for li in li_list:
            if not li.xpath("td[2]/span/text()") or not li.xpath("td[2]/span")[0].attrib.get('onclick'):
                continue

            file_name = li.xpath("td[2]/span/text()")[0]
            full_url = li.xpath("td[2]/span")[0].attrib.get('onclick')
            
            pattern = r"window\.open\('([^']+)'\s*,"
            match = re.search(pattern, full_url)

            if match:
                file_url = match.group(1)
                if file_url.startswith('personnel/uploadfile'):
                    file_url = base_url + file_url
                suffix = Path(file_url).suffix
        
                file_name = file_name + suffix
                file_ass = self._build_ass(file_url)
                file_asses.append(file_ass)
                file_names.append(file_name)
                
        return file_asses, file_names
        