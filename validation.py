#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

import re
from PIL import Image
import cv2

ds_folder = None

class BBox:
    label = None
    left = None
    right = None
    width = None
    bottom = None
    top = None
    height = None

    def __init__(self, label, x1, y1, x2, y2, img_width=None, img_height=None):
        if img_width is None and img_height is None:
        # This constructor is to be used with validation created labels
            self.label = label
            self.left = min(x1, x2)
            self.top = min(y1, y2)
            self.right = max(x1, x2)
            self.bottom = max(y1, y2)
            self.width = self.right-self.left
            self.height = self.bottom-self.top
        else:
        # This constructor is to be used with ground truth labels
            self.label = label
            self.width = x2*img_width
            self.height = y2*img_height
            self.left = x1*img_width - self.width/2.0
            self.right = x1*img_width + self.width/2.0
            self.top = y1*img_height - self.height/2.0
            self.bottom = y1*img_height + self.height/2.0
        #if self.width < 0 or self.height < 0 or self.left < 0 or self.right < 0 or self.top < 0 or self.bottom < 0:
        #    print("Wrong input parameters to BBox: [{:.0f},{:.0f}], [{:.0f},{:.0f}], {:.0f}, {:.0f}".format((self.left), (self.top), (self.right), (self.bottom), (self.width), (self.height)))


# These two functions are taken from https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]


def load_bboxes(img_name):
    bboxes = []
    width = None
    height = None
    try:
        with Image.open("{:s}/{:s}.jpg".format(ds_folder, img_name), 'r') as img:
            img_width, img_height = img.size
    except IOError:
        print("Cannot open file '{:s}/{:s}.jpg'".format(ds_folder, img_name))
        print("WARNING: Could not find image: '{:s}'!".format(img_name))
        return None
    try:
        # Open the label file '.'.join(img_name.split('.')[0:-1])
        with open("{:s}/{:s}.txt".format(ds_folder, img_name), 'r') as infname:
            for line in infname.readlines():
                spl = line.split(' ')
                cur_bbox = BBox(float(spl[0]), float(spl[1]), float(spl[2]), float(spl[3]), float(spl[4]), img_width, img_height)
                bboxes.append(cur_bbox)
        return bboxes
    except IOError:
        print("Cannot open file '{:s}/{:s}.txt'".format(ds_folder, img_name))
        print("WARNING: Image without a label: '{:s}'!".format(img_name))
        return None


def calc_IoU(bbox1, bbox2):
    width = min(bbox1.right, bbox2.right) - max(bbox1.left, bbox2.left)
    height =  min(bbox1.bottom, bbox2.bottom) - max(bbox1.top, bbox2.top)
    # This checks for the no-intersection case, which could otherwise cause trouble
    if width < 0.0 or height < 0.0:
        return 0.0
    AoO = width*height
    AoU = bbox1.width*bbox1.height + bbox2.width*bbox2.height - AoO
    return AoO/AoU


# TODO: Improve this function... this is suboptimal
def validate_image(img_name, vl_bboxes, IoU_threshold=0.5, show=False):
    gt_bboxes = load_bboxes(img_name)
    if gt_bboxes is None:  # this happens when the label file is not found
        return (None, None)

    gt_used = len(gt_bboxes)*[False]
    n_FPs = 0
    n_FNs = 0
    n_bboxes = len(gt_bboxes)

    if show:
        window_name = "blabla"
        img = cv2.imread("{:s}/{:s}.png".format(ds_folder, img_name), cv2.IMREAD_UNCHANGED)
        for bbox in vl_bboxes:
            x1 = int(np.ceil(bbox.left))
            x2 = int(np.floor(bbox.right))
            y1 = int(np.ceil(bbox.top))
            y2 = int(np.floor(bbox.bottom))
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 5)

        cv2.imshow(window_name, img)
        k = cv2.waitKey(0)  # 0 - wait forever
	
    score_total = 0.0
    for vl_bbox in vl_bboxes:
        max_IoU_set = False
        max_IoU_it = None
        max_IoU = None
        for gt_it in range(0, len(gt_bboxes)):
            if not gt_used[gt_it]:
                cur_IoU = calc_IoU(gt_bboxes[gt_it], vl_bbox)
                if cur_IoU > IoU_threshold and (not max_IoU_set or cur_IoU > max_IoU):
                    max_IoU = cur_IoU
                    max_IoU_set = True
                    max_IoU_it = gt_it

        if max_IoU_set:  # if a ground truth bounding box is left
            gt_used[max_IoU_it] = True
            # avg_IoU = (avg_IoU*n_IoU + max_IoU)/float(n_IoU+1) 
            # n_IoU += 1
            score_total += max_IoU
        else:    # If all ground truth bounding boxes were used and there are still some bounding boxes in the validation set
            # This means that we have a false positive
            n_FPs += 1
            # avg_IoU = (avg_IoU*n_IoU + 0.0)/float(n_IoU+1) 
            # n_IoU += 1

    # If there are any ground truth bounding boxes left and false negative counting is on, count them into the error
    for gt_it in range(0, len(gt_bboxes)):
        if not gt_used[gt_it]:
            n_FNs += 1
            # avg_IoU = (avg_IoU*n_IoU + 0.0)/float(n_IoU+1) 
            # n_IoU += 1

    return (score_total, n_bboxes, n_FPs, n_FNs)


def main():
    global ds_folder
    if len(sys.argv) < 3:
        print("Usage: ./validate.py <dataset folder> <validation folder>")
        # print("You must specify the dataset and validation folders")
        return

    ds_folder = sys.argv[1]
    ds_fnames = os.listdir(ds_folder)
    # ds_fnames.sort()
    vl_folder = sys.argv[2]
    vl_fnames = os.listdir(vl_folder)
    vl_fnames.sort(key=natural_keys)

    threshold = 0.6
    if len(sys.argv) > 3:
        threshold = float(sys.argv[3])

    tot_imgs = int(len(ds_fnames)/2)
    tot_weights = int(len(vl_fnames))
    print("There are {:d} total validation images".format(tot_imgs))
    print("There are {:d} total validation weights".format(tot_weights))

    results_IoU = np.zeros((4, tot_weights))
    vl_it = 0

    for filename in vl_fnames:
        score_total = 0.0   # total sum of all IoUs (should be then normalised over n_bboxes_total)
        n_bboxes_total = 0  # total number of Ground Truth bounding boxes in this validation set
        n_FPs = 0           # total number of false positives (detected objects wit IoU < threshold)
        n_FNs = 0           # total number of false negatives (undetected GT objects)
        with open("{:s}/{:s}".format(vl_folder, filename), 'r') as infname:
            print("Validating weights file '{:s}'".format(filename))
            tmp = re.split('(\d+)', filename)
            training_iterations = atoi(tmp[-2])
            prev_img_name = None
            cur_bboxes = []
            # There is one line per label (bounding box with object ID)
            # the format of a label is <image name> <center_x> <center_y> <width> <height>
            for line in infname.readlines():
                spl = line.split(' ')
                # print(spl)
                img_name = spl[0]
                # the labels are sorted by image name - thus when that changes,
                # it is time to evaluate the labels
                if img_name != prev_img_name:
                    if prev_img_name is not None:
                        [cur_score, cur_n_bboxes, cur_FPs, cur_FNs] = validate_image(prev_img_name, cur_bboxes)
                        n_FPs += cur_FPs
                        n_FNs += cur_FNs
                        # cur_error is none when the ground truth label file was not found
                        # cur_n_bboxes is zero is there are no detections in the image
                        if cur_score is not None:
                            score_total += cur_score
                            n_bboxes_total += cur_n_bboxes
                            # avg_score = (avg_score*n_bboxes_validated + cur_error*cur_n_bboxes)/(n_bboxes_validated+cur_n_bboxes)
                            # n_bboxes_validated += cur_n_bboxes
                    prev_img_name = img_name
                    cur_bboxes = []
                
                certainty = float(spl[1])
                
                if certainty > threshold:
                    # TODO: the darknet validation does not put object ID of the label into the results file... this should be fixed
                    cur_bbox = BBox(0, float(spl[2]), float(spl[3]), float(spl[4]), float(spl[5]))
                    # label = (
                    #     float(spl[2]),   # object ID
                    #     (float(spl[3]),  # x coordinate of the bb center
                    #      float(spl[4])), # y coordinate of the bb center
                    #     (float(spl[5]),  # width of the bb
                    #      float(spl[6]))  # height of the bb
                    # )
                    cur_bboxes.append(cur_bbox)
                    
        avg_score = score_total/float(n_bboxes_total)
        avg_FPs = n_FPs/float(n_bboxes_total)
        avg_FNs = n_FNs/float(n_bboxes_total)
        results_IoU[:, vl_it] = np.array([training_iterations, avg_score, avg_FPs, avg_FNs]).T
        print("Results:\n\taverage IoU:\t{:.3f}\n\taverage FPs:\t{:.3f}\t({:d}/{:d})\n\taverage FNs:\t{:.3f}\t({:d}/{:d})".format(avg_score, avg_FPs, n_FPs, n_bboxes_total, avg_FNs, n_FNs, n_bboxes_total))
        vl_it += 1

    plt.plot(results_IoU[0, :], results_IoU[1, :]*100.0, label="Average IoU score")
    plt.plot(results_IoU[0, :], results_IoU[2, :]*100.0, label= "Number of false positives")
    plt.plot(results_IoU[0, :], results_IoU[3, :]*100.0, label="Number of false negatives")
    plt.xlabel("Number of training iterations [iterations]")
    plt.ylabel("Value [%]")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
