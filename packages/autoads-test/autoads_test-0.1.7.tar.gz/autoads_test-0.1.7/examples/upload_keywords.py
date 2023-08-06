import os
import uuid
import pandas as pd
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from autoads.gads import create_adgroup,create_campaign,create_keyword,_handle_googleads_exception

df_path = 'data/keywords_to_upload.csv' # specify keywords to uplod csv here
save_path = 'data'
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id

os.makedirs(save_path,exist_ok=True)
os.makedirs(save_path+'/history',exist_ok=True)
googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df = pd.read_csv(df_path)
df = df.drop_duplicates("Keywords")
df_expand = df[~df['camp_id'].isna()].reset_index(drop=True)
df_create = df[df['camp_id'].isna()].reset_index(drop=True)

info_dict = {
        'campaign_id': list(),
        'adgroup_id': list(),
        'keyword_id': list(),
        'keyword_id2': list(),
        'type':list(),
}

if len(df_expand) != 0:
    #code for expanding existing campaign
    print("Adding to existing campaign")
    try:
        for i, row in df_expand.iterrows():
            keyword = row['Keywords']
            campaign_id = str(int(row['camp_id']))
            ad_group = create_adgroup(googleads_client,customer_id,campaign_id, adgroupName=keyword)
            if ad_group is None:
                continue
            ad_group_id = ad_group.split('/')[-1]
            keyword_id1 = create_keyword(
                googleads_client,customer_id,
                ad_group_id, keyword, kw_type='PHRASE')
            keyword_id1 = keyword_id1.split('/')[-1]
            keyword_id2 = create_keyword(
                googleads_client,customer_id,
                ad_group_id, keyword, kw_type='EXACT')
            keyword_id2 = keyword_id2.split('/')[-1]
            info_dict['campaign_id'].append(campaign_id)
            info_dict['adgroup_id'].append(ad_group_id)
            info_dict['keyword_id'].append(keyword_id1)
            info_dict['keyword_id2'].append(keyword_id2)
            info_dict['type'].append('expanded')
        print(f"{df_expand.shape[0]} campaigns expanded")
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)
else:
    print("No keywords to add into existing campaigns")

# code for ceating new campaign
if len(df_create) != 0:
    try:
        print("Creating new Campaigns")
        seed_keywords = df_create.groupby(['Keywords2']).groups  
        for k, d in seed_keywords.items():
            campaign = create_campaign(googleads_client,customer_id,campaignName=k,
                                        budgetName=k+'_budget_'+f"{uuid.uuid4()}", budgetDollars=100)
            campaign_id = campaign.split('/')[-1]
            data = df_create.iloc[d]['Keywords'].tolist()
            for keyword in data:
                ad_group = create_adgroup(googleads_client,customer_id,campaign_id, adgroupName=keyword)
                if ad_group is None:
                    continue
                ad_group_id = ad_group.split('/')[-1]
                keyword_id1 = create_keyword(
                    googleads_client,customer_id,
                    ad_group_id, keyword, kw_type='PHRASE')
                keyword_id1 = keyword_id1.split('/')[-1]
                keyword_id2 = create_keyword(
                    googleads_client,customer_id,
                    ad_group_id, keyword, kw_type='EXACT')
                keyword_id2 = keyword_id2.split('/')[-1]
                info_dict['campaign_id'].append(campaign_id)
                info_dict['adgroup_id'].append(ad_group_id)
                info_dict['keyword_id'].append(keyword_id1)
                info_dict['keyword_id2'].append(keyword_id2)
                info_dict['type'].append('created')
        print(f"{df_create.shape[0]} new campaigns created")
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)
else:
    print("No new campaigns to create")

info_df = pd.DataFrame.from_dict(info_dict)
df = pd.concat([df, info_df], axis=1)
df.to_csv(save_path+f'/history/{datetime.now().strftime("%m-%d-%Y %H-%M-%S")}.csv', index=False)
