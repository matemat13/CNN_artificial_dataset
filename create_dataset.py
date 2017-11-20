#!/usr/bin/env python3

try:
    from PIL import Image
except ImportError:
    import Image
import random as rnd
import numpy as np

def main():
    # TODO: Load these parameters from a file or command line
    drone_im_fnames = {"drone_images/drona1.png",
                       "drone_images/drona_na_nebi1.png",
                       "drone_images/drona_cerna.png"}
    backg_im_fnames = {"backg_images/backg_bily.png",
                       "backg_images/backg_les1.png",
                       "backg_images/backg_les2.png",
                       "backg_images/backg_poust1.png",
                       "backg_images/backg_poust2.png",
                       }
    n_rn_imgs = 3
    minimal_bb_width  = 100
    minimal_bb_height = 80
    max_rotation = 45 # in degrees
    out_folder = "dataset"
    labels_fname = "labels.csv"

    print("Loading background images:")
    backg_ims = []
    for im_fname in backg_im_fnames:
        backg_ims.append(Image.open(im_fname))
        print(im_fname, "-", backg_ims[len(backg_ims)-1].mode)

    print("Loading drone images:")
    drone_ims = []
    for im_fname in drone_im_fnames:
        drone_ims.append(Image.open(im_fname))
        print(im_fname, "-", drone_ims[len(drone_ims)-1].mode)

    tot_imgs = n_rn_imgs*len(drone_ims)*len(backg_ims)
    print("Starting dataset generation of {:d} total images".format(tot_imgs))
    # final_ims = n_rn_imgs*len(drone_ims)*len(backg_ims)*[None]
    labels = tot_imgs*[None]

    im_it = 0
    for backg_im in backg_ims:
        bg_size = backg_im.size
        maximal_bb_width  = int(np.round(bg_size[0]*0.25))
        maximal_bb_height = int(np.round(bg_size[1]*0.25))
        for drone_im in drone_ims:
            dr_size = drone_im.size

            xpos_min = 0
            ypos_min = 0

            width_min = minimal_bb_width
            height_min = minimal_bb_height
            width_max = min(bg_size[0], dr_size[0], maximal_bb_width)
            height_max = min(bg_size[1], dr_size[1], maximal_bb_height)
            for rn_it in range(0, n_rn_imgs):
                rotation = rnd.gauss(0, max_rotation/3)
                if rotation > max_rotation:
                    rotation = max_rotation
                elif rotation < -max_rotation:
                    rotation = -max_rotation
                
                # Rotate the drone image randomly
                cur_drone_im = drone_im.rotate(rotation)
                cur_width  = cur_drone_im.size[0]
                cur_height = cur_drone_im.size[1]

                min_resize_ratio = max(width_min/cur_width, height_min/cur_height)
                max_resize_ratio = min(width_max/cur_width, height_max/cur_height)
                resize_ratio = rnd.uniform(min_resize_ratio, max_resize_ratio)

                # Resize the drone image randomly
                cur_width  = int(np.round(cur_width*resize_ratio))
                cur_height = int(np.round(cur_height*resize_ratio))
                cur_drone_im = cur_drone_im.resize((cur_width, cur_height))

                xpos_max = bg_size[0] - cur_width
                ypos_max = bg_size[1] - cur_height

                xpos = rnd.randint(xpos_min, xpos_max)
                ypos = rnd.randint(ypos_min, ypos_max)

                tmp = Image.new("RGBA", backg_im.size)
                tmp.paste(cur_drone_im, (xpos,ypos), cur_drone_im)
                final = Image.alpha_composite(backg_im, tmp)

                cur_center = (xpos+int(np.floor(cur_width/2)), ypos+int(np.floor(cur_height/2)))
                cur_bb = (cur_width, cur_height)

                # Save the generated image
                im_fname = "dsimage_{:d}.png".format(im_it)
                final.save("{:s}/{:s}".format(out_folder, im_fname))
                label = (im_it, im_fname, cur_center, cur_bb)
                labels[im_it] = label

                im_it = im_it + 1
                print("Finished {:d}/{:d} images".format(im_it, tot_imgs))

    print("Ended dataset generation")
    print("Saving labels")
    with open("{:s}/{:s}".format(out_folder, labels_fname), 'w') as ofname:
        ofname.write("ID; image filename; center x; center y; bb width; bb height\n")
        for label in labels:
            ofname.write("{:d}; {:s}; {:d}; {:d}; {:d}; {:d}\n".format(label[0],
                                                                       label[1],
                                                                       label[2][0], label[2][1],
                                                                       label[3][0], label[3][1]))
    print("Done with everything. Goodbye.")



if __name__ == "__main__":
    main()
