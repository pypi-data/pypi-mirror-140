# TOPSIS-Python

Submitted By: **Shikhar 101917064**

***

## What is TOPSIS

**T**echnique for **O**rder **P**reference by **S**imilarity to **I**deal
**S**olution (TOPSIS) originated in the 1980s as a multi-criteria decision
making method. TOPSIS chooses the alternative of shortest Euclidean distance
from the ideal solution, and greatest distance from the negative-ideal
solution. 

<br>

## How to use this package:

Install it by using command : pip install Topsis_Shikhar_101917064
After installing, Topsis_Shikhar_101917064  can be run as shown in the following example:

### In Command Prompt
```
>> python
>> import pandas as pd
>> df = pd.read_csv("data.csv")
>> import Topsis_Shikhar_101917064
>> Topsis_Shikhar_101917064.topsis(df,"1,1,1,1","+,-,+,-") 
```
<br>

### In Python IDLE:
```
>>> import pandas as pd
>>> from Topsis_Shikhar_101917064 import topsis
>>> df = pd.read_csv("data.csv")
>>> weight = "1,1,1,1"
>>> impact = "+,-,+,-"
>>> topsis(df,weight,impact)
```

<br>

## Sample dataset

The decision matrix (`a`) should be constructed with each row representing a Model alternative, and each column representing a criterion like Accuracy, R<sup>2</sup>, Root Mean Squared Error, Correlation, and many more.

Model | Correlation | R<sup>2</sup> | RMSE | Accuracy
------------ | ------------- | ------------ | ------------- | ------------
M1 |	0.79 | 0.62	| 1.25 | 60.89
M2 |  0.66 | 0.44	| 2.89 | 63.07
M3 |	0.56 | 0.31	| 1.57 | 62.87
M4 |	0.82 | 0.67	| 2.68 | 70.19
M5 |	0.75 | 0.56	| 1.3	 | 80.39

Information of benefit positive(+) or negative(-) impact criteria should be provided in `I`.

<br>

## Output

```
Model   Score    Rank
-----  --------  ----
  1    0.772      2
  2    0.225      5
  3    0.438      4
  4    0.523      3
  5    0.811      1
```
<br>
The rankings are displayed in the form of a dataframe, with the 1st rank offering us the best decision, and last rank offering the worst decision making, according to TOPSIS method.
