import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from autoads.gads import remove_adgroup,remove_campaign,remove_keyword

# from autoads.gads remove_campaign
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id

# latest csv file
rollback_csv = 'data/history/03-01-2022 19-33-46.csv'
googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df_rollback = pd.read_csv(rollback_csv)
df_rollback_create = df_rollback[df_rollback['type']=='created']
df_rollback_expand = df_rollback[df_rollback['type']=='expanded']
df_rollback_negative = df_rollback[df_rollback['type']=='negative']

for i,row in df_rollback_negative.iterrows():
    keyword_id1 = str(int(row['keyword_id']))
    keyword_id2 = str(int(row['keyword_id2']))
    adgroup_id = str(int(row['adgroup_id']))
    remove_keyword(googleads_client,customer_id,adgroup_id,keyword_id1)
    remove_keyword(googleads_client,customer_id,adgroup_id,keyword_id2)

for i, row in df_rollback_expand.iterrows():
    adgroup_id = str(int(row['adgroup_id']))
    remove_adgroup(googleads_client,customer_id,adgroup_id)

for i, row in df_rollback_create.iterrows():
    campaign_id = str(int(row['campaign_id']))
    remove_campaign(googleads_client,customer_id,campaign_id)
