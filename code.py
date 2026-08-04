import pandas as pd
pd.set_option('display.max_columns', None)

accepted_file= pd.read_csv("accepted_2007_to_2018Q4.csv")
rejected_file= pd.read_csv("rejected_2007_to_2018Q4.csv")

print(rejected_file.columns)

