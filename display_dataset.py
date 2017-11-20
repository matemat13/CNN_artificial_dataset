#!/usr/bin/env python

import cv2
import os
import numpy as np

def main():
    # TODO: Load these parameters from a file or command line
    in_folder = "dataset"
    labels_fname = "labels.csv"

    print("Loading dataset labels")
    labels = dict()
    header = None
    lb_it = 0
    with open("{:s}/{:s}".format(in_folder, labels_fname), 'r') as infname:
        for line in infname.readlines():
            spl = line.split(';')
            if header is None:
                header = (
                    str(spl[0]),  # line/image ID
                    str(spl[1]),  # image filename
                    str(spl[2]),  # x coordinate of the bb
                    str(spl[3]),  # y coordinate of the bb
                    str(spl[4]),  # width of the bb
                    str(spl[5])   # height of the bb
                )
            else:
                img_fname = spl[1].strip()
                label = (
                    int(spl[0]),  # line/image ID
                    img_fname,    # image filename
                    (int(spl[2]),  # x coordinate of the bb
                    int(spl[3])),  # y coordinate of the bb
                    (int(spl[4]),  # width of the bb
                    int(spl[5]))   # height of the bb
                )
                labels[img_fname] = label


    tot_imgs = len(labels)
    print("Showing bounding boxes for {:d} total images".format(tot_imgs))

    datas_ims = []
    window_name = "Dataset bounding box check"
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)
    fname_list = os.listdir(in_folder)
    fname_list.sort()
    for filename in fname_list:
        if filename == labels_fname:
            continue

        img = cv2.imread("{:s}/{:s}".format(in_folder, filename), cv2.IMREAD_UNCHANGED)
        if not filename in labels:
            print("Unknown image without a label: '{:s}'!".format(filename))
        else:
            label = labels[filename]
            cent_x = label[2][0]
            cent_y = label[2][1]
            width  = label[3][0]
            height = label[3][1]
            x1 = int(np.ceil(cent_x - width/2))
            x2 = int(np.floor(cent_x + width/2))
            y1 = int(np.ceil(cent_y - height/2))
            y2 = int(np.floor(cent_y + height/2))
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 5)

        cv2.imshow(window_name, img)
        k = cv2.waitKey(0)  # 0 - wait forever
        if k == ord('w'):
            print("Image {:s} marked as labeled WRONG!".format(filename))

    cv2.destroyWindow(filename)
    print("Done with everything. Goodbye.")



if __name__ == "__main__":
    main()
