import uuid
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from autoads.gads import create_adgroup, create_campaign, create_keyword, _handle_googleads_exception

df_path = 'M:/GAds/Google-Ads-Project/data/keywords_to_upload.csv'  # specify keywords to uplod csv here
save_path = 'M:/GAds/Google-Ads-Project/data'
path = 'M:/GAds/google-ads_something.yaml'
customer_id = '6554081276'

googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")

df = pd.read_csv(df_path)

info_dict = {
    'campaign_id': list(),
    'adgroup_id': list(),
    'keyword_id': list(),
    'keyword_id2': list()
}
try:
    seed_keywords = df.groupby(['Keywords2']).groups
    for k, d in seed_keywords.items():
        campaign = create_campaign(googleads_client, customer_id, campaignName=k,
                                   budgetName=k+'_budget_'+f"{uuid.uuid4()}", budgetDollars=100)
        campaign_id = campaign.split('/')[-1]
        data = df.iloc[d]['Keywords'].tolist()
        for keyword in data:
            ad_group = create_adgroup(
                googleads_client, customer_id, campaign_id, adgroupName=keyword)
            if ad_group is None:
                continue
            ad_group_id = ad_group.split('/')[-1]
            keyword_id1 = create_keyword(
                googleads_client, customer_id,
                ad_group_id, keyword, kw_type='PHRASE')
            keyword_id1 = keyword_id1.split('/')[-1]
            keyword_id2 = create_keyword(
                googleads_client, customer_id,
                ad_group_id, keyword, kw_type='EXACT')
            keyword_id2 = keyword_id2.split('/')[-1]
            info_dict['campaign_id'].append(campaign_id)
            info_dict['adgroup_id'].append(ad_group_id)
            info_dict['keyword_id'].append(keyword_id1)
            info_dict['keyword_id2'].append(keyword_id2)
    info_df = pd.DataFrame.from_dict(info_dict)
    df = pd.concat([df, info_df], axis=1)
    df.to_csv(save_path+'/info.csv', index=False)
except GoogleAdsException as ex:
    _handle_googleads_exception(ex)
