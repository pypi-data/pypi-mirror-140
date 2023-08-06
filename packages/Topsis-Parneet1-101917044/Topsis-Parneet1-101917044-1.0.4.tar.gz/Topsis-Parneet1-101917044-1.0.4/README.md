Topsis-python
TOPSIS
Submitted By: Parneet Kaur Rakhra
Title: Multiple Creteria Decision Making (MCDM) Using TOPSIS
TOPSIS: Technique for Order of Preference By Similarity to Ideal Solution

What is TOPSIS?
Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) originated in the 1980s as a multi-criteria decision making method. TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution, and greatest distance from the negative-ideal solution.

Algorithm used in the Program:
Step 1:
Check whether the arguments entered by users are sufficient as per the requirements of our package.
Command should be like: topsis data_file.csv,"weights","impacts",result.csv

Step2:
Check whether weights and impact have same number of elements as that of number of columns in the csv file.

Step3:
Convert the column having categorical values to numerical values in the dataset.

Step4:
Vector normalisation is performed on the dataset and calculate the weighted normalised decision matrix..

Step5:
Calculate ideal best and ideal worst value in the dataset

Step6:
Calculate Euclidean distance from ideal best and ideal worst value.

Step7:
Finally calculate the Topsis Score and Rank

The output file contains columns of input file along with two additional columns having Topsis_score and Rank