# Topsis-Purvi-101953012

It calculates Topsis Score and Topsis Rank fo the given data

## Installation

```pip install Topsis-Yashika-101903787```

## To use via command line

```python topsis data.csv "1,1,1,1,1" "+,+,+,+,+" result.csv```

data.csv is the input data file, then enter the weights of the corresponding columns and then impacts for each column
except for name column and then enter the name of the file in which you want to save the output file

## to use in .py file

```from topsis_purvi05 import top_score```

```top_score(data.csv, "1,1,1,1,1", "+,+,+,+,+" result.csv)```

## Debugging

 Correct number of parameters (inputFileName, Weights, Impacts, resultFileName). 
 
 Show the appropriate message for wrong inputs.

 Handling of “File not Found” exception

 Input file must contain three or more columns.

 From 2nd to last columns must contain numeric values only (Handling of non-numeric values).

 Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.

 Impacts must be either +ve or -ve.

 Impacts and weights must be separated by ‘,’ (comma).
