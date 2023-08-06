import os
import pandas as pd
from autoads.gads import get_all_ads,get_existing_keywords,create_ad

from google.ads.googleads.client import GoogleAdsClient
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id
save_path = 'data'

os.makedirs(save_path,exist_ok=True)
client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df_ads_data = get_all_ads(client,customer_id)
df_exising = get_existing_keywords(client,customer_id)
df_exising = df_exising.groupby('adgroup_id')['keyword_name'].apply(list).reset_index()
df_ads_data = df_ads_data.merge(df_exising[['adgroup_id','keyword_name']],on='adgroup_id',how='left')
df_ads_data = df_ads_data.dropna(subset=['keyword_name'])

df_ads_data.to_csv(save_path+'/df_ads.csv',index=False)

df_ads_data['path1'].fillna("",inplace=True)
df_ads_data['path2'].fillna("",inplace=True)

if len(df_ads_data) != 0:
    answer = input("Do you want to add the ads in the file df_ads.csv (y/n) ?")
    if answer in ['y','Y']:
        for i,row in df_ads_data.iterrows():
            adgroup_id = row['adgroup_id']
            headlines = row['headline_keywords']
            descriptions = row['ad_description']
            final_url = row['final_url'][0]
            path1 = row['path1']
            path2 = row['path2']
            existing_keywords = row['keyword_name']
            
            headlines = list(set(headlines+existing_keywords))
            headlines = [x for x in headlines if len(x) <= 30][:15]
            descriptions = descriptions[:3]

            if len(headlines) != 0 and len(descriptions) != 0:
                create_ad(client,customer_id,adgroup_id,final_url,headlines,descriptions,path1,path2)
            else:
                print("Missing headlines or descriptions")
else:
    print("No ads to add")
