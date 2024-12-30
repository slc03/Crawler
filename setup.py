import argparse
from typing import Optional
from crawler import *

CRAWLERS = [
    SSECrawl,
    TEACHCrawl,
    GRADSCHOOLCrawl,
    BWCCrawl,
    PRESSCrawl,
    ISPCCrawl,
    ZHCCrawl,
    CSCrawl,
    CYBERSECCrawl,
    SISTCrawl,
    IATCrawl,
    HRCrawl,
]

def main(output_dir: str, log_dir: Optional[str]):
    print("开始爬取文件...")
    for crawler_cls in CRAWLERS:
        craw = crawler_cls(output_dir=output_dir, log_dir=log_dir)
        craw.run()
    print("爬取完毕!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawler Program")
    parser.add_argument('--output_dir', type=str, required=True, help="输出目录")
    parser.add_argument('--log_dir', type=str, default=None, help="日志文件目录")

    args = parser.parse_args()
    
    main(args.output_dir, args.log_dir)
