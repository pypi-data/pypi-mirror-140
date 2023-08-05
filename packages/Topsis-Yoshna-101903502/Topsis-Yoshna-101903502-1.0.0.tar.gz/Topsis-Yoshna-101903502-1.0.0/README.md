# TOPSIS-Python

Submitted By: _Yoshna Marwaha_

---

## What is TOPSIS

*Technique for **Order **Preference by **Similarity to **I*deal
*S*olution (TOPSIS) originated in the 1980s as a multi-criteria decision
making method. TOPSIS chooses the alternative of shortest Euclidean distance
from the ideal solution, and greatest distance from the negative-ideal
solution. More details at [wikipedia](https://en.wikipedia.org/wiki/TOPSIS).

<br>

## How to use this package:

Topsis-Yoshna-101903502 can be run as in the following example:

### In Command Prompt

> > topsis data.csv "1,1,1,1" "+,+,-,+" output.csv

<br>

### In Python IDLE:

> > > import pandas as pd
> > > from topsis_py.topsis import topsis
> > > dataset = pd.read_csv('data.csv').values
> > > d = dataset[:,1:]
> > > w = [1,1,1,1]
> > > im = ["+" , "+" , "-" , "+" ]
> > > topsis(d,w,im,output.csv)

<br>
<br>

The rankings are displayed in the form of a table using a package 'tabulate', with the 1st rank offering us the best decision, and last rank offering the worst decision making, according to TOPSIS method.
