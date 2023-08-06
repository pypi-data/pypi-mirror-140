# OncoPlot Extractor

![Build status](https://github.com/regmibijay/oncoplot-extractor/actions/workflows/main.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/oncoplot-extractor.svg)](https://badge.fury.io/py/oncoplot-extractor)

## About

OncoPlot Extractor provides python3.x library to read standard oncoplots also known as mutation matrix. This library allows you to export the data extracted as pandas.DataFrame so the data can be forth modified with toolkit offered by pandas. Two main modules that this package contains are OncoPlotExtractor and OncoPlotCreator.

## Installation

Please install this library with python pip as

```bash
$ pip3 -U install oncoplot-extractor
```

## Documentation

You can find extensive documentation [here](https://regdelivery.de/oncoplot-extractor)

## Usage

### OncoPlot Extractor

```python3
from oncoplot_extractor import OncoPlotExtractor

oce = OncoplotExtractor(
    path="path/to/oncoplot.png", # path to oncoplot image
    corners=(0,0,100,100), # corners are optional
    background_color=["#ffffff"] # you can also use oce.get_background_from_pixel()
    )
oce.extract()
oce.export_to_excel("path/to/oncoplot.xlsx")
```

### OncoPlot Creator

```python3
import pandas as pd
from oncoplot_extractor import OncoPlotCreator

df = pd.DataFrame(my_data)
opc = OncoPlotCreator(df=my_df, cell_size=60, workbook=wb, offset=10)
opc.gen_base_oncoplot()
opc.save(filename="my_oncoplot.xlsx")

```

## Contribution

This project is very amateur and I hope to help someone who might have ran into problem of getting one image or pdf as oncoplot and needing the actual data. If it helped you or have suggestions, please let me know.

I would really appreciate your contributions and I will get to the PRs as soon as possible.
