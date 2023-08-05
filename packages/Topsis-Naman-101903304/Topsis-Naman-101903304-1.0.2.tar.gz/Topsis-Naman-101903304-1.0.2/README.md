# <div align=center> TOPSIS implementation in Python


## What is TOPSIS

**T**echnique for **O**rder **P**reference by **S**imilarity to **I**deal
**S**olution (TOPSIS) originated in the 1980s as a multi-criteria decision
making method. TOPSIS chooses the alternative of shortest Euclidean distance
from the ideal solution, and greatest distance from the negative-ideal
solution. More details at [wikipedia](https://en.wikipedia.org/wiki/TOPSIS).

<br>

## Installation
Use the package manager pip to install this package.

```
pip install Topsis-Naman-101903304
```

## How to use this package ?

<br>


### In Terminal
```
$ topsis data.csv "1,1,1,1,2" "+,+,-,+,+" output.csv
```
<br>

### In Python:
```python
from topsis import TOPSIS

filepath = "input.csv"
weights  = "1,1,1,1,2"
impacts  = "+,-,+,-,+"
output   = "output.csv"

topsis = TOPSIS(filepath, impacts, weights, output)

# Method 1: Stepwise

topsis.readCSV()
topsis.normalize()
topsis.weight_assignment()
topsis.find_ibw()
topsis.euclidean_distance()
topsis.performance_score()
topsis.find_rank()
topsis.storeCSV(output)

# Method 2: Automated

topsis.auto()


"""
Attributs provided under TOPSIS :
filepath    : Input file path.
filename    : Extracted filename from filepath
impacts     : given impacts
weights     : given weithts
output      : output file name
odf         : output data
df          : modified dataframe
sp          : S+
sn          : S-
scores      : performance score
ideal_worst : V+
ideal_best  : V-

Usage:
    topsis = TOPSIS(filepath, impacts, weights, output)
    topsis.df
"""
```

<br>

## Sample dataset

Fund Name | P1   | P2   | P3  | P4   | P5
--------- | ---  | ---- | ----| ---- | ----
M1        | 0.92 | 0.71 | 4.5 | 43   | 12.59
M2        | 0.71 | 0.83 | 4.4 | 41.9 | 10.11
M3        | 0.77 | 0.62 | 3.5 | 33.2 | 13.2
M4        | 0.92 | 0.61 | 4.4 | 50.9 | 12.55
M5        | 0.7  | 0.88 | 6.7 | 43.7 | 16.91
M6        | 0.64 | 0.77 | 6.9 | 64.5 | 14.91
M7        | 0.68 | 0.44 | 4.5 | 31.1 | 13.83
M8        | 0.6  | 0.86 | 3   | 36.4 | 10.55


<br>

## Output

Fund Name | P1   | P2   | P3  | P4   | P5    | Topsis Score        | Rank
--------- | ---- | ---- | ----| ---- | ----- |  ---------------    |-----
M1        | 0.92 | 0.71 | 4.5 | 43.0 | 12.59 | 0.606157764635227   | 6.0
M2        | 0.71 | 0.83 | 4.4 | 41.9 | 10.11 | 0.630939331184659   | 3.0
M3        | 0.77 | 0.62 | 3.5 | 33.2 | 13.23 | 0.6376673741860752  | 2.0
M4        | 0.92 | 0.61 | 4.4 | 50.9 | 12.55 | 0.44683746237145194 | 7.0
M5        | 0.7  | 0.88 | 6.7 | 43.7 | 16.91 | 0.6223296058794716  | 4.0
M6        | 0.64 | 0.77 | 6.9 | 64.5 | 14.91 | 0.36651530625461226 | 8.0
M7        | 0.68 | 0.44 | 4.5 | 31.1 | 13.83 | 0.6381151861152682  | 1.0
M8        | 0.6  | 0.86 | 3.0 | 36.4 | 10.55 | 0.6124418308455085  | 5.0

<br>

The output file contains columns of input file along with two additional columns having **Topsis Score** and **Rank**