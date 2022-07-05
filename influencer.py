import json
import requests
import networkx as nx


def search_for_data(query, url):
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    resp = requests.get(url, headers=headers, data=json.dumps(query)).json()
    return resp


def post_users():
    url = 'some elastic urls'
    query = {"size": 150, "query": {"bool": {"filter": {"script": {
        "script": {"source": "doc['favourites_count'].size() > 0 &&  doc['favourites_count'].value > 5",
                   "lang": "painless"}}}}}, "aggs": {"langs": {"terms": {"field": "social_user.id", "size": 65536}}}}
    user = search_for_data(query, url)
    users = []
    for i in range(len(search_for_data(query, url)['aggregations']['langs']['buckets'])):
        users.append(user['aggregations']['langs']['buckets'][i]['key'])
    return users


# adding some experimental number as a threshold.
def threshold(id):
    url = ''
    query = {"size": 0, "query": {"bool": {"must": [{"match": {"social_user.id": id}}]}},
             "aggs": {"likes_count": {"sum": {"field": "favourites_count"}},
                      "likes_average": {"avg": {"field": "favourites_count"}},
                      "comments_count": {"sum": {"field": "comment_count"}},
                      "comments_average": {"avg": {"field": "comment_count"}},
                      "retweets_count": {"sum": {"field": "retweet_count"}},
                      "followers_count": {"min": {"field": "social_user.followers_count"}},
                      "followings_count": {"min": {"field": "social_user.friends_count"}},
                      "posts_polarity_agg": {"avg": {"field": "polarity"}}}}
    query2 = search_for_data(query, url)
    retweets = query2['aggregations']['retweets_count']['value']
    likes = query2['aggregations']['likes_count']['value']
    comments = query2['aggregations']['comments_count']['value']
    posts = query2['hits']['total']['value']
    followers = query2['aggregations']['followers_count']['value']

    if query2['aggregations']['followings_count']['value'] is None:
        followings = followers + 1
    else:
        followings = query2['aggregations']['followings_count']['value'] + 1
    ter = (50 * retweets + followers + 100 * followers / followings + comments + likes) / 100
    likes_avg = query2['aggregations']['likes_average']['value']
    return retweets, likes, comments, posts, followers, followings, ter, likes_avg


# 1. only get datas from users with atleast one post that has more than one post with 500 or moe likes.
url2 = 'some elastic urls'
query = {"size": 10000, "_source": ["followings", "id", "screen_name"],
         "query": {"bool": {"filter": {"terms": {"id": post_users()}}}}}
length = len(search_for_data(query, url2)["hits"]["hits"])
influencer = search_for_data(query, url2)["hits"]["hits"]
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


# 3. set all influencer ranks to zero so that we can update them with new ranks.
for i in range(len(pr)):
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    url2 = 'some elastic urls'
    query3 = {"script": {"inline": "ctx._source.influencer_rank=params.value", "lang": "painless",
                         "params": {"value": list(pr.values())[i]}}, "query": {"match": {"id": list(pr.keys())[i]}}}
    res = requests.post(url2, headers=headers, data=json.dumps(query3)).json()
