fiche
=====

Directory comparison tools. Fiche uses hashes based comparison.

Dependancies:
-------------
xlsxwriter => https://xlsxwriter.readthedocs.org/

Installation on Debian:
-----------------------
First install all the needed packages
```
sudo apt-get update
sudo apt-get install python3 python3-pip python3-setuptools
sudo pip3 install xlsxwriter
```

Download fiche and unzip it
```
wget https://github.com/tbores/fiche/archive/master.zip
unzip master.zip
```


Usage examples:
---------------
Calculate md5sum of all files in a directory:

```
python3 fiche.py path/to/directory
```

Exclude .txt and .png files from the analysis:
```
python3 fiche.py --ignore *.txt *.png path/to/directory
```

Find duplicated files in a directorory:

```
python3 fiche.py --duplicates path/to/directory
```

Compare files of two directories:

```
python3 fiche.py left_directory right_directory
```

Compare files of two directories, find duplicated files in each directory and export results in a xlsx

```
python3 fiche.py --xlsx output/results.xlsx --duplicates left_directory right_directory
```
