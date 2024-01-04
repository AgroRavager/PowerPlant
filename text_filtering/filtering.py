import pandas as pd

# this file is used to convert text files in csv format to a .csv file

read = pd.read_csv('test3.txt') # enter name of the text file here
read.to_csv('test3.csv') # enter name of resulting csv file here

print(read)