# Graph Drawer

## Overview

`Graph Drawer` is Web application to draw the graph automatically.  
The file format is supported in `csv`.

## Environment (confirmed operation)

- WSL2 (Windows11)
- Ubuntu 22.04.1 LTS (Jammy Jellyfish)
- docker-compose version 1.29.2

## How to use

```
./run.sh
```

Access to `http://localhost:5000` in your browser.

### Execution sample using `sample_data/sample1/sample.csv`

![GraphDrawer Demo](./figures/GraphDrawer-Demo.gif)

### Sample data

#### [sapmle1](./sample_data/sample1/)

`csv`file only.

#### [sample2_iris](./sample_data/sample2_iris/)

```
docker-compose exec sample_data bash
cd sample2_iris
python create_iris_csv.py 
```

#### [sample3_tokyo-weather-data_csv](./sample_data/sample3_tokyo-weather-data_csv/)

`csv`file only.

#### [sample4_coco-annotations_csv](./sample_data/sample4_coco-annotations_csv/)

```
docker-compose exec sample_data bash
cd sample4_coco-annotations_csv
./create_csv.sh
```
