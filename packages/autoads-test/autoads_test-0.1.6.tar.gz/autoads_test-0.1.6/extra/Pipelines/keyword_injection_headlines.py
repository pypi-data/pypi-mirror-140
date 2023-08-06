import pandas as pd
import datetime


from google.ads.googleads.client import GoogleAdsClient
path = 'M:/GAds/hubspot_andrew/google-ads.yaml'
customer_id = '8306215642'
# path = 'M:/GAds/google-ads_something.yaml'
# customer_id = '6554081276'
client = GoogleAdsClient.load_from_storage(
    path=path, version="v9")

query = """
SELECT
  ad_group.id,
  ad_group_ad.ad.id,
  ad_group_ad.ad.responsive_search_ad.headlines,
  ad_group_ad.ad.responsive_search_ad.descriptions,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.responsive_search_ad.path1,
  ad_group_ad.ad.responsive_search_ad.path2,
  ad_group_ad.status
FROM ad_group_ad
WHERE ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
"""

df_dict = {
    'adgroup_id': list(),
    'adgroup_ad_id': list(),
    'headline_keywords': list(),
    'ad_description': list(),
    'final_url': list(),
    'path1': list(),
    'path2': list()
}

ga_service = client.get_service("GoogleAdsService")
search_request = client.get_type("SearchGoogleAdsStreamRequest")
search_request.customer_id = customer_id
search_request.query = query
stream = ga_service.search_stream(search_request)
for batch in stream:
    for row in batch.results:
        temp = list()
        temp2 = list()
        temp3 = list()
        adgroup = row.ad_group
        adgroup_ad = row.ad_group_ad

        for headline in adgroup_ad.ad.responsive_search_ad.headlines:
            temp.append(headline.text)
        for descriptions in adgroup_ad.ad.responsive_search_ad.descriptions:
            temp2.append(descriptions.text)
        for final_url in adgroup_ad.ad.final_urls:
            temp3.append(final_url)

        df_dict['adgroup_id'].append(adgroup.id)
        df_dict['adgroup_ad_id'].append(adgroup_ad.ad.id)
        df_dict['headline_keywords'].append(temp)
        df_dict['ad_description'].append(temp2)
        df_dict['final_url'].append(temp3)
        df_dict['path1'].append(adgroup_ad.ad.responsive_search_ad.path1)
        df_dict['path2'].append(adgroup_ad.ad.responsive_search_ad.path2)

df = pd.DataFrame.from_dict(df_dict)

existing_dict = {}
dff = pd.read_csv('M:/GAds/existing_and.csv')
dff = dff[['adgroup_id', 'keyword_name']]
dff = dff.drop_duplicates(
    subset=['keyword_name', 'adgroup_id']).reset_index(drop=True)
existing_groups = dff.groupby(['adgroup_id'])
x = existing_groups.groups
for k, d in x.items():
    existing_dict[k] = (dff.iloc[d]['keyword_name'].values[0])

inject_dict = {}
dffx = df
dffx = dffx[['adgroup_id', 'headline_keywords']]
inject_groups = dffx.groupby(['adgroup_id'])
for k, d in inject_groups.groups.items():
    data = dffx.iloc[d]['headline_keywords'].values[0]
    inject_dict[k] = (data)

fin_inject = {}
for k, d in inject_dict.items():
    if existing_dict.get(k):
        if existing_dict.get(k) in d:
            continue
        else:
            fin_inject[k] = existing_dict.get(k)

fin_df = pd.DataFrame(
    {
        'adgroup_id': fin_inject.keys(),
        'inject_keywords': fin_inject.values()
    },
).reset_index(drop=True)

dffx = df
finn = pd.merge(left=dffx, right=fin_df, on='adgroup_id', how='left')
customer_id = '6554081276'
# finn.to_csv('finn_df.csv', index= False)


def create_ad(client, ad_group_id, final_url, headlines, descriptions, path1, path2):
    print(customer_id)
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_service = client.get_service("AdGroupService")

    # Create the ad group ad.
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad_group_ad.ad_group = ad_group_service.ad_group_path(
        customer_id, ad_group_id
    )

    # Set responsive search ad info.
    ad_group_ad.ad.final_urls.append(final_url)

    # Set a pinning to always choose this asset for HEADLINE_1. Pinning is
    # optional; if no pinning is set, then headlines and descriptions will be
    # rotated and the ones that perform best will be used more often.
    # served_asset_enum = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1

    ad_group_ad.ad.responsive_search_ad.headlines.extend(
        [_create_ad_text_asset(client, headline) for headline in headlines]
    )
    ad_group_ad.ad.responsive_search_ad.descriptions.extend(
        [_create_ad_text_asset(client, headline) for headline in descriptions]
    )
    ad_group_ad.ad.responsive_search_ad.path1 = path1
    ad_group_ad.ad.responsive_search_ad.path2 = path2

    # Send a request to the server to add a responsive search ad.
    ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[ad_group_ad_operation]
    )

    for result in ad_group_ad_response.results:
        print(
            f"Created responsive search ad with resource name "
            f'"{result.resource_name}".'
        )


def _create_ad_text_asset(client, text, pinned_field=None):
    """Create an AdTextAsset."""
    ad_text_asset = client.get_type("AdTextAsset")
    ad_text_asset.text = text
    if pinned_field:
        ad_text_asset.pinned_field = pinned_field
    return ad_text_asset


if __name__ == '__main__':
    path = 'M:/GAds/google-ads_something.yaml'
    client = GoogleAdsClient.load_from_storage(
        path=path, version="v9")
    df = finn
    df = df.dropna(subset=['inject_keywords'])
    for i, row in df.iterrows():
        if len(row.inject_keywords) <= 30:
            headlines = row.headline_keywords
            headlines.append(row.inject_keywords)
            if len(headlines) <= 15:
                descriptions = row.ad_description
                final_url = row.final_url
                create_ad(client, ad_group_id=128850628970,
                          final_url=final_url[0], headlines=headlines, descriptions=descriptions, path1=row.path1, path2=row.path2)