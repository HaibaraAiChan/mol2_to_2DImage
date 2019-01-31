import argparse
from Voronoi import Bionoi
import os
import skimage
from skimage.io import imshow
import para
from skimage.transform import rotate
import numpy as np
import shutil
import gc
import objgraph


def getArgs():
    parser = argparse.ArgumentParser('python')
    parser.add_argument('-folderPath',
                        default=para.folderPath,    #"./mols/",
                        required=False,
                        help='the path of mol2 file folder')
    parser.add_argument('-folderName',
                        default=para.folderName,   #"steroid/",
                        required=False,
                        help='the name of mol2 file folder')
    parser.add_argument('-out',
                        default=para.out,    #"./output/",
                        required=False,
                        help='the folder of output images file')
    parser.add_argument('-proDirect',
                        type=int,
                        default=para.proDirect,  # 4,
                        choices=[0, 1, 2, 3, 4, 5, 6],
                        required=False,
                        help='the direction of projection(from all, xy+,xy-,yz+,yz-,zx+,zx-)')
    parser.add_argument('-rotAngle2D',
                        type=int,
                        default=para.rotAngle2D,
                        choices=[0, 1, 2, 3, 4],
                        required=False,
                        help='the angle of rotation(from original all, 0, 90, 180, 270)')
    parser.add_argument('-flip',
                        type=int,
                        default=para.flip,
                        choices=[0, 1, 2],
                        required=False,
                        help='the type of flipping(all, original, up-down)')
    parser.add_argument('-dpi',
                        default=256,
                        required=False,
                        help='image quality in dpi')
    parser.add_argument('-size', default=256,
                        required=False,
                        help='image size in pixels, eg: 128')
    parser.add_argument('-alpha',
                        default=1.0,
                        required=False,
                        help='alpha for color of cells')
    parser.add_argument('-colorby',
                        default="residue_type",
                        choices=["atom_type", "residue_type", "residue_num"],
                        required=False,
                        help='color the voronoi cells according to {atom_type, residue_type, residue_num}')
    parser.add_argument('-imageType',
                        default=".jpg",
                        choices=[".jpg", ".png"],
                        required=False,
                        help='the type of image {.jpg, .png}')
    parser.add_argument('-save_fig',
                        default=False,
                        choices=[True, False],
                        required=False,
                        help='whether the original image needs save (True, False)')
    return parser.parse_args()


def gen_output_filename_list(dirct, rotAngle, flip):
    f_p_list = []
    f_r_list = []
    f_f_list = []

    if dirct != 0:
        name = ''
        if dirct == 1:
            name = 'XOY+'
        elif dirct == 2:
            name = 'XOY-'
        elif dirct == 3:
            name = 'YOZ+'
        elif dirct == 4:
            name = 'YOZ-'
        elif dirct == 5:
            name = 'ZOX+'
        elif dirct == 6:
            name = 'ZOX-'
        f_p_list.append(name)
    elif dirct == 0:
        f_p_list = ['XOY+', 'XOY-', 'YOZ+', 'YOZ-', 'ZOX+', 'ZOX-']

    if rotAngle != 0:
        name = ''
        if rotAngle == 1:
            name = '_r0'
        elif rotAngle == 2:
            name = '_r90'
        elif rotAngle == 3:
            name = '_r180'
        elif rotAngle == 4:
            name = '_r270'
        f_r_list.append(name)
    else:
        f_r_list = ['_r0', '_r90', '_r180', '_r270']

    if flip != 0:
        name = ''
        if flip == 1:
            name = '_OO'
        elif flip == 2:
            name = '_ud'

        f_f_list.append(name)
    else:
        f_f_list = ['_OO', '_ud']

    return f_p_list, f_r_list, f_f_list


def one_gen_48(mol, out_folder, args):

    basepath = os.path.basename(mol)
    basename = os.path.splitext(basepath)[0]
    size = args.size
    dpi = args.dpi
    alpha = args.alpha
    imgtype = args.imageType
    colorby = args.colorby
    proDirect = args.proDirect
    rotAngle = args.rotAngle2D
    flip = args.flip

    f_p_list, f_r_list, f_f_list = gen_output_filename_list(proDirect, rotAngle, flip)
    len_list = len(f_p_list)
    proj_img_list = []
    rotate_img_list = []
    flip_img_list = []

    # ===================================== Projection ===============================================
    if proDirect != 0:
        atoms, vor, img = Bionoi(mol=mol,
                                 bs_out='',
                                 size=size,
                                 dpi=dpi,
                                 alpha=alpha,
                                 colorby=colorby,
                                 proDirct=proDirect)
        # imshow(img)
        proj_img_list.append(img)
    else:
        for i in range(len_list):
            atoms, vor, img = Bionoi(mol=mol,
                                     bs_out='',
                                     size=size,
                                     dpi=dpi,
                                     alpha=alpha,
                                     colorby=colorby,
                                     proDirct=i+1)
            proj_img_list.append(img)
    # ---------------------------------- rotate -----------------------------------------

    col = proj_img_list
    m = len(col)

    for i in range(m):
        img = col[i]
        if rotAngle == 0:
            rotate_img_list.append(img)
            rotate_img_list.append(rotate(img, angle=90))
            rotate_img_list.append(rotate(img, angle=180))
            rotate_img_list.append(rotate(img, angle=270))
        elif rotAngle == 1:
            rotate_img_list.append(rotate(img, angle=0))
        elif rotAngle == 2:
            rotate_img_list.append(rotate(img, angle=90))
        elif rotAngle == 3:
            rotate_img_list.append(rotate(img, angle=180))
        elif rotAngle == 4:
            rotate_img_list.append(rotate(img, angle=270))
    # ---------------------------------- flip  -----------------------------------------

    for i in range(len(rotate_img_list)):
        img = rotate_img_list[i]
        if flip == 0:
            flip_img_list.append(img)
            flip_img_list.append(np.flipud(img))
        if flip == 1:
            flip_img_list.append(img)
        if flip == 2:
            img = np.flipud(img)
            flip_img_list.append(img)

    # assert len(proj_img_list) == len(f_p_list)
    # assert len(rotate_img_list) == len(f_r_list)*len(f_p_list)
    # assert len(flip_img_list) == len(f_f_list)*len(f_r_list)*len(f_p_list)
    filename_list = []

    for i in range(len(f_p_list)):
        for j in range(len(f_r_list)):
            for k in range(len(f_f_list)):

                saveFile = f_p_list[i] + f_r_list[j] + f_f_list[k] + imgtype
                filename_list.append(saveFile)

    # assert len(filename_list) == len(flip_img_list)
    for i in range(len(filename_list)):
        # imshow(flip_img_list[i])
        # print(i+1)
        path_base = os.path.join(out_folder, basename + '_')
        skimage.io.imsave(path_base + filename_list[i], flip_img_list[i])

    del filename_list
    del flip_img_list
    del rotate_img_list
    del proj_img_list
    del f_p_list, f_r_list, f_f_list

def gen_48():
    args = getArgs()

    input_folder = args.folderPath+args.folderName
    for root, dirs, files in os.walk(input_folder):
        for name in dirs:
            out_folder = args.out + args.folderName + name
            if os.path.exists(out_folder):
                shutil.rmtree(out_folder, ignore_errors=True)

            os.makedirs(out_folder)
            input_files = os.listdir(input_folder + name)
            num = 0
            for mol in input_files:
                one_gen_48(input_folder + name+'/'+mol, out_folder,args)
                num = num+1
                print(num)
                objgraph.show_growth()
            obj = objgraph.by_type('dict')[1000]
            objgraph.show_backrefs(obj, max_depth=10, filename='test.png')


if __name__ == "__main__":
    gen_48()

