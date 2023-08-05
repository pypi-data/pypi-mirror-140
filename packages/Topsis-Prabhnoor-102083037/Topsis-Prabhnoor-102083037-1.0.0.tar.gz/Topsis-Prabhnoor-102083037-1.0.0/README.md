
# Package for calculating TOPSIS score and ranking of a given dataframe

Submitted by:
- Prabhnoor Singh
- 102083037
- 3CO12

### Description

The Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS) is a multiple-criteria decision making (MCDM) method.

### 1. Usage

#####  a) topsis.norm_dataframe(data)  

Normalize all the columns  except 1st(treated as index); distributive normalization

##### b) topsis.topsis_calc(data,weights,impacts)  

Calculates and returns the topsis score and rank for the given arguments

### 2. Arguments

##### a) topsis.norm_dataframe(data)

  1. data  
    
    A dataframe with m rows and n columns; First column is treated as index; All the calculations are done from second column onwards

##### b) topsis.topsis_calc(data,weights,impacts)

  1. data  
        
    A dataframe with m rows for m alternatives and n columns for n-1 criterions. First column is treated as index

  2. weights

    A numeric list with length equal to number of columns (from second to last columns) in dataframe for weights of criterions.

  3. impacts

    A character list of "+" and "-" signs for the way that each criterion influences on the alternatives.

### 3. Value (return)

##### a) topsis.norm_dataframe(data)  

A normalized dataframe (distributive normalization)

##### b) topsis.topsis_calc(data,weights,impacts)  

Input dataframe with  2 additional columns

  * TOPSIS Score  
    
    TOPSIS score of alternatives.

  * Rank  
  
    Rank of alternatives based on TOPSIS scores.

### 4. Installation
```
> pip install Topsis-Prabhnoor-102083037
```

### 5. Example
```
>>> import pandas as pd
>>> from topsispackage_prabhnoorsingh import topsis
>>> raw=pd.DataFrame({"CR": ['M1', 'M2', 'M3', 'M4', 'M5'], "A": [250, 200, 300, 275, 225], "B": [16, 16, 32, 32, 16], "C": [12, 8, 16, 8, 16], "D": [5, 3, 4, 4, 2]})
>>> w=[0.25,0.25,0.25,0.25]
>>> i=['-','+','+','+']
>>> topsis.norm_dataframe(raw)
>>> topsis.topsis_calc(raw,w,i)
```