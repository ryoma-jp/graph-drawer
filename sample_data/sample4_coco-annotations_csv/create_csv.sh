#! /bin/bash

DATASET_DIR="/tmp/dataset"
OUTPUT_DIR="./output"

# --- Download and extract the COCO 2017 annotations ---
mkdir -p $DATASET_DIR
if [ -e $DATASET_DIR/annotations_trainval2017.zip ]; then
    echo "COCO 2017 annotations already downloaded."
else
    echo "Downloading COCO 2017 annotations..."
    wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip -P $DATASET_DIR
    unzip $DATASET_DIR/annotations_trainval2017.zip -d $DATASET_DIR
fi

# --- Convert the COCO 2017 annotations to CSV ---
mkdir -p $OUTPUT_DIR
python3 coco_to_csv.py --input $DATASET_DIR/annotations/instances_val2017.json --output $OUTPUT_DIR/val2017.csv
