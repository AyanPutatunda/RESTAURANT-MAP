# %% md
# Model Testing
### Import libraries
# %%
import os
import json
import pandas as pd
# %%
from surprise import Dataset
from surprise import Reader
from surprise import SVD, evaluate, accuracy
from surprise import dump
from surprise.model_selection import cross_validate, train_test_split
from surprise.model_selection import GridSearchCV

# %% md
# Testing on Final Data
# %%
file_path = os.path.expanduser('finaldata.csv')
# %%
reader = Reader(line_format='user item rating', sep=',')
# %%
data = Dataset.load_from_file(file_path, reader=reader)
# %%
data.split(n_folds=5)
# %% md
## Chosen Model: SVD (results of other models at the bottom)
# %%
svd = SVD()
# %%
evaluate(svd, data, measures=['RMSE', 'MAE'])
# %% md
## Gridsearch 1 -- tuning bias and learning rate
# %%
param_grid = {'biased': [True, False], 'lr_all': [0.001, 0.005, 0.05]}
gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)
# 'n_epochs': [10, 20, 50],'reg_all': [0.02, 0.05, 0.08]
# %%
gs.fit(data)
# %%
results = gs.cv_results
# %%
results_df = pd.DataFrame.from_dict(gs.cv_results)
results_df.to_csv('results.csv')
# %%
results_df
# %% md
#### Best LR = 0.005, Bias = True
# %% md
## Gridsearch 2 -- tuning n_factors
# %%
param_grid = {'n_factors': [1, 5, 10], 'biased': [True], 'lr_all': [0.005],
              'n_epochs': [20]}

gs2 = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)
# 'n_epochs': [10, 20, 50],'reg_all': [0.02, 0.05, 0.08]
# %%
gs2.fit(data)
# %%
results = gs2.cv_results
# %%
results_df = pd.DataFrame.from_dict(results)
results_df
# %% md
#### Best - 1 factor (also tested higher values)
# %% md
# Gridsearch 3 -- tuning n_epochs
# %%
param_grid = {'n_epochs': [10, 20, 50], 'n_factors': [1], 'biased': [True], 'lr_all': [0.005]}
gs3 = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)
# %%
gs3.fit(data)
# %%
results = gs3.cv_results
results_df = pd.DataFrame.from_dict(results)
results_df
# %% md
#### Best n_epochs = 20
# %% md
# Gridsearch 4: Tuning reg_all
# %%
param_grid = {'n_epochs': [20], 'n_factors': [1], 'biased': [True],
              'lr_all': [0.005], 'reg_all': [0.05, 0.06, 0.07]}
gs4 = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)

# %%
gs4.fit(data)
# %%
results = gs4.cv_results
results_df = pd.DataFrame.from_dict(results)
results_df
# %%
results_df[['rank_test_rmse', 'rank_test_mae']]
# %% md
#### Best reg = 0.06
# %% md
# Other Models (not used)
# %%
svdpp = SVDpp()
# %%
evaluate(svdpp, data, measures=['RMSE', 'MAE'])
# %%
nmf = NMF()
# %%
evaluate(nmf, data, measures=['RMSE', 'MAE'])
# %% md
# Best Model
# %%
final = SVD(n_epochs=20, n_factors=1, biased=True,
            lr_all=0.005, reg_all=0.06)
# %%
data = Dataset.load_from_file(file_path, reader=reader)
trainset, testset = train_test_split(data, test_size=.2)
# %%
import time

start = time.time()
# %%
final.fit(trainset)
runtime = time.time() - start
print(runtime)
# %%
predictions = final.test(testset)
# %%
accuracy.rmse(predictions)
# %%
accuracy.mae(predictions)
# %%
dump.dump('finalmodel', algo=final, predictions=predictions, verbose=1)
# %%
preds, model = dump.load('finalmodel')
# %% md
# Getting Predictions
# %% md
number_of_businesses = 73100

number_of_users = 81416
# %%
model.predict('30678', '51871')


# %% md
### Mapping restaurant information to item IDs
# %%
def find(f, seq):
    for item in seq:
        if f(item):
            return item


# %%
def get_info(iid):
    return find(lambda b: iid == b['id'], businesses)


# %%
get_info(78)
# %%
import json

with open('finalbusinessesindexed.json') as f:
    businesses = json.load(f)


# %%
def get_n_preds(uid, n):
    ratings = []
    for i in range(1, 73101):
        pred = model.predict(str(uid), str(i))
        ratings.append((int(pred.iid), pred.est))
    ratingsdesc = sorted(ratings, reverse=True, key=lambda x: x[1])[:n]
    namedratings = [(get_info(r[0])['name'], r[1]) for r in ratingsdesc]
    return namedratings


# %%
get_all_preds(44, 10)
# %%
import csv

with open('finaldata.csv', 'r') as f:
    reader = csv.reader(f)
    reviews = list(reader)


# %%
def get_reviewed_restaurants(uid, desc=True):
    userreviews = list(filter(lambda r: r[0] == str(uid), reviews))
    ratings = [r[2] for r in userreviews]
    restaurants = list(map(lambda r: get_info(int(r[1])), userreviews))
    names = [r['name'] for r in restaurants]
    if desc == True:
        return sorted(list(zip(names, ratings)), reverse=True, key=lambda x: x[1])
    return sorted(list(zip(names, ratings)), key=lambda x: x[1])


# %%
get_reviewed_restaurants(81415)
# %%
