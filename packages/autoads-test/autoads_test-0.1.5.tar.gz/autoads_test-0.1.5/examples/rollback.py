import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from autoads.gads import remove_adgroup,remove_campaign

# from autoads.gads remove_campaign
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id

# latest csv file
rollback_csv = 'data/history/02-24-2022 02-24-29.csv'
googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df_rollback = pd.read_csv(rollback_csv)
df_rollback_create = df_rollback[df_rollback['type']=='created']
df_rollback_expand = df_rollback[df_rollback['type']=='expanded']

for i, row in df_rollback_expand.iterrows():
    adgroup_id = str(int(row['adgroup_id']))
    remove_adgroup(googleads_client,customer_id,adgroup_id)

for i, row in df_rollback_create.iterrows():
    campaign_id = str(int(row['campaign_id']))
    remove_campaign(googleads_client,customer_id,campaign_id)
