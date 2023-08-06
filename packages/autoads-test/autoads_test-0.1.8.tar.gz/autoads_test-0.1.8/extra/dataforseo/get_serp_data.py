import pandas as pd
from make_get_SERP import make_live_request,get_response,get_results, make_request

task_type = [
    # 'organic',
    # 'related_searches',
    'people_also_ask',
    # 'top_stories',
    # 'knowledge_graph'
]

task_params = {
    # 'organic': ['url', 'description', 'extended_people_also_search'],
    # 'related_searches' : Not required
    'people_also_ask': ['title', 'title2', 'url', 'description'],
    # top_stories['items'] params
    # 'top_stories': ['domain', 'title', 'date', 'url'],
    # 'knowledge_graph': ['text', 'title', 'url', 'title']
}

response = make_live_request("crypto 401k",'weilbacherindustries@gmail.com','05f014a493983975')[0]
df = get_results(response,task_type,task_params)
print(df['people_also_ask_title'])