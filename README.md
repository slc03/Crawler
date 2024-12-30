## 环境准备

推荐linux ubuntu或windows平台，python>=3.7

```shell
pip install -r requirements.txt
```

## 快速开始

使用下面的命令爬取文件

```shell
python setup.py --output_dir raw_dataset --log_dir run.log
```

## 主要介绍

- 爬到的数据按照文件类型（后缀名）分别存储
- dataset_info.json中记录了所有文件的信息