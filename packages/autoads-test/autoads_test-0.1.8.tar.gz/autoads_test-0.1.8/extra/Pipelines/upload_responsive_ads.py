import argparse
import sys
from uuid import uuid4
import pandas as pd

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

customer_id = '6554081276'


def create_ad(client, ad_group_id, final_url, headlines, descriptions, path1, path2):
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
    df = pd.read_csv('M:/GAds/finn_df.csv')
    df = df.dropna(subset=['inject_keywords'])
    for i, row in df.iterrows():
        if len(row.inject_keywords) < 30:
            # headlines = row.headline_keywords.replace(
            #     '[', '').replace(']', '').replace("'", '').split(',')
            # headlines = [v.strip() for v in headlines]
            headlines = row.headlines
            headlines.append(row.inject_keywords)
            if len(row.headlines) < 15:
                print(len(row.headlines))
                descriptions = row.ad_description
                # .replace('[', '').replace(']', '').replace("'", '').split(',')
                # descriptions = [v.strip() for v in descriptions]
                final_url = row.final_url
                # .replace('[', '').replace(']', '').replace("'", '').split(',')
                print(final_url[0])
                create_ad(client, ad_group_id=128850628970,
                        final_url=final_url[0], headlines=headlines, descriptions=descriptions, path1=row.path1, path2=row.path2)
