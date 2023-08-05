TOPSIS.
Submitted By: Prateek Rai.

</br>

Type: Package.

Title: TOPSIS method for multiple-criteria decision making (MCDM).

Version: 1.0.0.


Author: Prateek Rai.

Maintainer: Prateek Rai prateek11rai@gmail.com.

</br>

Description: Evaluation of alternatives based on multiple criteria using TOPSIS method.

What is TOPSIS?
Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) originated in the 1980s as a multi-criteria decision making method. TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution, and greatest distance from the negative-ideal solution.


How to install this package : 
pip install Topsis-Prateek-101916078

In Command Prompt : 
python topsis data.csv "1,1,1,1,1" "+,+,-,+,+" result.csv



Input file (data.csv)
The decision matrix should be constructed with each row representing a Model alternative, and each column representing a criterion like Accuracy, R2, Root Mean Squared Error, Correlation, and many more. The file should be put in the command line as the location of the file.

| Fund Name |  P1  |  P2  | P3  |  P4  |   P5   |
| M1        | 0.73 | 0.53 | 3.4 |  46  |  12.67 |
| M2        | 0.72 | 0.52 | 4.1 |  35  |  10.09 |
| M3        | 0.83 | 0.69 | 3.1 | 48.6 |  13.31 |
| M4        | 0.85 | 0.72 | 4.3 | 59.8 |  16.42 |
| M5        | 0.93 | 0.86 | 4.9 | 64.3 |  17.75 |
| M6        | 0.73 | 0.53 | 4.7 | 44.1 |  12.52 |
| M7        | 0.88 | 0.77 | 6.3 | 41.7 |  12.41 |
| M8        | 0.8  | 0.64 | 4.8 | 67.4 |  18.41 |

Weights (weights) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in impacts.


Output file (result.csv)

| Fund Name |  P1  |  P2  | P3  |  P4  |   P5   | Topsis Score        | Rank |
| M1        | 0.73 | 0.53 | 3.4 |  46  |  12.67 | 0.5443557844202768  |  4   | 
| M2        | 0.72 | 0.52 | 4.1 |  35  |  10.09 | 0.4256480475457405  |  6   |
| M3        | 0.83 | 0.69 | 3.1 | 48.6 |  13.31 | 0.7477966268745603  |  1   |
| M4        | 0.85 | 0.72 | 4.3 | 59.8 |  16.42 | 0.6228391928555446  |  3   |
| M5        | 0.93 | 0.86 | 4.9 | 64.3 |  17.75 | 0.6268025462066721  |  2   |
| M6        | 0.73 | 0.53 | 4.7 | 44.1 |  12.52 | 0.3278090845190438  |  7   |
| M7        | 0.88 | 0.77 | 6.3 | 41.7 |  12.41 | 0.3182486586359413  |  8   |
| M8        | 0.8  | 0.64 | 4.8 | 67.4 |  18.41 | 0.47120452726540807 |  5   |
				

The output file contains columns of input file along with two additional columns having *Topsis_score* and *Rank*