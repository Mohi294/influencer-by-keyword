# social media influencer
this code finds influencers based on some keywords and some experimental pointings that is calculateed based on number of likes, followers, followings, etc. of users and then by ```networkx``` package and ```DiGraph``` gets pagerank of each user and gives it back to database.

The documentations of main packages are available in following links:
- networkx: https://networkx.org/documentation/stable/index.html

# Getting started

calculating each user's threshold(or points):

```python
 ter = (50 * retweets + followers + 100 * followers / followings + comments + likes) / 100
    likes_avg = query2['aggregations']['likes_average']['value']
```

getting users that have more than 100 threshold and using some directed weighted graph to achieve pageranks of each users:

```python
relations = []
item = []
for i in range(length):
    if threshold(influencer[i]['_source']['id'])[6] > 100:
        step = 0
        lengthFollowing = len(influencer[i]['_source']['followings'])
        for j in range(lengthFollowing):
            item.append(influencer[i]['_source']['id'])
            item.append(int(influencer[i]['_source']['followings'][j]['id_str']))
            item.append(threshold(influencer[i]['_source']['id'])[6])
            item = tuple(item)
            relations.append(item)
            item = []


# 2. getting users page ranks.
g = nx.DiGraph()
g.add_weighted_edges_from(relations)
pr = nx.pagerank(g)
```

# Requirements
Python 3.8+ is required. The following packages are required:
- [json](https://docs.python.org/3/library/json.html)
- [request](https://requests.readthedocs.io/) (for elastic database)
- [networkx](https://networkx.org/documentation/stable/index.html)

# important links
- Documentation: https://networkx.org/documentation/networkx-1.9/
- Source code: https://github.com/Mohi294/social-media-influencer/
- Issue tracker: https://github.com/Mohi294/social-media-influencer/issues/

# License
NetworkX is a Python library for studying graphs and networks. NetworkX is free software released under the BSD-new license.



