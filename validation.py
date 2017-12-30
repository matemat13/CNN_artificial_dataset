#!/usr/bin/env python

import matplotlib
import sys
import os

ds_folder = None

def load_labels(img_name):
    labels = []
    try:
        # Open the label file
        with open("{:s}/{:s}.txt".format(ds_folder, img_name), 'r') as infname:
            for line in infname.readlines():
                spl = line.split(' ')
                label = (
                    float(spl[0]),   # object ID
                    (float(spl[1]),  # x coordinate of the bb center
                     float(spl[2])), # y coordinate of the bb center
                    (float(spl[3]),  # width of the bb
                     float(spl[4]))  # height of the bb
                )
                labels.append(label)
    except:
        print("WARNING: Image without a label: '{:s}'!".format(filename))
    return labels


def validate_image(img_name, vl_labels):
    gt_labels = load_labels(img_name)
    
    for label in vl_labels:
        pass  # TODO: finish this function


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
            cur_labels = []
            for line in infname.readlines():
                spl = line.split(' ')
                img_name = spl[0]
                # the labels are sorted by image name - thus when that changes,
                # it is time to evaluate the labels
                if img_name != prev_img_name
                    if imname is not None
                        cur_error = validate_image(img_name, cur_labels)
                        avg_error = (avg_error*n_images_validated + cur_error)/(n_images_validated+1)
                        n_images_validated += 1
                    prev_img_name = img_name
                    cur_labels = []
                
                certainty = spl[1]
                
                if certainty > threshold
                    label = (
                        float(spl[2]),   # object ID
                        (float(spl[3]),  # x coordinate of the bb center
                         float(spl[4])), # y coordinate of the bb center
                        (float(spl[5]),  # width of the bb
                         float(spl[6]))  # height of the bb
                    )
                    labels.append(label)
                    
      print("The average IoU error for all validation images is {:.3f}".format(avg_error))


if __name__ == "__main__":
    main()
