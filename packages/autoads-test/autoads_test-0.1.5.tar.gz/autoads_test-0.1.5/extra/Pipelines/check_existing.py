# cleaning is required.
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

path = 'M:/GAds/google-ads_something.yaml'
customer_id = '6554081276'
threshold = 0.9

status = [
    'ENABLED',
    'PAUSED',
    'REMOVED',
    'UNKNOWN',
    'UNSPECIFIED']

keyword_type = [
    'BROAD',
    'EXACT',
    'PHRASE',
    'UNKNOWN',
    'UNSPECIFIED'
]

_DEFAULT_PAGE_SIZE = 1000

googleads_client = GoogleAdsClient.load_from_storage(
    path=path, version="v9")


def get_keywords(ad_group_id=None):
    ga_service = googleads_client.get_service("GoogleAdsService")

    query = """
        SELECT
          ad_group.id,
          ad_group_criterion.type,
          ad_group_criterion.status,
          ad_group_criterion.criterion_id,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD"""

    if ad_group_id:
        query += f" AND ad_group.id = {ad_group_id}"

    search_request = googleads_client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    search_request.page_size = _DEFAULT_PAGE_SIZE

    results = ga_service.search(request=search_request)
    return results


def get_adgroups(campaign_id=None):
    ga_service = googleads_client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          ad_group.id,
          ad_group.status,
          ad_group.name
        FROM ad_group"""

    if campaign_id:
        query += f" WHERE campaign.id = {campaign_id}"

    search_request = googleads_client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    search_request.page_size = _DEFAULT_PAGE_SIZE

    results = ga_service.search(request=search_request)
    return results


def get_existing():
    camps = {
        'camp_name': list(),
        'camp_id': list(),
        'camp_status': list(),
        'adgroup_name': list(),
        'adgroup_status': list(),
        'adgroup_id': list(),
        'keyword_name': list(),
        'keyword_type': list(),
        'keyword_id' : list()
    }
    ga_service = googleads_client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          campaign.status,
          campaign.name
        FROM campaign
        WHERE campaign.status IN ('PAUSED', 'ENABLED')
        """
        # ORDER BY campaign.id

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in stream:
        for camp_row in batch.results:
            print(
                f"Campaign with ID {camp_row.campaign.id} and name "
                f'"{camp_row.campaign.name}" was found.'
            )
            ad_groups = get_adgroups(camp_row.campaign.id)
            for grp_row in ad_groups:
                print(
                    f"Ad group with ID {grp_row.ad_group.id} and name "
                    f'"{grp_row.ad_group.name}" was found in campaign with '
                    f"ID {grp_row.campaign.id}.")

                keywords = get_keywords(grp_row.ad_group.id)
                for row in keywords:
                    ad_group = row.ad_group
                    ad_group_criterion = row.ad_group_criterion
                    keyword = row.ad_group_criterion.keyword
                    print(
                        f'Keyword with text "{keyword.text}", match type '
                        f"{keyword.match_type}, criteria type "
                        f"{ad_group_criterion.type_}, and ID "
                        f"{ad_group_criterion.criterion_id} was found in ad group "
                        f"with ID {ad_group.id}.")
                    camps['camp_name'].append(camp_row.campaign.name)
                    camps['camp_id'].append(camp_row.campaign.id)
                    camps['camp_status'].append(camp_row.campaign.status.name)
                    camps['adgroup_name'].append(grp_row.ad_group.name)
                    camps['adgroup_id'].append(grp_row.ad_group.id)
                    camps['adgroup_status'].append(grp_row.ad_group.status.name)
                    camps['keyword_name'].append(keyword.text)
                    camps['keyword_type'].append(keyword.match_type.name)
                    camps['keyword_id'].append(row.ad_group_criterion.criterion_id)
        df = pd.DataFrame.from_dict(camps)
        df.to_csv('existing.csv', index=False)


if __name__ == '__main__':
    get_existing()
