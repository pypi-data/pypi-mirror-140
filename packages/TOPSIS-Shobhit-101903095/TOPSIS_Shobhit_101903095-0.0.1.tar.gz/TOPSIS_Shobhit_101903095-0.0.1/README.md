# TOPSIS_Shobhit_101903095

With this you can calculate the TOPSIS score and RANK of the data provided in '.csv' format.

- Input file:
  - contain three or more columns
  - First column is the object/variable name.
  - From 2nd to last column contain numeric values only

# Overview

- it calculates the posis score and a rank based on that score

## Usage

i have explained how to make use topsis yourself below

### Getting it

To download TOPSIS use  pip .

    $ pip install TOPSIS_Shobhit_101903095

### Using it

TOPSIS was programmed with ease-of-use in mind. Just, import topsis from TOPSIS_Shobhit_101903095.topsis1 import topsis
    topsis('inputfilename','Weights','Impacts','Outputfilename')

And you are ready to go!

## Topsis

There are 5 steps in this:

- normalized_matrix
- weight_normalized
- ideal_best_worst
- euclidean_distance
- topsis_score

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Pre-requisite

The data should be in csv format and have more than 3 columns in it.

## Result

the output(outputfilename)  is saved in the project folder with extra 2 columns with topsis score and rank.
