Created for college assignment
Topsis package is used for perfoming topsis over any data file.

Data file should be of minimum 3 columns
Impacts must be either +ve or -ve.
Impacts and weights must be separated by ‘,’
Features
Output file will be generated after perfoming topsis.
Installation
To install the package use

pip install Topsis_Shivang_101917183
Usage

from Topsis_Shivang_101917183 import topsis

#creating the topsis object
#t = topsis(INPUT_FILENAME,WEIGHT_STRING,IMPACT_STRING,OUTPUT_FILENAME)

# Example
t = tp.topsis("data.xlsx", "1,1,1,2,1", "+,-,-,+,-", "output.csv")

#Calculate TOPSIS
t.calculate()
License
MIT