# %%
import json

businesses = []
for line in open('yelp_dataset/business.json', 'r'):
    businesses.append(json.loads(line))
# %%
len(businesses)
# %%
categories = []
for b in businesses:
    if b['categories'] not in categories:
        categories.append(b['categories'])
categories
# %%
withcategories = list(filter(lambda b: b['categories'] != None, businesses))
len(withcategories)
# %%
restaurants = list(
    filter(lambda b: 'food' in [x.lower() for x in b['categories']] or 'restaurant' in [x.lower() for x in b['categories']], withcategories))

# %%
len(restaurants)
# %%
restaurants[0]
# %%
restaurant_ids = [r['business_id'] for r in restaurants]
# %%
reviews = []
for line in open('yelp_dataset/review.json', 'r'):
    reviews.append(json.loads(line))
# %%
len(reviews)
# %%
reviews[0]
# %%
restaurant_reviews = list(filter(lambda r: r['business_id'] in restaurant_ids, reviews))
# %%
len(restaurant_reviews)
# %%
with open('restreviews.json', 'w') as f:
    json.dump(restaurant_reviews, f)

# %% md
## Working off filtered reviews json
# %%
import json

for line in open('restreviews.json', 'r'):
    reviewsnew = json.loads(line)
# %%
len(reviewsnew)
# %%
reviewsnew[0]
# %%
users = [r['user_id'] for r in reviewsnew]
unique_users = list(set(users))
len(unique_users)
# %%
from collections import Counter

user_count = dict(Counter(users))
# %%
user_count
# %%
over10 = {x: user_count[x] for x in user_count if user_count[x] >= 10}
# %%
len(over10)
# %%
users10 = list(over10)
# %%
# filtering down reviews to users who've reviewed 10 or more businesses

ten_reviews = list(filter(lambda r: r['user_id'] in users10, reviewsnew))
# %%
with open('user10reviews.json', 'w') as f:
    json.dump(ten_reviews, f)
# %%
len(ten_reviews)
# %%
businesses = [r['business_id'] for r in reviewsnew]
unique_businesses = list(set(businesses))
len(unique_businesses)
# %%
cut = [(r['user_id'], r['business_id'], r['stars']) for r in reviewsnew]
# %%
indexed_users = {v: k for k, v in enumerate(unique_users)}
indexed_businesses = {v: k for k, v in enumerate(unique_businesses)}
# %%
indexed_data = list(map(lambda r: (indexed_users[r[0]], indexed_businesses[r[1]], r[2]), cut))
# %%
indexed_data[:10]
# %%
import csv

with open('reviews.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    for tup in indexed_data:
        writer.writerow(tup)
# %%
import pandas as pd

reviews = pd.read_csv('reviews.csv')
reviews.head()
# %% md
## Cleaning Data for Final Model
# %%
import json

for line in open('user10reviews.json', 'r'):
    finalreviews = json.loads(line)
# %%
finalbusinesses = [r['business_id'] for r in finalreviews]
# %%
final_unique_businesses = list(set(finalbusinesses))
# %%
final_indexed_businesses = {v: k for k, v in enumerate(final_unique_businesses)}
# %%
businesses = []
for line in open('yelp_dataset/business.json', 'r'):
    businesses.append(json.loads(line))
# %%
businesses[0]
# %%
len(businesses)
# %%
final_businesses_dicts = list(filter(lambda b: b['business_id'] in final_unique_businesses, businesses))
# %%
len(final_businesses_dicts)
# %%
with open('finalbusinesses.json', 'w') as f:
    json.dump(final_businesses_dicts, f)
# %%
for b in final_businesses_dicts:
    b['id'] = final_indexed_businesses[b['business_id']]
# %%
with open('finalbusinessesindexed.json', 'w') as f:
    json.dump(final_businesses_dicts, f)
# %%
