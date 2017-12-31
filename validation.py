#!/usr/bin/env python

import matplotlib
import sys
import os

ds_folder = None

class BBox:
    label = None
    left = None
    right = None
    width = None
    bottom = None
    top = None
    height = None

    def BBox(label, center_x, center_y, width, height):
        self.label = label
        self.width = width
        self.height = height
        self.left = center_x - width/2.0
        self.right = center_x + width/2.0
        self.top = center_y - height/2.0
        self.bottom = center_y + height/2.0


def load_bboxes(img_name):
    bboxes = []
    try:
        # Open the label file
        with open("{:s}/{:s}.txt".format(ds_folder, img_name), 'r') as infname:
            for line in infname.readlines():
                spl = line.split(' ')
                cur_bbox = BBox(spl[0], spl[1], spl[2], spl[3], spl[4])
                bboxes.append(cur_bbox)
    except:
        print("WARNING: Image without a label: '{:s}'!".format(filename))
    return bboxes


def calc_IoU(bbox1, bbox2):
    width = max(bbox1.left, bbox2.left) - min(bbox1.right, bbox2.right)
    height = max(bbox1.top, bbox2.top) - min(bbox1.bottom, bbox2.bottom)
    AoO = width*heigh
    AoU = bbox1.width*bbox1.height + bbox2.width*bbox2.height - AoO
    return AoO/AoU


# TODO: Improve this function... this is suboptimal
def validate_image(img_name, vl_bboxes):
    gt_bboxes = load_bboxes(img_name)
    gt_used = len(gt_bboxes)*[False]
    
    avg_IoU = 0.0
    n_IoU = 0.0
    for vl_bbox in vl_bboxes:
        min_IoU_set = False
        min_IoU_it = None
        min_IoU = None
        for gt_it in range(0, len(gt_bboxes)):
            if not gt_used[gt_it]:
                cur_IoU = calc_IoU(gt_bboxes[gt_it], vl_bbox)
                if not min_IoU_set or cur_IoU < min_IoU:
                    min_IoU = cur_IoU
                    min_IoU_set = True
                    min_IoU_it = gt_it

        if min_IoU_set:  # if a ground truth bounding box is left
            gt_used[min_IoU_it] = True
        else:    # If all ground truth bounding boxes were used and there are still some bounding boxes in the validation set
            min_IoU = 1.0
        avg_IoU = (avg_IoU*n_IoU + min_IoU)/(n_IoU+1.0) 
        n_IoU += 1.0

    # If there are any ground truth bounding boxes left, count them into the error
    for gt_it in range(0, len(gt_bboxes)):
        if not gt_used[gt_it]:
            min_IoU = 1.0
            avg_IoU = (avg_IoU*n_IoU + min_IoU)/(n_IoU+1.0) 
            n_IoU += 1.0

    return avg_IoU


def main():
    global ds_folder
    if len(sys.argv) < 3:
        print("You must specify the dataset and validation folders")
        return

    ds_folder = sys.argv[1]
    ds_fnames = os.listdir(ds_folder)
    ds_fnames.sort()
    vl_folder = sys.argv[2]
    vl_fnames = os.listdir(vl_folder)
    vl_fnames.sort()

    threshold = 0.6
    if len(sys.argv) > 3:
        threshold = int(sys.argv[3])

    tot_imgs = int(len(ds_fnames)/2)
    tot_weights = int(len(vl_fnames))
    print("There are {:d} total validation images".format(tot_imgs))
    print("There are {:d} total validation weights".format(tot_weights))

    avg_error = 0.0
    n_images_validated = 0

    for filename in vl_fnames:
        with open("{:s}/{:s}.txt".format(vl_folder, filaneme), 'r') as infname:
            prev_img_name = None
            cur_bboxes = []
            for line in infname.readlines():
                spl = line.split(' ')
                img_name = spl[0]
                # the labels are sorted by image name - thus when that changes,
                # it is time to evaluate the labels
                if img_name != prev_img_name
                    if imname is not None
                        cur_error = validate_image(img_name, cur_bboxes)
                        avg_error = (avg_error*n_images_validated + cur_error)/(n_images_validated+1)
                        n_images_validated += 1
                    prev_img_name = img_name
                    cur_bboxes = []
                
                certainty = spl[1]
                
                if certainty > threshold
                    cur_bbox = BBox(spl[2], spl[3], spl[4], spl[5], spl[6])
                    # label = (
                    #     float(spl[2]),   # object ID
                    #     (float(spl[3]),  # x coordinate of the bb center
                    #      float(spl[4])), # y coordinate of the bb center
                    #     (float(spl[5]),  # width of the bb
                    #      float(spl[6]))  # height of the bb
                    # )
                    cur_bboxes.append(cur_bbox)
                    
      print("The average IoU error for all validation images is {:.3f}".format(avg_error))


if __name__ == "__main__":
    main()
