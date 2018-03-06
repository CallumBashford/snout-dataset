import numpy as np
import pandas as pd

"""
Script that splits dataset into training/testing datasets by a 80/20 ratio.
"""

np.random.seed(1)
labels = pd.read_csv('data/food_labels.csv')

grouped = labels.groupby('filename')

grouped_list = [grouped.get_group(x) for x in grouped.groups]

print(len(grouped_list))

train_index = np.random.choice(len(grouped_list), size=int(len(grouped_list)*.8), replace=False)
test_index = np.setdiff1d(list(range(len(grouped_list))), train_index)

print(len(train_index), len(test_index))

train = pd.concat([grouped_list[i] for i in train_index])
test = pd.concat([grouped_list[i] for i in test_index])

print(len(train), len(test))

train.to_csv('data/train_labels.csv', index=None)
test.to_csv('data/test_labels.csv', index=None)
