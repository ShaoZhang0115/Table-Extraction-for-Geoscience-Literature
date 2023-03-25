# Table-Extraction-for-Geoscience-Literature

Here is a system for table extraction from literature. Our models are specifivally trained at the geoscience literature, but can also process the literature from other areas.

## Installation

### Docker

It is recommended to install using a Docker container.

model Url: [https://layoutlm.blob.core.windows.net/tablebank/model_zoo/detection/All_X152/model_final.pth](https://layoutlm.blob.core.windows.net/tablebank/model_zoo/detection/All_X152/model_final.pth)

Download the model and put it in the `docker/table-outline-server/table_outline/`

We provide a docker-compose.yml configuration file. Clone this repository and execute docker-compose up -d to start the container.

## Demo
The Demo is available at https://ddescholar.acemap.info/table-extraction

## Citation
Our Paper
```
@article{https://doi.org/10.1002/gdj3.186,
author = {Zhang, Shao and Xu, Hui and Jia, Yuting and Wen, Ying and Wang, Dakuo and Fu, Luoyi and Wang, Xinbing and Zhou, Chenghu},
title = {GeoDeepShovel: A platform for building scientific database from geoscience literature with AI assistance},
journal = {Geoscience Data Journal},
volume = {n/a},
number = {n/a},
pages = {},
keywords = {artificial intelligence, big data-driven discovery, data extraction, scientific database, human-computer interaction},
doi = {https://doi.org/10.1002/gdj3.186},
url = {https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/gdj3.186},
eprint = {https://rmets.onlinelibrary.wiley.com/doi/pdf/10.1002/gdj3.186}
}


```
This Repo
```
@misc{[Table-Extraction-for-Geoscience-Literature],
    title={Table Extraction for Geoscience Literature},
    author={Shen, Yifei and Li, Qi and Zhang, Shao and Guo, Jia and Shi, Tao and Jia, Yuting and Wen, Ying and Wang, Xinbing},
    booktitle={GitHub},
    year={2023},
    url={https://github.com/ShaoZhang0115/Table-Extraction-for-Geoscience-Literature}
}
```
