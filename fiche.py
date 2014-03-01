#!/usr/bin/python3.3
# -*- coding: utf-8 -*-

import os
import hashlib
import sys
import argparse
import xlsxwriter
import csv

# Constants
VERSION = 'v1.3'

# Global 
global_args = None # Program's command line arguments

def md5sum(file_path, block_size=1024):
    md5 = hashlib.md5()
    try:
        f = open(file_path, "rb")
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    except IOError:
        print('IOerror: '+ file_path)
    return md5.hexdigest()

def save(list_of_hashlists):
    # Save as csv
    save_as_csv(list_of_hashlists)

    # Save as xlsx
    if global_args.xlsx is not None:
        save_as_excel(global_args.xlsx, list_of_hashlists)

def save_as_csv(list_of_hashlists):
    for name, hashlist in list_of_hashlists:
        if hashlist is not None:
            try:
                f = open(name+'csv', 'w', newline='')
                print('Writing results in '+name+'.csv')
                writer = csv.writer(f, delimiter=',')
                for line in hashlist:
                    writer.writerow(line)
                f.close()
            except IOError:
                print('IOError: '+filename)

def save_as_excel(filename, list_of_hashlists):
    print('Writing results in '+global_args.xlsx)
    
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

def handle_directory(directory_path):
    files_hashes = list()
    files_duplicates = None

    if global_args.duplicates:
        files_duplicates = list()
    if os.path.isdir(directory_path):
        for root, dirs, files in os.walk(directory_path):
            num_files = len(files)
            num_dirs = len(dirs)
            print("Directory %s has:"%root)
            print("\t- %d files"%num_files)
            print("\t- %d directories"%num_dirs)
            for file in files:
                if root.endswith('/') or root.endswith('\\'):
                    handle_file(files_hashes, files_duplicates, str(root+file))
                else:
                    handle_file(files_hashes, files_duplicates, str(root+'/'+file))
    else:
        print("\"%s\" is not a directory!"%(directory_path))
    return files_hashes, files_duplicates

def handle_file(files_hashes, files_duplicates, filepath):
    md5_hash = md5sum(filepath)
    hashes_list = (el[1] for el in files_hashes)

    if files_duplicates is not None:
        # duplicates argument has been set
        # Check for duplicated files
        if md5_hash in hashes_list:
            for f_path, f_hash in files_hashes:
                if f_hash == md5_hash:
                    files_duplicates.append((filepath,md5_hash,f_path,f_hash))
    
    files_hashes.append((filepath,md5_hash))

def cmp_hashlist(left_hashlist, right_hashlist):
    left_only_items = list()
    right_only_items = list()
    right_hashes = [el[1] for el in right_hashlist]
    
    for file_path, file_hash in left_hashlist:
        if file_hash not in right_hashes:
            left_only_items.append((file_path, file_hash))
    return left_only_items

def main(left_directory, right_directory):
    list_of_hashlist = list()

    # Handle left
    left_hashlist,left_duplicates = handle_directory(left_directory)
    list_of_hashlist.append(( 'left', left_hashlist))
    list_of_hashlist.append(('left_duplicates', left_duplicates))

    # Handle right
    right_hashlist, right_duplicates = handle_directory(right_directory)
    list_of_hashlist.append(('right', right_hashlist))
    list_of_hashlist.append(('right_duplicates', right_duplicates))

    # Compare
    list_of_hashlist.append(('left_only', 
                            cmp_hashlist(left_hashlist, right_hashlist)))
    list_of_hashlist.append(('right_only',
                            cmp_hashlist(right_hashlist, left_hashlist)))
    
    # Write results
    save(list_of_hashlist)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='fiche',
                                     description='Compare two directories')
    parser.add_argument('left_directory',
                        help='Left (source) directory',
                        action='store')
    parser.add_argument('right_directory',
                        help='Right (target) directory',
                        action='store')
    parser.add_argument('--xlsx', nargs='?', help='Generate an Excel file that\
                         contains the results')
    parser.add_argument('--duplicates', nargs='?', help='Find duplicated files\
                         on both sides. Produce two lists: left_duplicates and\
                         and right_duplicates')
    parser.add_argument('--ignore', nargs='*', help='Regular expression that\
                         contains the files that will be ignored during the\
                         analyze')
    global_args = parser.parse_args()
    print('Welcome to fiche '+VERSION)
    print('Thanks for using it!')
    print('Coded by Thomas Bores')
    main(global_args.left_directory, global_args.right_directory)
