import os
import re
import uuid
import numpy as np
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from sentence_transformers import SentenceTransformer
from autoads.models import get_similarity_matrix,get_similarity_api
from autoads.keywords import get_keywords_metrics,make_live_request,get_results
from autoads.gads import get_existing_keywords

email = 'weilbacherindustries@gmail.com' # email in data for seo
api_key = '05f014a493983975' # api key for data for seo
match_extract = ['exact', 'phrase']  # exact, phrase, broad
df_path = 'data/df_final.csv' # csv where keywords are stored
save_path = 'data' #all the csvs will be stored on this folder
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id
first_threshold = 0.8 # similarity threshold for keyword similarity
second_threshold = 0.8 # similarity threshold for description similarity
third_threshold = 0.35 # similarity threshold for seed keyword and keywords3
conversion_threshold = 1 #  get conversion >= conversion_threshold
allowed_funnels = ['LF','MF'] # available options LF, MF, UF
similarity_model_path = 'Maunish/ecomm-sbert' # this model is already uploaded on huggingface so no need to download

os.makedirs(save_path,exist_ok=True)
googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df = pd.read_csv(df_path)

print("Getting existing keywords")
df_existing = get_existing_keywords(googleads_client,customer_id)
df_existing = pd.read_csv(save_path+'/df_existing.csv')
keywords_to_remove = df_existing.query("(camp_status == 'ENABLED') & \
                                        (adgroup_status == 'ENABLED') &\
                                        (keyword_status == 'ENABLED')")['keyword_name'].unique().tolist()
df = df[~df["Keywords"].isin(keywords_to_remove)] # if campaign in enabled and keyword clash remove it.

#First pass of filters
print("Applying filters on the data")
df = df[~df["Keywords"].isin(keywords_to_remove)]
df = df[df['similarity'] >= first_threshold]
df = df[df['lf/mf/uf'].isin(allowed_funnels)].reset_index(drop=True)
df = df.drop_duplicates("Keywords")

#Second pass of similarity with page titles
tasks = [
    'organic',
    # 'people_also_ask',
]
task_params = {
    'organic': ['description'],
    # 'people_also_ask': ['title'],
}

print("Getting meta titles from SERP")
seed_keywords = df["Keywords2"].unique().tolist()
for keyword in seed_keywords:
    print(keyword)
    response = make_live_request(keyword,email,api_key,depth=5)
    results = get_results(response,tasks,task_params)
    if results.get('organic_description') and response['tasks'][0]['result']:
        organic_description = str([x.replace(",","") for x in results['organic_description']])
        organic_description = organic_description.replace("[","").replace("]","")
        df.loc[df["Keywords2"]== keyword,'seed_organic_description'] = str(organic_description)
    else:
        df.loc[df["Keywords2"]== keyword,'seed_organic_description'] =  keyword

all_keywords = df["Keywords"].unique().tolist()
for keyword in all_keywords:
    print(keyword)
    response = make_live_request(keyword,email,api_key,depth=5)
    results = get_results(response,tasks,task_params)
    if results.get('organic_description') and response['tasks'][0]['result']:
        organic_description = str([x.replace(",","") for x in results['organic_description']])
        organic_description = organic_description.replace("[","").replace("]","")
        df.loc[df["Keywords"]== keyword,'organic_description'] = organic_description
    else:
        df.loc[df["Keywords"]== keyword,'organic_description'] = [keyword]  

model = SentenceTransformer(similarity_model_path)

print("Performing similarity using organic description")
for i,row in df.iterrows():
    all_titles = row['seed_organic_description'].split(',')
    all_seed_titles = row['organic_description'].split(',')
    similarity_matrix = get_similarity_matrix(model,all_titles,all_seed_titles)
    df.loc[i,'second_similarity'] = similarity_matrix.max(axis=1).mean()

df = df[df['second_similarity'] >= second_threshold]

def remove_word(row):
    keyword1 = re.split("\s|(?<!\d)[,-](?!\d)",row['Keywords'])
    keyword2 = re.split("\s|(?<!\d)[,-](?!\d)",row['Keywords2'])
    keyword = [x for x in keyword1 if x not in keyword2]
    return "" if len(keyword) == 0 else ' '.join(keyword)

df['Keywords3'] = df.apply(remove_word,axis=1)

keywords1 = df['Keywords2'].tolist()
keywords2 = df['Keywords3'].tolist()
df['third_similarity'] = get_similarity_api(model,keywords1,keywords2)

df = df[df['third_similarity'] >= third_threshold]

df_enabled = df_existing.query("(camp_status == 'ENABLED') & \
                                (adgroup_status == 'ENABLED') &\
                                (keyword_status == 'ENABLED') & \
                                (camp_experiment_type != 'EXPERIMENT')")

df_paused = df_existing.query("camp_status == 'PAUSED'")

if len(df) != 0:
    if len(df_enabled) == 0:
        print("No adgroups to expand to")
    else:
        print("Finding similarity with existing keywords")
        existing_campaign_id = df_enabled['camp_id'].tolist()
        existing_campaign_status = df_enabled['camp_status'].tolist()
        existing_keywords = df_enabled['keyword_name'].tolist()
        new_keywords = df['Keywords'].tolist()
        model = SentenceTransformer(similarity_model_path)
        similarity_matrix = get_similarity_matrix(model,existing_keywords,new_keywords)
        similarity_indexes = np.where(similarity_matrix>=first_threshold)

        if len(similarity_indexes[0]) != 0:
            keyword_campaign_id_pair = list()
            for i,j in zip(similarity_indexes[0],similarity_indexes[1]):
                keyword_campaign_id_pair.append((new_keywords[i],
                                                existing_campaign_id[j],
                                                existing_campaign_status[j],
                                                similarity_matrix[i][j]))

            df_expand = pd.DataFrame(keyword_campaign_id_pair,columns=['Keywords','camp_id','camp_status','similarity'])
            df_expand = df_expand.loc[df_expand.groupby(['Keywords'])['similarity'].idxmax()].reset_index(drop=True)
            df_expand = df_expand.loc[df_expand['similarity']!=1]
            if len(df_expand) != 0:
                df_expand.to_csv(save_path+'/df_expand.csv',index=False)
                df_expand = df_expand.drop('similarity',axis=1)
                df = df.merge(df_expand,how='left',on='Keywords')
            else:
                print("All the matching keywords are already present in the ad group")
        else:
            print("No matching campaigns found for expanding")

        print("Finding keywords to add in already existing campaign")
        already_exist_campaign = df_enabled['camp_name'].tolist()
        df.loc[df["Keywords2"].isin(df_enabled['camp_name'].tolist()),'camp_id'] = df_enabled.loc[df_enabled["camp_name"].isin(df['Keywords2'].tolist()),'camp_id']

    # code for altering campaign names
    paused_campaigns = df_paused['camp_name'].unique().tolist()
    for i,row in df[df['camp_id'].isna()].iterrows():
        if row['Keywords2'] in paused_campaigns:
            df.loc[i,'Keywords2'] = row['Keywords2'] + "_" + str(uuid.uuid4())

df = df.drop_duplicates('Keywords')

if len(df) == 0:
    print("No new keywords to add")
else:
    print("Getting Keywords metrics")
    # df = get_keywords_metrics(email,api_key,df,match_extract)

df_existing.to_csv(save_path+'/df_existing.csv',index=False)
df.to_csv(save_path+'/keywords_to_upload.csv',index=False)
