#!/usr/bin/python3.4

import os
import hashlib
import sys

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

def save_hashlist(filename, hashlist):
    try:
        f = open(filename, 'w')
        for line in hashlist:
            for el in line:
                f.write(el+',')
            f.write('\r\n')
        f.close()
    except IOError:
        print('IOError: '+filename)

def handle_directory(directory_path):
    files_hashes = list()
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
    # Handle left
    left_hashlist,left_duplicates = handle_directory(left_directory)
    save_hashlist("left.csv", left_hashlist)
    save_hashlist("left_duplicates.csv", left_duplicates)

    # Handle right
    right_hashlist, right_duplicates = handle_directory(right_directory)
    save_hashlist("right.csv", right_hashlist)
    save_hashlist("right_duplicates.csv", right_duplicates)

    # Compare
    save_hashlist("left_only.csv", cmp_hashlist(left_hashlist, right_hashlist))
    save_hashlist("right_only.csv", cmp_hashlist(right_hashlist, left_hashlist))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s <left_directory_path> <right_directory_path>"%sys.argv[0])
    else:
        main(sys.argv[1], sys.argv[2])

