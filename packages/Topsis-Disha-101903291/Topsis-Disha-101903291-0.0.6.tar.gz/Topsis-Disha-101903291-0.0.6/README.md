# topsis-py
Topsis_Disha is a library for calculating topsis score and ranking them according to the score.
## Installation
pip install Topsis-Disha-101903291
## Code Snippet
from topsis import main
main()
## Usage in terminal
python <filename.py> <data.csv> '1,1,1,1,1' '+,+,-,+,+' <result.csv>
## Input File (input.csv)
In this script, the first column should be named 'Fund Name' for the script to work correctly

| Fund Name | P1   | P2   | P3   | P4    |
| --------- | ---- | ---- | ---- | ----- |
| M1        | 0.79 | 0.62 | 1.25 | 60.89 |
| M2        | 0.66 | 0.44 | 2.89 | 63.07 |
| M3        | 0.56 | 0.31 | 1.57 | 62.87 |
| M4        | 0.82 | 0.67 | 2.68 | 70.19 |
| M5        | 0.75 | 0.56 | 1.3  | 80.39 |

## Output file (result.csv)

| Fund Name | P1   | P2   | P3   | P4    | Topsis Score | Rank |
| --------- | ---- | ---- | ---- | ----- | ------------ | ---- |
| M1        | 0.79 | 0.62 | 1.25 | 60.89 | 0.7722       | 2    |
| M2        | 0.66 | 0.44 | 2.89 | 63.07 | 0.2255       | 5    |
| M3        | 0.56 | 0.31 | 1.57 | 62.87 | 0.4388       | 4    |
| M4        | 0.82 | 0.67 | 2.68 | 70.19 | 0.5238       | 3    |
| M5        | 0.75 | 0.56 | 1.3  | 80.39 | 0.8113       | 1    |

The output file contains columns of input file along with two additional columns having **Topsis Score** and **Rank**
