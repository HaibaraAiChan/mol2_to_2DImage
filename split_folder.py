import numpy as np
import os
import re
import shutil
import sys
import argparse


def getArgs():
    parser = argparse.ArgumentParser('python')
    parser.add_argument('-train',
                        type=float,
                        default=0.8,
                        required=False,
                        help='train data set ratio')
    parser.add_argument('-validate',
                        type=float,
                        default=0.1,
                        required=False,
                        help='validation data set ratio')
    parser.add_argument('-test',
                        type=float,
                        default=0.1,
                        required=False,
                        help='test data set ratio')
    parser.add_argument('-folderPath',
                        default='mols/',
                        required=False,
                        help='image folder path')
    parser.add_argument('-folderName',
                        default='steroid/',
                        required=False,
                        help='image folder name')

    return parser.parse_args()


# save the splitted datasets to folders
def saveToFolder(filenameList, folderDir):
    m = len(filenameList)
    target = folderDir

    source_dir = os.path.dirname(os.path.normpath(target))
    for i in range(m):
        source = source_dir + '/' + filenameList[i]
        try:
            shutil.copy(source, target)
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())


def split_mol2_Folder(folderPath, folderName, val_data_fraction=0.1, test_data_fraction=0.1):
    DIR = folderPath + folderName

    m = 0
    filename_list = []
    for parentdir, dirname, filenames in os.walk(DIR):

        for filename in filenames:

            if re.match(r'[0-9a-zA-Z]*\-1\.mol2', filename):
                m = m + 1
                filename_list.append(filename)

    assert len(filename_list) == m


    # shuffle the collection to create a new one
    idx = np.arange(m)
    idx_permu = np.random.permutation(idx)
    col_shuffle = [filename_list[i] for i in idx_permu]

    # calculate the length of each new folder
    len_val = int(m * val_data_fraction)
    len_test = int(m * test_data_fraction)
    len_train = m - (len_val + len_test)

    # create 3 new lists of images
    train_set = col_shuffle[0:len_train]
    val_set = col_shuffle[len_train:len_train + len_val]
    test_set = col_shuffle[len_train + len_val:m]

    # directory of 3 new folders
    trainDir = folderPath + folderName + '_train/'
    if not os.path.exists(trainDir):
        os.makedirs(trainDir)

    valDir = folderPath + folderName + '_val/'
    if not os.path.exists(valDir):
        os.makedirs(valDir)

    testDir = folderPath + folderName + '_test/'
    if not os.path.exists(testDir):
        os.makedirs(testDir)

    # save images
    saveToFolder(train_set, trainDir)
    saveToFolder(val_set, valDir)
    saveToFolder(test_set, testDir)


if __name__ == "__main__":
    args = getArgs()
    # folderPath = 'mols/'
    # # folderName = 'control/'
    # # folderName = 'heme/'
    # # folderName = 'nucleotide/'
    # folderName = 'steroid/'
    # split_mol2_Folder(folderPath, folderName, val_data_fraction=0.1, test_data_fraction=0.1)
    split_mol2_Folder(args.folderPath,
                      args.folderName,
                      val_data_fraction=args.validate,
                      test_data_fraction=args.test)