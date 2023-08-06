# Topsis Result Calculator
It runs on terminal and takes a csv file , weights of column, impacts and name of the output file as input and gives an output csv file that contains topsis performance score and the rank of a particular entity.

## Installation
On your terminal run the command below:<br>
```pip install Topsis-RaghavNarula-101903795```

## Importing and using in source file
use the package in source file as follows:<br>

```
tbj=__import__("topsis")
tbj.get_topsis_result()
```

## How to get output?
output is taken by running the command on terminal as : python "sourcefile.py" "input.csv" "weights(separateed by ',')" "impact(separated by ','))" 
use impact as '+' for maximizing the feature and '-' for minimizing.
On your terminal run the command:<br>
```python source_file_name.py input_file.csv "1,1,0,1" "+,-,+,+" output_file_name.csv```
<br>
It will display the input arguments and the input data on terminal screen  and Output will be stored in your present working directory as a csv file.

## Constraints
### Number of columns in input file(other than the name of the entity) should be equal to length of impacts and length of weights.
### Input file should not have blank values
### Number of Columns in Input files should not be less than 3
### There should not be any csv file with same name as your output file in present directory
### Number of Arguments should be equal to the number as specified above  

