"""
It's the basic class of Crawler program
"""

from typing import List, Optional, Literal, Tuple, Callable
from dataclasses import asdict, dataclass
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from lxml import etree
from tqdm import tqdm
import os
import json
import logging
import requests
import threading


@dataclass
class DataContent:
    """
    Basic properties for raw dataset.\n
    Notice that file storage location can be obtained from 'file_type' and 'file_name'.
    """
    source_url: str
    source_name: str
    create_time: str
    file_type: str
    file_name: str
    

class BaseCrawl(ABC):
    r"""Any class inherited from this class should overwrite attribute [name, target_urls] and method [etree_to_ass]."""
    def __init__(self, output_dir: str, log_dir: Optional[str]=None, max_attempt: int=3, headers: Optional[str]=None, timeout: int=3) -> None:
        r"""output_dir should be given, and log_dir is suggested to be given"""
        self.output_dir = output_dir
        self.max_attempt = max_attempt
        self.headers = headers
        self.timeout = timeout
        self.lock = threading.Lock()
        
        self._init_logger(log_dir)
    
    def _init_logger(self, log_dir: Optional[str]):
        r"""init Logger module"""
        self.logger = logging.getLogger(f"{self.name}-LOGGER")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if log_dir is not None:
            file_handler = logging.FileHandler(log_dir, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
        
    def _build_ass(self, url: str, params: Optional[dict]=None) -> dict:
        r"""construct dictionary which send to requests"""
        ass = {
            'url': url,
            'timeout': self.timeout
        }
        if self.headers is not None:
            ass['headers'] = self.headers
        if params is not None:
            ass['params'] = params
        return ass
        
    def _request_get(self, ass: dict, count: int=1, types: Literal['raw', 'etree']='etree') -> Optional[etree._Element]:
        r"""send requests to defined url"""
        try:
            content = requests.get(**ass)
            content.raise_for_status()
        except:
            if count > self.max_attempt:
                self.error_links.append(ass['url'])
                return None
            return self._request_get(ass, count+1, types)
        if types == 'raw':
            return content.content
        elif types == 'etree':
            content.encoding = 'utf-8'
            return etree.HTML(content.text)
        else:
            raise NameError(f"types must be in ['raw', 'etree'], but got {types}.")
    
    def _more_thread_get(self, task: Callable, asses: List[dict], others: List[dict]=list(), max_workers: Optional[int]=None, use_tqdm: bool=True):
        r"""send requests using multi threads"""
        assert len(others) == len(asses) or len(others) == 0
        if len(others) == 0:
            others = [dict() for _ in asses]
            
        future_result = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for ass, other in zip(asses, others):
                future = executor.submit(task, ass, **other)
                future_result[future] = ass['url']
            
            if use_tqdm:
                iteration = tqdm(as_completed(future_result), total=len(self.target_urls), desc=self.name)
            else:
                iteration = as_completed(future_result)
                
            for future in iteration:
                url = future_result[future]
                try:
                    result = future.result()
                except Exception as exc:
                    self.logger.warning(f'{url} generated an exception: {exc}')
    
    @property
    @abstractmethod
    def name(self) -> str:
        r"""the description of class"""
        return str()
    
    @property
    @abstractmethod
    def target_urls(self) -> List[str]:
        r"""root urls that will be visit"""
        return list()
    
    @abstractmethod
    def etree_to_ass(self, etree: etree._Element) -> Tuple[List[dict], List[str]]:
        r"""according to etree, get file addresses and filenames"""
        return list(), list()
    
    def process_file(self, ass: dict, filename: str, force_download: bool=False):
        r"""task for download raw file"""
        suffix = Path(filename).suffix
        if suffix:
            output_dir = os.path.join(self.output_dir, suffix+'/')
        else:
            # don't support file with no suffix any more
            # output_dir = os.path.join(self.output_dir, '.unk/')
            return
        os.makedirs(output_dir, exist_ok=True)
        output_dir = os.path.join(output_dir, filename)

        if os.path.exists(output_dir) and not force_download:
            self.logger.info(f"file has already been downloaded: {filename}")
            return
        
        content = self._request_get(ass, types='raw')
        if content is None:
            return
        
        with self.lock:
            if os.path.exists(output_dir) and not force_download:
                self.logger.info(f"file has already been downloaded: {filename}")
                return
            
            with open(output_dir, 'wb') as file:
                file.write(content)
                
            data = DataContent(ass['url'], 
                            self.name,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                            suffix, 
                            filename)

            dataset_dir = os.path.join(self.output_dir, 'dataset_info.json')
            if os.path.isfile(dataset_dir):
                with open(dataset_dir, 'r', encoding='utf-8') as fp:
                    dataset_info = json.load(fp)
            else:
                dataset_info = list()
            dataset_info.append(asdict(data))
            with open(dataset_dir, 'w', encoding='utf-8') as fp:
                json.dump(dataset_info, fp, ensure_ascii=False, indent=2)
        
            self.logger.info(f"file download successfully: {filename}")
        
    def process_ass(self, ass: dict):
        """Helper function to process a single URL."""
        etree = self._request_get(ass)
        if etree is not None:
            asses, filenames = self.etree_to_ass(etree)
            if asses and filenames:
                others = [{'filename': filename} for filename in filenames]
                self._more_thread_get(self.process_file, asses, others, use_tqdm=False)
                
    def delete_empty_dirs(self):
        """delete empty directory which is created wrongly"""
        for dirpath, dirnames, filenames in os.walk(self.output_dir, topdown=False):
            for dirname in dirnames:
                dir_to_check = os.path.join(dirpath, dirname)
                if not os.listdir(dir_to_check):
                    self.logger.info(f"Deleting empty directory: {dir_to_check}")
                    os.rmdir(dir_to_check)
    
    def run(self):
        r"""workflow, also the interface"""
        self.error_links = []
        
        self.logger.info(f"[{self.name}] Start crawling files...")

        target_asses = [self._build_ass(url) for url in self.target_urls]
        self._more_thread_get(self.process_ass, target_asses)

        if self.error_links:
            self.logger.error(f"[{self.name}] There are links failed below:")
            for link in self.error_links:
                self.logger.error(link)
        
        self.delete_empty_dirs()
        self.logger.info(f"[{self.name}] Completed crawling files!")
            