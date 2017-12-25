#!/usr/bin/env python3

try:
    from PIL import Image
    from PIL import ImageEnhance
except ImportError:
    import Image
import random as rnd
import numpy as np
import os
import cv2

# TODO: Load these parameters from a file or command line
# Settings for the image generation
max_bg_im_width = 600
max_bg_im_height = 600
minimal_bb_width = 40
minimal_bb_height = 30
max_rotation = 35  # in degrees
max_objects_in_image = 4
label = 0
min_contrast_change = 0.25
max_brightness_change = 0.25

show_images = False


def generate_images(backgr_ims, object_ims, n_imgs, out_folder):
    im_it = 0
    
    if show_images:
        window_name = "Bounding box check window"
        cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
    
    # Generate n_rn_imgs of random images
    for rn_it in range(0, n_imgs):
        backgr_im = backgr_ims[rnd.randint(0, len(backgr_ims)-1)]
        bg_size = backgr_im.size
        bg_width = bg_size[0]
        bg_height = bg_size[1]
        maximal_bb_width  = int(np.round(bg_width*0.25))
        maximal_bb_height = int(np.round(bg_height*0.25))

        n_objects_in_image = rnd.randint(1, max_objects_in_image)
        object_bbs_in_image = n_objects_in_image*[None]

        generated_image = Image.new("RGBA", backgr_im.size)
        generated_image.paste(backgr_im, (0,0), backgr_im)

        for obj_it in range(0, n_objects_in_image):
            object_im = object_ims[rnd.randint(0, len(object_ims)-1)]
            ob_size = object_im.size

            xpos_min = 0
            ypos_min = 0

            width_min = minimal_bb_width
            height_min = minimal_bb_height
            width_max = min(bg_width, ob_size[0], maximal_bb_width)
            height_max = min(bg_height, ob_size[1], maximal_bb_height)

            rotation = rnd.gauss(0, max_rotation/3)
            if rotation > max_rotation:
                rotation = max_rotation
            elif rotation < -max_rotation:
                rotation = -max_rotation

            # Rotate the object image randomly
            cur_object_im = object_im.rotate(rotation)
            cur_width  = cur_object_im.size[0]
            cur_height = cur_object_im.size[1]

            # Resize the object image randomly
            min_resize_ratio = max(width_min/cur_width, height_min/cur_height)
            max_resize_ratio = min(width_max/cur_width, height_max/cur_height)
            resize_ratio = rnd.uniform(min_resize_ratio, max_resize_ratio)

            cur_width  = int(np.round(cur_width*resize_ratio))
            cur_height = int(np.round(cur_height*resize_ratio))
            cur_object_im = cur_object_im.resize((cur_width, cur_height))

            xpos_max = bg_width - cur_width
            ypos_max = bg_height - cur_height

            xpos = rnd.randint(xpos_min, xpos_max)
            ypos = rnd.randint(ypos_min, ypos_max)

            # Change the contrast and brightness randomly
            cur_contrast = min(max(1.0-min_contrast_change, rnd.gauss(1.0, min_contrast_change/3.0)), 1.0+min_contrast_change)
            cur_brightness = min(max(1.0-max_brightness_change, rnd.gauss(1.0, max_brightness_change/3.0)), 1.0+max_brightness_change)

            cur_object_im = ImageEnhance.Brightness(ImageEnhance.Contrast(cur_object_im).enhance(cur_contrast)).enhance(cur_brightness)

            tmp = Image.new("RGBA", backgr_im.size)
            tmp.paste(cur_object_im, (xpos,ypos), cur_object_im)

            generated_image = Image.alpha_composite(generated_image, tmp)

            # lefttop_pt = (xpos/bg_width, ypos/bg_height)
            # rightbot_pt = ((xpos+cur_width)/bg_width, (ypos+cur_height)/bg_height)
            cur_center = ((xpos+cur_width/2.0)/bg_width, (ypos+cur_height/2.0)/bg_height)
            cur_bb = (cur_width/bg_width, cur_height/bg_height)

            object_bb = (label, cur_center, cur_bb)
            # object_bb = (label, lefttop_pt, rightbot_pt)
            object_bbs_in_image[obj_it] = object_bb

        im_fname = "dsimage_{:d}.png".format(im_it)
        # Convert the generated image to not include alpha channel (it was used only for blending the images)
        final_image = Image.new("RGB", generated_image.size, (255, 255, 255))
        final_image.paste(generated_image, mask=generated_image.split()[3])  # 3 is the alpha channel
        # Save the generated image
        final_image.save("{:s}/{:s}".format(out_folder, im_fname))

        with open("{:s}/{:s}".format(out_folder, "dsimage_{:d}.txt".format(im_it)), 'w') as ofname:
            for object_bb in object_bbs_in_image:
                ofname.write("{:d} {:f} {:f} {:f} {:f}\n".format(object_bb[0],
                                                                     object_bb[1][0], object_bb[1][1],
                                                                     object_bb[2][0], object_bb[2][1]))
        if show_images:
            cv_image = np.array(final_image)[:, :, ::-1].copy() 
            img_width = cv_image.shape[1]
            img_height = cv_image.shape[0]
            for bb in object_bbs_in_image:
                cent_x = bb[1][0]*img_width
                cent_y = bb[1][1]*img_height
                width  = bb[2][0]*img_width
                height = bb[2][1]*img_height
                x1 = int(np.ceil(cent_x - width/2))
                x2 = int(np.floor(cent_x + width/2))
                y1 = int(np.ceil(cent_y - height/2))
                y2 = int(np.floor(cent_y + height/2))
                cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0,0,255), 5)

            cv2.imshow(window_name, cv_image)
            k = cv2.waitKey(0)  # 0 - wait forever

        im_it = im_it + 1
        print("Finished {:d}/{:d} images".format(im_it, n_imgs))


def main():
    # TODO: Load these parameters from a file or command line
    backgr_im_folder = "input/backgrounds"
    backgr_im_fnames = os.listdir(backgr_im_folder)
    backgr_im_fnames.sort()
    object_im_folder = "input/objects"
    object_im_fnames = os.listdir(object_im_folder)
    object_im_fnames.sort()

    n_train_imgs = 10000
    n_test_imgs = 1000
    tr_out_folder = "output/training"
    ts_out_folder = "output/testing"

    print("Loading background images:")
    backgr_ims = []
    for im_fname in backgr_im_fnames:
        im = Image.open("{:s}/{:s}".format(backgr_im_folder, im_fname))
        if im.size[0] > max_bg_im_width or im.size[1] > max_bg_im_height:
            ratio = max(max_bg_im_width/im.size[0], max_bg_im_height/im.size[1])
            im = im.resize((int(np.floor(im.size[0]*ratio)), int(np.floor(im.size[1]*ratio))))
            # crop the image to have the correct aspect ratio
            tmp = Image.new("RGBA", (max_bg_im_width, max_bg_im_height))
            tmp.paste(im, (0,0), im)
            im = tmp
        backgr_ims.append(im)
        print(im_fname, "-", backgr_ims[len(backgr_ims)-1].mode)

    print("Loading object images:")
    object_ims = []
    for im_fname in object_im_fnames:
        object_ims.append(Image.open("{:s}/{:s}".format(object_im_folder, im_fname)))
        print(im_fname, "-", object_ims[len(object_ims)-1].mode)

    print("------ Starting generation of {:d} total training images ------".format(n_train_imgs))
    generate_images(backgr_ims, object_ims, n_train_imgs, tr_out_folder)
    print("------ Finished generating training images ------")

    print("------ Starting generation of {:d} total testing images ------".format(n_test_imgs))
    generate_images(backgr_ims, object_ims, n_test_imgs, ts_out_folder)
    print("------ Finished generating testing images ------")

    print("Ended dataset generation")
    print("Done with everything. Goodbye.")


if __name__ == "__main__":
    main()
