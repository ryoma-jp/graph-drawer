'''
COCO Annotations to CSV

This script converts COCO annotations to CSV format.

Arguments:
    -i, --input: Path to COCO annotations file.
    -o, --output: Path to output CSV file.
'''

import argparse
import pandas as pd
from pycocotools.coco import COCO

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='COCO Annotations to CSV')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to COCO annotations file.')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to output CSV file.')
    args = parser.parse_args()

    # Load COCO annotations
    coco = COCO(args.input)

    # Initialize list to store annotations
    annotations = []

    # Loop through images
    for img_id in coco.getImgIds():
        img = coco.loadImgs(img_id)[0]
        ann_ids = coco.getAnnIds(imgIds=img['id'])
        anns = coco.loadAnns(ann_ids)

        # Loop through annotations
        for ann in anns:
            annotation = {
                'image_id': img['id'],
                'file_name': img['file_name'],
                'width': img['width'],
                'height': img['height'],
                'category_id': ann['category_id'],
                'category_name': coco.loadCats(ann['category_id'])[0]['name'],
                'bbox': ann['bbox'],
                'area': ann['area'],
                'segmentation': ann['segmentation'],
                'iscrowd': ann['iscrowd']
            }
            annotations.append(annotation)

    # Convert annotations to DataFrame
    df = pd.DataFrame(annotations)

    # Save DataFrame to CSV
    df.to_csv(args.output, index=False)

    print('CSV file saved to', args.output)

if __name__=='__main__':
    main()
    