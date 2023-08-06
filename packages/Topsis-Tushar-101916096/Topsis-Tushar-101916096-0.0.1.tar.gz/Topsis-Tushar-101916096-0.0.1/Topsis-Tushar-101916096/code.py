def function_topsis(data, weights, impacts):
    import pandas as pd
    import numpy as np
    import sys
    if(len(sys.argv) != 5):
        raise Exception('Argument count incorrect!')

    data = pd.read_csv(sys.argv[1])

    if(len(data.columns) < 3):
        raise Exception("count should be > 3!")

    ans = data.apply(lambda s: pd.to_numeric(
        s, errors='coerce').notnull().all())
    temp = True
    for i in range(1, len(data.columns)):
        temp = temp & ans[i]
    if(temp == False):
        raise Exception("Enter Numeric Data!")

    weights = sys.argv[2]
    if(weights.count(",") != len(data.columns)-2):
        raise Exception("Incorrect no of weights!")
    weights = list(weights.split(","))
    for i in weights:
        if i.isalpha():
            raise Exception("Enter Numeric Weights!")
    if(len(weights) != len(data.columns)-1):
        raise Exception("Incorrect weight parameters count")
    weights = pd.to_numeric(weights)
    impacts = sys.argv[3]
    if(impacts.count(",") != len(data.columns)-2):
        raise Exception("Comma Incorrect")
    lst = list(impacts.split(","))
    if(len(lst) != len(data.columns)-1):
        raise Exception("Wrong impact count ")
    for i in lst:
        if i not in ['+', '-']:
            raise Exception("Wrong impact paramteres")
    impacts = [1 if i == '+' else -1 for i in lst]
    data.to_csv("101916096-data.csv", index=False)

    col1 = pd.DataFrame(data['Fund Name'])
    data.drop("Fund Name", inplace=True, axis=1)

    import topsispy as tp2
    a = data.values.tolist()
    x = tp2.topsis(a, weights, impacts)
    data["Topsis Score"] = x[1]
    data['Rank'] = data['Topsis Score'].rank(ascending=False)
    new_dataset = pd.concat([col1, data], axis=1)
    new_dataset.to_csv(sys.argv[4], index=False)
    return new_dataset
