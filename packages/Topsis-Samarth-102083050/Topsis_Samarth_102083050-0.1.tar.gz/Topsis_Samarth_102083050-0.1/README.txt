Topsis Value Calculator

## Installation
$ pip install Topsis-Garvit-101903778==0.1

The package consists of two methods :
1). topsis_samarth(temp_dataset, dataset, number of columns, weights, impact) : It calculates the topsis value and gives rank. The data is saved as a csv file with name==result_filename.

2). main() : To run the topsis function by providing input from the command line use this method.

3). Normalisation(tem_dataset, nCol, weights): To normalise the values

4). Calculation(tem_dataset, nCol, impact): To calculate negative and positive values

Command Line syntax :
$ python <script_name> <input_data_file> <weights> <impacts> <output_data_file>

Note : weights and impacts should be provided as strings and input/output data file should be csv.

License -> MIT