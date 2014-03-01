#!/usr/bin/python3.3
# -*- coding: utf-8 -*-

"""
Fiche is an open source and free program developed by Thomas Bores.
It enables the user to handle some specific directory tasks like:
    * Finding duplicated files
    * Comparing repositories based on hashfile comparison
"""

import os
import hashlib
import argparse
import xlsxwriter
import csv
import fnmatch

# Constants
VERSION = 'v2.0'

def md5sum(file_path, block_size=1024):
    """
    Calculate the md5 sum of a file.
    The file is read a block after another.

    Args:
        file_path -- Path to the file
        block_size -- Buffer size
    Return:
        The md5 hash
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as file:
            while True:
                data = file.read(block_size)
                if not data:
                    break
                md5.update(data)
    except IOError:
        print('IOerror: '+ file_path)
    return md5.hexdigest()

def save(list_of_hashlists):
    """
    Save program results.
    Depending on the input arguments it will save only in csv format.
    Or in csv and xlsx.

    Arg:
        list_of_hashlist -- A list of all calculated hash listes
    """
    # Save as csv
    save_as_csv(list_of_hashlists)

    # Save as xlsx
    if ARGS.xlsx is not None:
        save_as_excel(ARGS.xlsx, list_of_hashlists)

def save_as_csv(list_of_hashlists):
    """
    Save program results in csv files.
    Each hash list is saved in a separated csv file.

    Arg:
        list_of_hashlists -- A list of all calculated hash listes
    """
    for name, hashlist in list_of_hashlists:
        if hashlist is not None:
            try:
                with open(name+'.csv', 'w', newline='') as file:
                    print('Writing results in '+name+'.csv')
                    writer = csv.writer(file, delimiter=',')
                    for line in hashlist:
                        writer.writerow(line)
            except IOError:
                print('IOError: '+name)

def save_as_excel(filename, list_of_hashlists):
    """
    Save program results in a xlsx file.
    Each hash list is saved in a dedicated sheet of the xlsx file.

    Arg:
        list_of_hashlists -- A list of all calculated hash listes
    """
    print('Writing results in '+ARGS.xlsx)

    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    workbook = xlsxwriter.Workbook(filename)

    for name, hashlist in list_of_hashlists:
        if hashlist is not None:
            worksheet = workbook.add_worksheet(name)
            for row, line in enumerate(hashlist):
                for i in range(0, len(line)):
                    worksheet.write(row, i, line[i])
                    worksheet.write(row, i, line[i])

def is_file_ignored(file):
    """
    Check if the given file shall be ignored or not, depending on the
    -i or --ignore parameter value.

    Arg:
        file -- The file to be checked
    """
    if ARGS.ignore is not None:
        for regex in ARGS.ignore:
            if fnmatch.fnmatch(file, regex):
                return True
    return False

def handle_directory(directory_path):
    """
    Go through directory and its subdirectories.

    Arg:
        directory_path -- Path of the directory to be checked
    """
    files_hashes = list()
    files_duplicates = None

    if ARGS.duplicates:
        files_duplicates = list()
    if os.path.isdir(directory_path):
        for root, dirs, files in os.walk(directory_path):
            num_files = len(files)
            num_dirs = len(dirs)
            print("Directory %s has:"%root)
            print("\t- %d files"%num_files)
            print("\t- %d directories"%num_dirs)
            for file in files:
                if is_file_ignored(file) == False:
                    if root.endswith('/') or root.endswith('\\'):
                        handle_file(files_hashes,
                                    files_duplicates,
                                    str(root+file))
                    else:
                        handle_file(files_hashes,
                                    files_duplicates,
                                    str(root+'/'+file))
                else:
                    print('Ignore file '+file)
    else:
        print("\"%s\" is not a directory!"%(directory_path))
        raise IOError
    return files_hashes, files_duplicates

def handle_file(files_hashes, files_duplicates, filepath):
    """
    Start work on a specific file:
        * Start checksum
        * Add it to the hashlist

    Args:
        files_hashes -- List of file hashes in the directory
        files_duplicates -- List of files duplicated in the directory
        filepath -- path of the current file
    """
    md5_hash = md5sum(filepath)
    hashes_list = (el[1] for el in files_hashes)

    if files_duplicates is not None:
        # duplicates argument has been set
        # Check for duplicated files
        if md5_hash in hashes_list:
            for f_path, f_hash in files_hashes:
                if f_hash == md5_hash:
                    files_duplicates.append((filepath,
                                             md5_hash,
                                             f_path,
                                             f_hash))

    files_hashes.append((filepath, md5_hash))

def cmp_hashlist(left_hashlist, right_hashlist):
    """
    Compare two hash lists and return the items that are only in the first one.

    Args:
        left_hashlist -- Source list of hashes
        right_hashlist -- List of hashes to be compared with the source list
    Return:
        List of items that are only in the source list
    """
    left_only_items = list()
    right_hashes = [el[1] for el in right_hashlist]

    for file_path, file_hash in left_hashlist:
        if file_hash not in right_hashes:
            left_only_items.append((file_path, file_hash))
    return left_only_items

def main(left_directory, right_directory):
    """
    Main function
    """
    list_of_hashlist = list()

    try:
        # Handle left
        left_hashlist, left_duplicates = handle_directory(left_directory)
        list_of_hashlist.append(('left', left_hashlist))
        list_of_hashlist.append(('left_duplicates', left_duplicates))

        if ARGS.right_directory is not None:
            # Handle right
            right_hashlist, right_duplicates = handle_directory(right_directory)
            list_of_hashlist.append(('right', right_hashlist))
            list_of_hashlist.append(('right_duplicates', right_duplicates))

            # Compare
            list_of_hashlist.append(('left_only',
                                    cmp_hashlist(left_hashlist,
                                                 right_hashlist)))
            list_of_hashlist.append(('right_only',
                                    cmp_hashlist(right_hashlist,
                                                 left_hashlist)))

        # Display results
        if ARGS.duplicates:
            print('%d duplicated file(s) found in left_directory!'%
                  (len(left_duplicates)))
            if ARGS.right_directory is not None:
                print('%d duplicated file(s) found in right_directory!'%
                      (len(right_duplicates)))

        # Write results
        save(list_of_hashlist)
    except IOError:
        print('Error while execution, please check your path(s)!')

if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(prog='fiche',
                                     description='Compare two directories')
    PARSER.add_argument('left_directory',
                        help='Left (source) directory',
                        )
    PARSER.add_argument('right_directory',
                        nargs='?',
                        help='Right (target) directory',
                        )
    PARSER.add_argument('-x', '--xlsx',
                        nargs='?',
                        help='Generate an Excel file that contains the results')
    PARSER.add_argument('-d', '--duplicates',
                        action='store_true',
                        help='Find duplicated files on both sides.\
                        Produce two lists: left_duplicates and\
                         right_duplicates')
    PARSER.add_argument('-i', '--ignore',
                        nargs='*',
                        help='Regular expression that contains the files \
                        that will be ignored during the \
                        analyze')
    ARGS = PARSER.parse_args()
    print('Welcome to fiche '+VERSION)
    print('Thanks for using it!')
    print('Coded by Thomas Bores')
    main(ARGS.left_directory, ARGS.right_directory)
