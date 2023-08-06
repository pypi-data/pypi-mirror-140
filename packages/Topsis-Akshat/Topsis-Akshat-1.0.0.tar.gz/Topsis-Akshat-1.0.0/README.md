# (TOPSIS)Technique for Order of Preference by Similarity to Ideal Solution 
It takes input from command line and creates a .csv file containing TOPSIS score and ranks.

## Installation
```pip install Topsis-Akshat```

## How to use it?
Open terminal and type the input in following format
import topsis
topsis.topsis(<InputDataFile>, <Weights>, <Impacts>, <ResultFileName>)
e.g.
topsis.topsis("data.csv", "1,1,1,1,1", "+,-,+,-,+", "output.csv")

## License

© 2022 Akshat Gupta

This repository is licensed under the MIT license. See LICENSE for details.