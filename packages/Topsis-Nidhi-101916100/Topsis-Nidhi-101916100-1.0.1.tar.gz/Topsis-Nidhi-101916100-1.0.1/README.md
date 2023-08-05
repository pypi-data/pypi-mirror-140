TOPSIS
Submitted By: Nidhi Bhasker

Type: Package.

Title: TOPSIS method for multiple-criteria decision making (MCDM).

Version: 1.0.1.

Author: Nidhi Bhasker.

Maintainer: Nidhi Bhasker nidhibhasker001@gmail.com.

Description: Evaluation of alternatives based on multiple criteria using TOPSIS method.

What is TOPSIS?
Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) originated in the 1980s as a multi-criteria decision making method. TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution, and greatest distance from the negative-ideal solution.


How to install this package:
pip install topsis-nidhi
In Command Prompt
python topsis data.csv "1,1,1,1,1" "+,-,+,-,+" result.csv
Input file (data.csv)

Weights (weights) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in impacts.

Output file (result.csv)

The output file contains columns of input file along with two additional columns having *Topsis_score* and *Rank*
