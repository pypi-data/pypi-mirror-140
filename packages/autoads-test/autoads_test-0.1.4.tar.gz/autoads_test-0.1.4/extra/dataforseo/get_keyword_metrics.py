import pandas as pd
from client import RestClient
client = RestClient("lzvwylzynyvizpztrj@nthrl.com", "34f2a32258a08c98")
df_path = 'M:/GAds/Google-Ads-Project/data/df_final.csv'
threshold = 0.9
match_extract = ['exact', 'phrase']  # exact, phrase, broad

keyword_metrics = {
    'Keywords': list(),
    'volume': list(),
    'competition': list(),
    'low_bid': list(),
    'high_bid': list()
}
cpc_metrics = {
    'Keywords' : list()
}
values = ['ctr', 'cpc', 'impressions', 'cost', 'clicks']
for match in match_extract:
    for v in values:
        cpc_metrics.update(
            {
                f'{v}_{match}': list()
            }
        )

def get_cpc(keywords_list, match = 'exact', bid = 999.0):
    post_data = dict()
    post_data[len(post_data)] = dict(
        location_name="United States",
        language_name="English",
        bid=bid,
        match=match,
        keywords=keywords_list
    )
    response = client.post(
        "/v3/keywords_data/google_ads/ad_traffic_by_keywords/live", post_data)
    if response["status_code"] == 20000:
        return (response)
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
    
def get_volume(keywords_list):
    post_data = dict()
    post_data[len(post_data)] = dict(
        location_code=2840,
        keywords=keywords_list,
        date_from="2021-08-01",
        search_partners=True
    )
    response = client.post(
        "/v3/keywords_data/google_ads/search_volume/live", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        return(response)
    else:
        print("error. Code: %d Message: %s" %
              (response["status_code"], response["status_message"]))


def extract_volume(response):
    results = response['tasks'][0]['result']
    if results != None:
        for res in results:
            keyword_metrics['Keywords'].append(res['keyword'])
            keyword_metrics['volume'].append(res['search_volume'])
            keyword_metrics['competition'].append(res['competition'])
            keyword_metrics['low_bid'].append(res['low_top_of_page_bid'])
            keyword_metrics['high_bid'].append(res['high_top_of_page_bid'])


def extract_cpc(response):
    results = response['tasks'][0]['result']
    if results != None:
        match = response['tasks'][0]['result'][0]['match']
        for res in results:
            if res['keyword'] not in cpc_metrics['Keywords']:
                cpc_metrics[f'Keywords'].append(res['keyword'])
            cpc_metrics[f'ctr_{match}'].append(res['ctr'])
            cpc_metrics[f'impressions_{match}'].append(res['impressions'])
            cpc_metrics[f'cpc_{match}'].append(res['average_cpc'])
            cpc_metrics[f'cost_{match}'].append(res['cost'])
            cpc_metrics[f'clicks_{match}'].append(res['clicks'])

df = pd.read_csv(df_path)
df = df[df['similarity'] >= threshold].reset_index(drop=True)
keywords_list = df['Keywords'].unique().tolist()
if len(keywords_list) > 1000:
    for i, x in enumerate(range(0, len(keywords_list), 1000)):
        volume = get_volume(keywords_list[i*1000: (i+1)*1000])
        extract_volume(volume)
        for c in match_extract:
            cpc = get_cpc(keywords_list[i*1000: (i+1)*1000], match=c)
            extract_cpc(cpc)   
else:
    volume = get_volume(keywords_list)
    extract_volume(volume)
    for c in match_extract:
        cpc = get_cpc(keywords_list, match=c)
        extract_cpc(cpc)

fin_df_1 = pd.DataFrame.from_dict(keyword_metrics)
fin_df_2 = pd.DataFrame.from_dict(cpc_metrics)
fin_df = pd.merge(left=fin_df_1, right=fin_df_2, how='left', on=['Keywords'])

df = pd.merge(left=df, right=fin_df, how='left', on=['Keywords'])
df.to_csv(f'{df_path}', index=False)
