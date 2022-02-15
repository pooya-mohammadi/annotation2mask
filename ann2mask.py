"""
Converting json coco file segmentations to masks for Unet and other methods.
"""
# pip install deep_utils
from deep_utils import remove_create
import os
import cv2
import json
from tqdm import tqdm
import numpy as np
from collections import defaultdict


def get_image_id(json_dict, img_name):
    images = json_dict['images']
    for d in images:
        if d['file_name'] == img_name:
            return d['id']


def get_annotation(json_dict, id_):
    annotations = json_dict['annotations']
    annotations_list = list()
    for ann in annotations:
        if ann['image_id'] == id_:
            annotations_list.append(ann)
    return annotations_list


def main(json_path, image_path, mask_path):
    remove_create(mask_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
    # get the annotations
    annotations_point = json_dict['annotations']
    # make a dictionary from annotations with image_ids as keys for each of use.
    # img_annotation_dict = {ann['image_id']: ann for ann in annotations_point}
    img_annotation_dict = defaultdict(list)
    for ann in annotations_point:
        img_annotation_dict[ann['image_id']].append(ann)
    img_annotation_dict = {1: [{segmentations: ....} , {segmentations: ....}, ... ]}
    # get the images' information
    image_file = json_dict['images'] # [{img_name: ... , width, id:... } , {}, ... ]
    # make a dictionary of images' information for ease of use.
    img_dict = {img_file['id']: img_file for img_file in image_file}
    for img_id, img_info in tqdm(img_dict.items(), total=len(img_dict)):
        mask = np.zeros((img_info['height'], img_info['width']), dtype=np.uint8)
        annotations = img_annotation_dict[img_id]
	for ann in annotations:
	    segmentations = ann['segmentation']
	    cat_id = ann['category_id']
	    for seg in segmentations:
		# getting the points
		xs = seg[0::2]
		ys = seg[1::2]
		pts = np.array([[x, y] for x, y in zip(xs, ys)], dtype=np.int32)
		pts = pts.reshape((-1, 1, 2))

		# draw the points on the mask image.
		try:
		    mask = cv2.fillPoly(mask, [pts], cat_id)
		except Exception as e:
		    print(f"[ERROR] error for {img_info['file_name']}, len={len(pts)}")
        cv2.imwrite(os.path.join(mask_path, img_info['file_name']), mask)
        print(f'[INFO] img_id: {img_id} is done!')


if __name__ == '__main__':
    main('cloth_fc.json', "cloth_fc", "cloth_fc_masks")

