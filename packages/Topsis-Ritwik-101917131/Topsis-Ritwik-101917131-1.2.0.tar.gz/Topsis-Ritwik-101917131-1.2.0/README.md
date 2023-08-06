## Topsis_Ritwik

# TOPSIS

Created By: **Ritwik Khanna**.
Type: **Package**.

Title: **TOPSIS method for multiple-criteria decision making (MCDM)**.

Version: **1.2.0**.

Author: **Ritwik Khanna**.

Maintainer: **Ritwik Khanna <khannaritwik.rk@gmail.com>>**.

Description: **Evaluation of alternatives based on multiple criteria using TOPSIS method.**.

---

## What is TOPSIS?

**T**echnique for **O**rder **P**reference by **S**imilarity to **I**deal **S**olution
(TOPSIS) originated in the 1980s as a multi-criteria decision making method.
TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution,
and greatest distance from the negative-ideal solution.

<br>

## How to install this package:

```
>> pip install Topsis-Ritwik-101917131
```

### In Command Prompt

```
>> python topsis.py data.csv "1,1,1.5,1,2" "+,+,-,+,-" result.csv
```

## Input file (data.csv)

The decision matrix should be constructed with each row representing a Model alternative, and each column representing a criterion like Accuracy, R<sup>2</sup>, Root Mean Squared Error, Correlation, and many more.

| Model |  P1  |  P2  |  P3  |  P4  |  P5   |
| ----- | ---- | ---- | ---- | ---- | ----  |
| M1    | 0.84 | 0.71 | 6.7  | 42.1 | 12.59 |
| M2    | 0.91 | 0.83 | 7.0  | 31.7 | 10.11 |
| M3    | 0.79 | 0.62 | 4.8  | 46.7 | 13.23 |
| M4    | 0.78 | 0.61 | 6.4  | 42.4 | 12.55 |
| M5    | 0.94 | 0.88 | 3.6  | 62.2 | 16.91 |
| M6    | 0.88 | 0.77 | 6.5  | 51.5 | 14.91 |
| M7    | 0.66 | 0.44 | 5.3  | 48.9 | 13.83 |
| M8    | 0.93 | 0.86 | 3.4  | 37.0 | 10.55 |

Weights (`weights`) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in `impacts`.

<br>

## Output file (result.csv)

| Model |  P1  |  P2  |  P3  |  P4  |  P5   |  Topsis Score  | Rank |
| ----- | ---- | ---- | ---- | ---- | ----  |  ------------  | ---- |
| M1    | 0.84 | 0.71 | 6.7  | 42.1 | 12.59 |     0.4295     |  5   |
| M2    | 0.91 | 0.83 | 7.0  | 31.7 | 10.11 |     0.5055     |  4   |
| M3    | 0.79 | 0.62 | 4.8  | 46.7 | 13.23 |     0.5358     |  3   |
| M4    | 0.78 | 0.61 | 6.4  | 42.4 | 12.55 |     0.4185     |  6   |
| M5    | 0.94 | 0.88 | 3.6  | 62.2 | 16.91 |     0.5616     |  2   |
| M6    | 0.88 | 0.77 | 6.5  | 51.5 | 14.91 |     0.3983     |  8   |
| M7    | 0.66 | 0.44 | 5.3  | 48.9 | 13.83 |     0.4134     |  7   |
| M8    | 0.93 | 0.86 | 3.4  | 37.0 | 10.55 |     0.7332     |  1   |









<br>
The output file contains columns of input file along with two additional columns having **Topsis_score** and **Rank**