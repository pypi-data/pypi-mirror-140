# Topsis
Topsis-Tarush-102083060 is a python package to implement Multiple criteria decision making (MCDM) using TOPSIS. It takes data, calculates topsis score and ranks the data according to the score.

## Installation
Run the following command in the terminal to install the package:<br />
```pip install Topsis-Tarush-102083060```

## Importing and Using in Source File
Run the following commands to import the package into your python file:<br />
```
topsis = __import__('Topsis-Tarush-102083060')
topsis.main()
```
## How to get Output File
To get the output file with topsis score and rank you need to provide 4 arguments- csv filename, weights, impacts and output filename and then run on terminal in order to generate output file.<br /> 
Sample Case:<br />
```python filename.py data.csv "1,2,1,1,2" "+,-,+,-,-" outputfilename.csv```

## License
Copyright(c) 2022 Tarush Srivastava

