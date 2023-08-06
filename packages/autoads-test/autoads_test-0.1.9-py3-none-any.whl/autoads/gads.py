import argparse
import datetime
import sys
import uuid

import pandas as pd
from google.api_core import protobuf_helpers
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

_DATE_FORMAT = "%Y%m%d"

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


def get_keywords(googleads_client,customer_id,ad_group_id=None):
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


def get_adgroups(googleads_client,customer_id,campaign_id=None):
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


def get_existing(googleads_client,customer_id):
    camps = {
        'camp_name': list(),
        'camp_id': list(),
        'camp_status': list(),
        'adgroup_name': list(),
        'adgroup_status': list(),
        'adgroup_id': list(),
        'keyword_name': list(),
        'keyword_type': list(),
    }
    ga_service = googleads_client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          campaign.status,
          campaign.name
        FROM campaign
        WHERE
            campaign.status IN ('ENABLED', 'PAUSED') 
        ORDER BY campaign.id"""

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in stream:
        for camp_row in batch.results:
            print(
                f"Campaign with ID {camp_row.campaign.id} and name "
                f'"{camp_row.campaign.name}" was found.'
            )
            ad_groups = get_adgroups(googleads_client,customer_id,camp_row.campaign.id)
            for grp_row in ad_groups:
                print(
                    f"Ad group with ID {grp_row.ad_group.id} and name "
                    f'"{grp_row.ad_group.name}" was found in campaign with '
                    f"ID {grp_row.campaign.id}.")

                keywords = get_keywords(googleads_client,customer_id,grp_row.ad_group.id)
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
        df = pd.DataFrame.from_dict(camps)

        return df

def get_existing_keywords(googleads_client,customer_id):
    camps = {
        'camp_name': list(),
        'camp_id': list(),
        'camp_status': list(),
        'camp_experiment_type': list(),
        'adgroup_name': list(),
        'adgroup_status': list(),
        'adgroup_id': list(),
        'keyword_name': list(),
        'keyword_type': list(),
        'keyword_status': list(),
    }
    ga_service = googleads_client.get_service("GoogleAdsService")
    query = """
        SELECT
          ad_group.id,
          ad_group.name,
          ad_group.status,
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.experiment_type,
          ad_group_criterion.type,
          ad_group_criterion.status,
          ad_group_criterion.criterion_id,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type,
          ad_group_criterion.status
        FROM ad_group_criterion       
        WHERE ad_group_criterion.type = KEYWORD AND campaign.status IN ('ENABLED', 'PAUSED')"""

    search_request = googleads_client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    search_request.page_size = _DEFAULT_PAGE_SIZE

    results = ga_service.search(request=search_request)
    for row in results:
        ad_group = row.ad_group
        ad_group_criterion = row.ad_group_criterion
        keyword = row.ad_group_criterion.keyword
        print(
            f'Keyword with text "{keyword.text}", match type '
            f"{keyword.match_type}, criteria type "
            f"{ad_group_criterion.type_}, and ID "
            f"{ad_group_criterion.criterion_id} was found in ad group "
            f"with ID {ad_group.id}.")
        camps['camp_name'].append(row.campaign.name)
        camps['camp_id'].append(row.campaign.id)
        camps['camp_status'].append(row.campaign.status.name)
        camps['camp_experiment_type'].append(row.campaign.experiment_type.name)
        camps['adgroup_name'].append(row.ad_group.name)
        camps['adgroup_id'].append(row.ad_group.id)
        camps['adgroup_status'].append(row.ad_group.status.name)
        camps['keyword_name'].append(keyword.text)
        camps['keyword_type'].append(keyword.match_type.name)
        camps['keyword_status'].append(ad_group_criterion.status.name)
    df = pd.DataFrame(camps)
    return df

def create_keyword(googleads_client,customer_id,ad_group_id, keyword_text, kw_type,negative=False):
    ad_group_service = googleads_client.get_service("AdGroupService")
    ad_group_criterion_service = googleads_client.get_service(
        "AdGroupCriterionService")

    # Create keyword.
    ad_group_criterion_operation = googleads_client.get_type(
        "AdGroupCriterionOperation")
    ad_group_criterion = ad_group_criterion_operation.create
    ad_group_criterion.ad_group = ad_group_service.ad_group_path(
        customer_id, ad_group_id
    )
    ad_group_criterion.status = googleads_client.enums.AdGroupCriterionStatusEnum.ENABLED
    ad_group_criterion.keyword.text = keyword_text
    if kw_type == 'PHRASE':
        kw_type = googleads_client.enums.KeywordMatchTypeEnum.PHRASE
    elif kw_type == 'BROAD':
        kw_type = googleads_client.enums.KeywordMatchTypeEnum.BROAD
    else:
        kw_type = googleads_client.enums.KeywordMatchTypeEnum.EXACT
    ad_group_criterion.keyword.match_type = (
        kw_type
    )
    ad_group_criterion.negative = negative

    # Optional field
    # All fields can be referenced from the protos directly.
    # The protos are located in subdirectories under:
    # https://github.com/googleapis/googleapis/tree/master/google/ads/googleads
    # ad_group_criterion.negative = True

    # Optional repeated field
    # ad_group_criterion.final_urls.append('https://www.example.com')

    # Add keyword
    try:
        ad_group_criterion_response = (
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id,
                operations=[ad_group_criterion_operation],
            )
        )

        print(
            "Created keyword "
            f"{ad_group_criterion_response.results[0].resource_name}."
        )
        return ad_group_criterion_response.results[0].resource_name
    except:
        pass


def create_adgroup(googleads_client,customer_id,campaign_id, adgroupName, cpc_bid=10000000):
    ad_group_service = googleads_client.get_service("AdGroupService")
    campaign_service = googleads_client.get_service("CampaignService")

    # Create ad group.
    ad_group_operation = googleads_client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = adgroupName
    ad_group.status = googleads_client.enums.AdGroupStatusEnum.ENABLED
    ad_group.campaign = campaign_service.campaign_path(
        customer_id, campaign_id)
    ad_group.type_ = googleads_client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = cpc_bid

    try:
        # Add the ad group.
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        print(f"Created ad group {ad_group_response.results[0].resource_name}.")
        return ad_group_response.results[0].resource_name
    
    except:
        pass

def create_campaign(googleads_client,customer_id,campaignName, budgetName, budgetDollars):
    campaign_budget_service = googleads_client.get_service(
        "CampaignBudgetService")
    campaign_service = googleads_client.get_service("CampaignService")

    # Create a budget, which can be shared by multiple campaigns.
    campaign_budget_operation = googleads_client.get_type(
        "CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = budgetName
    campaign_budget.delivery_method = (
        googleads_client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    campaign_budget.amount_micros = int(budgetDollars * 1000000)
    campaign_budget.explicitly_shared = False

    # Add budget.
    try:
        campaign_budget_response = (
            campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[campaign_budget_operation]
            )
        )
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)

    # Create campaign.
    campaign_operation = googleads_client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaignName
    campaign.advertising_channel_type = (
        googleads_client.enums.AdvertisingChannelTypeEnum.SEARCH
    )

    # Recommendation: Set the campaign to PAUSED when creating it to prevent
    # the ads from immediately serving. Set to ENABLED once you've added
    # targeting and the ads are ready to serve.
    campaign.status = googleads_client.enums.CampaignStatusEnum.PAUSED

    # Set the bidding strategy and budget.
    campaign.manual_cpc.enhanced_cpc_enabled = True
    campaign.campaign_budget = campaign_budget_response.results[0].resource_name

    # Set the campaign network options.
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False

    # Optional: Set the start date.
    start_time = datetime.date.today() + datetime.timedelta(days=1)
    campaign.start_date = datetime.date.strftime(start_time, _DATE_FORMAT)

    # Optional: Set the end date.
    end_time = start_time + datetime.timedelta(weeks=4)
    campaign.end_date = datetime.date.strftime(end_time, _DATE_FORMAT)

    # Add the campaign.
    try:
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        print(
            f"Created campaign {campaign_response.results[0].resource_name}.")
        return campaign_response.results[0].resource_name
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)

def add_negative_keywords(client,customer_id,shared_set_id,keywords,kw_type):
    shared_set_service = client.get_service("SharedSetService")
    shared_criterion_service = client.get_service("SharedCriterionService")

    shared_criterion_operations = list()

    for keyword in keywords:
        shared_criterion_operation = client.get_type("SharedCriterionOperation")
        shared_criterion = shared_criterion_operation.create
        shared_criterion.shared_set = shared_set_service.shared_set_path(customer_id, shared_set_id)
        shared_criterion.keyword.text = keyword
        if kw_type == 'PHRASE':
            kw_type = client.enums.KeywordMatchTypeEnum.PHRASE
        elif kw_type == 'BROAD':
            kw_type = client.enums.KeywordMatchTypeEnum.BROAD
        else:
            kw_type = client.enums.KeywordMatchTypeEnum.EXACT
        
        shared_criterion.keyword.match_type = kw_type

        shared_criterion_operations.append(shared_criterion_operation)

    try:
        shared_set_criterion_response = (
            shared_criterion_service.mutate_shared_criteria(
                customer_id=customer_id,
                operations=shared_criterion_operations,
            )
        )
        for response in shared_set_criterion_response.results:
            print(
                "Created Shared Set Criteria"
                f"{response.resource_name}."
                )

        return shared_set_criterion_response.results
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)

def get_all_shared_sets(client,customer_id):
    df_dict = {
        "shared_set_id": list(),
        "shared_set_name": list(),
    }
    query = """
    SELECT 
    shared_set.id, 
    shared_set.name 
    FROM shared_set 
    """

    ga_service = client.get_service("GoogleAdsService")
    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    stream = ga_service.search_stream(search_request)
    
    for batch in stream:
        for row in batch.results:
            df_dict['shared_set_id'].append(row.shared_set.id)
            df_dict['shared_set_name'].append(row.shared_set.name)
    
    df = pd.DataFrame(df_dict)
    return df

def get_shared_set_keywords(client,customer_id,shared_set_id):
    df_dict = {
        "shared_set_id": list(),
        "shared_criterion_id": list(),
        "shared_criterion_keyword_type": list(),
        "shared_criterion_keyword_text": list(),
    }

    query = f"""
    SELECT 
    shared_set.id,
    shared_criterion.criterion_id, 
    shared_criterion.keyword.match_type, 
    shared_criterion.keyword.text 
    FROM shared_criterion 
    WHERE shared_set.id = {shared_set_id} 
    """

    ga_service = client.get_service("GoogleAdsService")
    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    stream = ga_service.search_stream(search_request)
    
    for batch in stream:
        for row in batch.results:
            df_dict['shared_set_id'].append(row.shared_set.id)
            df_dict['shared_criterion_id'].append(row.shared_criterion.criterion_id)
            df_dict['shared_criterion_keyword_text'].append(row.shared_criterion.keyword.text)
            df_dict['shared_criterion_keyword_type'].append(row.shared_criterion.keyword.match_type.name)
    
    df = pd.DataFrame(df_dict)
    return df

def get_all_ads(client,customer_id):
    query = """
    SELECT
    ad_group.id,
    campaign.id,
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
        'campaign_id': list(),
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
            campaign = row.campaign

            for headline in adgroup_ad.ad.responsive_search_ad.headlines:
                temp.append(headline.text)
            for descriptions in adgroup_ad.ad.responsive_search_ad.descriptions:
                temp2.append(descriptions.text)
            for final_url in adgroup_ad.ad.final_urls:
                temp3.append(final_url)

            df_dict['adgroup_id'].append(adgroup.id)
            df_dict['campaign_id'].append(campaign.id)
            df_dict['adgroup_ad_id'].append(adgroup_ad.ad.id)
            df_dict['headline_keywords'].append(temp)
            df_dict['ad_description'].append(temp2)
            df_dict['final_url'].append(temp3)
            df_dict['path1'].append(adgroup_ad.ad.responsive_search_ad.path1)
            df_dict['path2'].append(adgroup_ad.ad.responsive_search_ad.path2)

    df = pd.DataFrame.from_dict(df_dict)
    return df

def get_ads(client,customer_id,ad_group_id):
    query = f"""
    SELECT
    ad_group.id,
    campaign.id,
    ad_group_ad.ad.id,
    ad_group_ad.ad.responsive_search_ad.headlines,
    ad_group_ad.ad.responsive_search_ad.descriptions,
    ad_group_ad.ad.final_urls,
    ad_group_ad.ad.responsive_search_ad.path1,
    ad_group_ad.ad.responsive_search_ad.path2,
    ad_group_ad.status
    FROM ad_group_ad
    WHERE ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD AND ad_group.id == {ad_group_id}
    """

    df_dict = {
        'adgroup_id': list(),
        'campaign_id': list(),
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
            campaign = row.campaign

            for headline in adgroup_ad.ad.responsive_search_ad.headlines:
                temp.append(headline.text)
            for descriptions in adgroup_ad.ad.responsive_search_ad.descriptions:
                temp2.append(descriptions.text)
            for final_url in adgroup_ad.ad.final_urls:
                temp3.append(final_url)

            df_dict['adgroup_id'].append(adgroup.id)
            df_dict['campaign_id'].append(campaign.id)
            df_dict['adgroup_ad_id'].append(adgroup_ad.ad.id)
            df_dict['headline_keywords'].append(temp)
            df_dict['ad_description'].append(temp2)
            df_dict['final_url'].append(temp3)
            df_dict['path1'].append(adgroup_ad.ad.responsive_search_ad.path1)
            df_dict['path2'].append(adgroup_ad.ad.responsive_search_ad.path2)

    df = pd.DataFrame.from_dict(df_dict)
    return df

def create_ad(client, customer_id, ad_group_id, final_url, headlines, descriptions, path1, path2):

    def _create_ad_text_asset(client, text, pinned_field=None):
        """Create an AdTextAsset."""
        ad_text_asset = client.get_type("AdTextAsset")
        ad_text_asset.text = text
        if pinned_field:
            ad_text_asset.pinned_field = pinned_field
        return ad_text_asset
    
    
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
    heads = [_create_ad_text_asset(client, headline) for headline in headlines]
    print(heads)

    ad_group_ad.ad.responsive_search_ad.headlines.extend(
        heads
    )
    descs = [_create_ad_text_asset(client, headline) for headline in descriptions]
    ad_group_ad.ad.responsive_search_ad.descriptions.extend(
        descs
    )
    print(descs)
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
    
def update_adgroup(client,customer_id, ad_group_id, **kwargs):
    if len(kwargs) > 0:
        ad_group_service = client.get_service("AdGroupService")

        # Create ad group operation.
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.update
        ad_group.resource_name = ad_group_service.ad_group_path(
            customer_id, ad_group_id
        )
        if 'status' in kwargs:
            stat = kwargs['status']
            if stat == 'PAUSED':
                ad_group.status = client.enums.AdGroupStatusEnum.PAUSED
            elif stat == 'ENABLED':
                ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
            elif stat == 'UNSPECIFIED':
                ad_group.status = client.enums.AdGroupStatusEnum.UNSPECIFIED
        if 'cpc_bid_micro_amount' in kwargs:
            ad_group.cpc_bid_micros = kwargs['cpc_bid_micro_amount']
        client.copy_from(
            ad_group_operation.update_mask,
            protobuf_helpers.field_mask(None, ad_group._pb),
        )
        # Update the ad group.
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )

        print(f"Updated ad group {ad_group_response.results[0].resource_name}.")
    else:
        print('nothing to update')
        

def update_campaign(client,customer_id, campaign_id, **kwargs):
    if len(kwargs) > 0:
        campaign_service = client.get_service("CampaignService")

        # Create ad group operation.
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(
            customer_id, campaign_id
        )
        if 'status' in kwargs:
            stat = kwargs['status']
            if stat == 'PAUSED':
                campaign.status = client.enums.CampaignStatusEnum.PAUSED
            elif stat == 'ENABLED':
                campaign.status = client.enums.CampaignStatusEnum.ENABLED
            elif stat == 'UNSPECIFIED':
                campaign.status = client.enums.CampaignStatusEnum.UNSPECIFIED
        if 'cpc_bid_micro_amount' in kwargs:
            campaign.cpc_bid_micros = kwargs['cpc_bid_micro_amount']
        client.copy_from(
            campaign_operation.update_mask,
            protobuf_helpers.field_mask(None, campaign._pb),
        )
        # Update the ad group.
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )

        print(
            f"Updated campaign {campaign_response.results[0].resource_name}.")
    else:
        print('nothing to update')
        

def update_keyword(client,customer_id, ad_group_id, criterion_id, **kwargs):
    if len(kwargs) > 0:
        agc_service = client.get_service("AdGroupCriterionService")
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")

        ad_group_criterion = ad_group_criterion_operation.update
        ad_group_criterion.resource_name = agc_service.ad_group_criterion_path(
            customer_id, ad_group_id, criterion_id
        )
        if 'status' in kwargs:
            stat = kwargs['status']
            if stat == 'PAUSED':
                ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            elif stat == 'ENABLED':
                ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            elif stat == 'UNSPECIFIED':
                ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.UNSPECIFIED
        if 'cpc_bid_micro_amount' in kwargs:
            ad_group_criterion.cpc_bid_micros = kwargs['cpc_bid_micro_amount']
        # ad_group_criterion.final_urls.append("https://www.example.com")
        client.copy_from(
            ad_group_criterion_operation.update_mask,
            protobuf_helpers.field_mask(None, ad_group_criterion._pb),
        )

        agc_response = agc_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[ad_group_criterion_operation]
        )
        print(f"Updated keyword {agc_response.results[0].resource_name}.")
    else:
        print('nothing to update')


def remove_campaign(client, customer_id, campaign_id):
    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")

    resource_name = campaign_service.campaign_path(customer_id, campaign_id)
    campaign_operation.remove = resource_name

    campaign_response = campaign_service.mutate_campaigns(
        customer_id=customer_id, operations=[campaign_operation]
    )

    print(f"Removed campaign {campaign_response.results[0].resource_name}.")


def remove_adgroup(client, customer_id, ad_group_id):
    ad_group_service = client.get_service("AdGroupService")
    ad_group_operation = client.get_type("AdGroupOperation")

    resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)
    ad_group_operation.remove = resource_name

    ad_group_response = ad_group_service.mutate_ad_groups(
        customer_id=customer_id, operations=[ad_group_operation]
    )

    print(f"Removed ad group {ad_group_response.results[0].resource_name}.")

def remove_keyword(client, customer_id, ad_group_id, criterion_id):
    agc_service = client.get_service("AdGroupCriterionService")
    agc_operation = client.get_type("AdGroupCriterionOperation")

    resource_name = agc_service.ad_group_criterion_path(
        customer_id, ad_group_id, criterion_id
    )
    agc_operation.remove = resource_name

    agc_response = agc_service.mutate_ad_group_criteria(
        customer_id=customer_id, operations=[agc_operation]
    )

    print(f"Removed keyword {agc_response.results[0].resource_name}.")


def get_search_term_report(client, customer_id,start_date='2022-01-01', end_date='2022-01-10'):
    df_dict = {
    'date' : list(),
    'stv_resource_name' : list(),
    'stv_status' : list(),
    'stv_search_term' : list(),
    'stv_adgroup': list(),
    'adgroupad_resource_name' : list(),
    'adgroupad_ad_resource_name' : list(),
    'adgroupad_ad_id' : list(),
    'adgroup_resource_name' : list(),
    'adgroup_id': list(),
    'adgroup_status': list(),
    'adgroup_camp': list(),
    'campaign_id': list(),
    'campaign_status': list(),
    'metrics_clicks': list(),
    'metrics_conversion_value' : list(),
    'metrics_conversions' : list(),
    'metrics_cost': list(),
    'metrics_cpc': list(),
    'metrics_ctr': list(),
    'metrics_engagements': list(),
    'metrics_all_conversions': list(),
    'metrics_avg_cost': list(),
    'metrics_avg_cpc': list(),
    'metrics_impressions': list(),
    'metrics_interactions' : list(),
    }
    
    ga_service = client.get_service("GoogleAdsService")
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    step = datetime.timedelta(days=1)
    while start <= end:
        query1 = """
        SELECT 
            search_term_view.ad_group, 
            search_term_view.resource_name, 
            search_term_view.search_term, 
            search_term_view.status, 
            ad_group_ad.ad.name, 
            ad_group_ad.ad.id, 
            metrics.average_cost, 
            metrics.average_cpc, 
            metrics.clicks, 
            metrics.conversions, 
            metrics.average_cpv, 
            metrics.conversions_value, 
            metrics.cost_micros, 
            metrics.cost_per_conversion, 
            metrics.ctr, 
            metrics.engagements, 
            metrics.impressions, 
            metrics.interactions, 
            metrics.all_conversions, 
            ad_group.id, 
            ad_group.status,
            ad_group.campaign,
            campaign.id,
            campaign.status
        FROM search_term_view
        WHERE campaign.status IN ('ENABLED','PAUSED') AND
        """
        query2 = f" segments.date >= '{str(start)[0:10]}' AND segments.date < '{str(start+step)[0:10]}'"
        query = query1 + '\n' + query2
        search_request = client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        stream = ga_service.search_stream(search_request)
        for batch in stream:
            for row in batch.results:
                adgroup = row.ad_group
                metrics = row.metrics
                adgroupad = row.ad_group_ad
                stv = row.search_term_view
                
                df_dict['date'].append(start)
                df_dict['stv_resource_name'].append(stv.resource_name)
                df_dict['stv_status'].append(stv.status.name)
                df_dict['stv_search_term'].append(stv.search_term)
                df_dict['stv_adgroup'].append(stv.ad_group)
                
                df_dict['adgroupad_resource_name'].append(adgroupad.resource_name)
                df_dict['adgroupad_ad_resource_name'].append(adgroupad.ad.resource_name)
                df_dict['adgroupad_ad_id'].append(adgroupad.ad.id)
                
                df_dict['adgroup_resource_name'].append(adgroup.resource_name)
                df_dict['adgroup_status'].append(adgroup.status.name)
                df_dict['adgroup_id'].append(adgroup.id)
                df_dict['adgroup_camp'].append(adgroup.campaign)

                df_dict['campaign_id'].append(row.campaign.id)
                df_dict['campaign_status'].append(row.campaign.status.name)
                
                df_dict['metrics_clicks'].append(metrics.clicks)
                df_dict['metrics_conversion_value'].append(metrics.conversions_value)
                df_dict['metrics_conversions'].append(metrics.conversions)
                df_dict['metrics_cost'].append(metrics.cost_micros)
                df_dict['metrics_cpc'].append(metrics.cost_per_conversion)
                df_dict['metrics_ctr'].append(metrics.ctr)
                df_dict['metrics_engagements'].append(metrics.engagements)
                df_dict['metrics_all_conversions'].append(metrics.all_conversions)
                df_dict['metrics_avg_cost'].append(metrics.average_cost)
                df_dict['metrics_avg_cpc'].append(metrics.average_cpc)
                df_dict['metrics_impressions'].append(metrics.impressions)
                df_dict['metrics_interactions'].append(metrics.interactions)
        start += step
    df = pd.DataFrame.from_dict(df_dict)
    return df

df_dict = {
    'date' : list(),
    'camp_id' : list(),
    'camp_name' : list(),
    'camp_status' : list(),
    'adgroup_id' : list(),
    'adgroup_name' : list(),
    'adgroup_status' : list(),
    'ad_group_criterion_resource_name' : list(),
    'adgroup_criterion_id' : list(),
    'ad_group_criterion_keyword_text' : list(),
    'ad_group_criterion_keyword_match_type' : list(),
    'adgroup_criterion_status' : list(),
    'metrics_impressions' : list(),
    'metrics_clicks' : list(),
    'metrics_cost' : list(),
    'metrics_cpc' : list(),
    'metrics_cost_per_conversion' : list(),
    'metrics_cost_per_all_conversions' : list(),
    'metrics_all_conversions_by_conversion_date' : list(),
    'metrics_all_conversions' : list(),
    }


def get_keyword_stats(client, customer_id, start_date = '2020-09-01', end_date = '2022-02-25'):
    ga_service = client.get_service("GoogleAdsService")
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    step = datetime.timedelta(days=1)
    while start <= end:
        query1 = """
            SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group_criterion.resource_name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.cost_per_conversion, 
            metrics.cost_per_all_conversions,
            metrics.all_conversions_by_conversion_date, 
            metrics.all_conversions"""
        query2 = f"FROM keyword_view WHERE segments.date >= '{str(start)[0:10]}' AND segments.date < '{str(start+step)[0:10]}'"
        query3 = """AND campaign.advertising_channel_type = 'SEARCH'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status IN ('ENABLED', 'PAUSED')
            ORDER BY metrics.impressions DESC
            """
        fin_query = query1 + '\n' + query2 + '\n' + query3
        
        search_request = client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = customer_id
        search_request.query = fin_query
        stream = ga_service.search_stream(search_request)
        for batch in stream:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                criterion = row.ad_group_criterion
                metrics = row.metrics
                df_dict['date'].append(start)
                df_dict['camp_id'].append(campaign.id)
                df_dict['camp_name'].append(campaign.name)
                df_dict['camp_status'].append(campaign.status.name)
                df_dict['adgroup_id'].append(ad_group.id)
                df_dict['adgroup_name'].append(ad_group.name)
                df_dict['adgroup_status'].append(ad_group.status.name)
                df_dict['ad_group_criterion_resource_name'].append(criterion.resource_name)
                df_dict['adgroup_criterion_id'].append(criterion.criterion_id)
                df_dict['ad_group_criterion_keyword_text'].append(criterion.keyword.text)
                df_dict['ad_group_criterion_keyword_match_type'].append(criterion.keyword.match_type.name)
                df_dict['adgroup_criterion_status'].append(criterion.status.name)
                df_dict['metrics_impressions'].append(metrics.impressions)
                df_dict['metrics_clicks'].append(metrics.clicks)
                df_dict['metrics_cost'].append(metrics.cost_micros)
                df_dict['metrics_cpc'].append(metrics.average_cpc)
                df_dict['metrics_cost_per_conversion'].append(metrics.cost_per_conversion)
                df_dict['metrics_cost_per_all_conversions'].append(metrics.cost_per_all_conversions)
                df_dict['metrics_all_conversions'].append(metrics.all_conversions)
                df_dict['metrics_all_conversions_by_conversion_date'].append(
                    metrics.all_conversions_by_conversion_date)
        start = start+step
    df = pd.DataFrame.from_dict(df_dict)
    return df

def _handle_googleads_exception(exception):
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
        continue
        sys.exit(1)
