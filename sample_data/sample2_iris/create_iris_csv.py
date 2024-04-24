'''
Load the iris dataset from sklearn and save it as a csv file
'''

import pandas as pd
from sklearn import datasets

def main():
    # Load iris dataset
    iris = datasets.load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    
    # Save as csv
    df.to_csv('iris.csv', index=False)
    
if __name__ == '__main__':
    main()
    