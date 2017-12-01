#!/usr/bin/env python

import cv2
import os
import numpy as np

def main():
    # TODO: Load these parameters from a file or command line
    ds_folder = "output/training"
    ds_fnames = os.listdir(ds_folder)
    ds_fnames.sort()

    print("Loading dataset")
    labels = dict()
    for filename in ds_fnames:
        img_name = '.'.join(filename.split('.')[0:-1])
        extension = filename.split('.')[-1]

        if extension == "txt":
            with open("{:s}/{:s}".format(ds_folder, filename), 'r') as infname:
                for line in infname.readlines():
                    spl = line.split(' ')
                    label = (
                        float(spl[0]),   # object ID
                        (float(spl[1]),  # x coordinate of the bb center
                         float(spl[2])),  # y coordinate of the bb center
                        (float(spl[3]),  # width of the bb
                         float(spl[4]))   # height of the bb
                    )
                    if img_name not in labels:
                        labels[img_name] = list()
                    labels[img_name].append(label)

    tot_imgs = len(labels)
    print("Showing bounding boxes for {:d} total images".format(tot_imgs))

    window_name = "Dataset bounding box check"
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)
    for filename in ds_fnames:
        img_name = '.'.join(filename.split('.')[0:-1])
        extension = filename.split('.')[-1]

        if extension == "txt":
            continue

        img = cv2.imread("{:s}/{:s}".format(ds_folder, filename), cv2.IMREAD_UNCHANGED)
        if not img_name in labels:
            print("Unknown image without a label: '{:s}'!".format(filename))
        else:
            img_width = img.shape[0]
            img_height = img.shape[1]
            for label in labels[img_name]:
                cent_x = label[1][0]*img_width
                cent_y = label[1][1]*img_height
                width  = label[2][0]*img_width
                height = label[2][1]*img_height
                x1 = int(np.ceil(cent_x - width/2))
                x2 = int(np.floor(cent_x + width/2))
                y1 = int(np.ceil(cent_y - height/2))
                y2 = int(np.floor(cent_y + height/2))
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 5)

        cv2.imshow(window_name, img)
        k = cv2.waitKey(0)  # 0 - wait forever
        if k == ord('w'):
            print("Image {:s} marked as labeled WRONG!".format(filename))

    cv2.destroyWindow(window_name)
    print("Done with everything. Goodbye.")


if __name__ == "__main__":
    main()
