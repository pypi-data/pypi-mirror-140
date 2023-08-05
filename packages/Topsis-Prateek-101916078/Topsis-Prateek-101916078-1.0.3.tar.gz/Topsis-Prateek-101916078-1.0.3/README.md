TOPSIS.
Submitted By: Prateek Rai.

</br>

Type: Package.

Title: TOPSIS method for multiple-criteria decision making (MCDM).

Version: 1.0.3.


Author: Prateek Rai.

Maintainer: Prateek Rai prateek11rai@gmail.com.

</br>

Description: Evaluation of alternatives based on multiple criteria using TOPSIS method.

What is TOPSIS?
Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) originated in the 1980s as a multi-criteria decision making method. TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution, and greatest distance from the negative-ideal solution.


How to install this package : 
pip install Topsis-Prateek-101916078

In Command Prompt : 
topsis data.csv "1,1,1,1,1" "+,+,-,+,+" result.csv



Input file (data.csv)
The decision matrix should be constructed with each row representing a Model alternative, and each column representing a criterion like Accuracy, R2, Root Mean Squared Error, Correlation, and many more. The file should be put in the command line as the location of the file.


Weights (weights) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in impacts.


Output file (result.csv)
				

The output file contains columns of input file along with two additional columns having *Topsis_score* and *Rank*