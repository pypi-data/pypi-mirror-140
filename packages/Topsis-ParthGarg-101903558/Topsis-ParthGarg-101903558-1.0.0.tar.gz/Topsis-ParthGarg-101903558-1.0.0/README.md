# Topsis 
It runs on terminal and takes a csv file , weights of column, impacts and name of the output file as input and gives an output csv file that contains topsis performance score and the rank of a particular entity.

## Installation
On your terminal run the command below:<br>
```pip install Topsis-ParthGarg-101903558```

## Importing and using in source file
use the package in source file as follows:<br>

```
pg=__import__("topsis")
pg.get_topsis_result()
```

## How to get output?
output is taken by running the command on terminal as : python "sourcefile.py" "input.csv" "weights(separateed by ',')" "impact(separated by ','))" 
use impact as '+' for maximizing the feature and '-' for minimizing.
On your terminal run the command:<br>
```python source_file_name.py input_file.csv "1,1,0,1" "+,-,+,+" output_file_name.csv```