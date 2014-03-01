fiche
=====

Directory comparison tools. Fiche uses hashes based comparison.

Usage examples:
---------------
Calculate md5sum of all files in a directory:

```
python3 fiche.py path/to/directory
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
