# topsis-python
Topsis analysis of a csv file

""Project-1 Submission""

Name - Gursangat Singh

Roll no. - 101917025

## About Topsis

The Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS) is a multi-criteria decision analysis method, which was originally developed by Ching-Lai Hwang and Yoon in 1981 with further developments by Yoon in 1987, and Hwang, Lai and Liu in 1993. TOPSIS is based on the concept that the chosen alternative should have the shortest geometric distance from the positive ideal solution (PIS) and the longest geometric distance from the negative ideal solution (NIS).

## Installation


```bash
pip install Topsis-Gursangat-101917025
```

## Usage

```
>>> import pandas as pd
>>> from topsis_101917025 import topsiscalc as t
>>> raw=pd.DataFrame({"CR": ['M1', 'M2', 'M3', 'M4', 'M5'], "A": [250, 200, 300, 275, 225], "B": [16, 16, 32, 32, 16], "C": [12, 8, 16, 8, 16], "D": [5, 3, 4, 4, 2]})
>>> w=[1,1,1,1]
>>> i=['-','+','+','+']
>>> t.topsis(raw,w,i,'result.csv')
```

w1,w2,w3,w4 represent weights, and i1,i2,i3,i4 represent impacts where 1 is used for maximize and 0 for minimize. 
Size of w and i is equal to number of features. 

Note that the first row and first column of dataset is dropped

Rank 1 signifies best decision

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

