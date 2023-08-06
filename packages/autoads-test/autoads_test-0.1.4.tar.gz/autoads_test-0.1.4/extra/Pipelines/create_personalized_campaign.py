import argparse
import datetime
import sys
import uuid

import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

df_path = 'M:/Upwork/OpenMoves/OpenMoves/401k_sim_ext_downstream1.csv'
path = 'M:/GAds/google-ads_something.yaml'
customer_id = '6554081276'
threshold = 0.9

googleads_client = GoogleAdsClient.load_from_storage(
    path=path, version="v9")

_DATE_FORMAT = "%Y%m%d"


def create_keyword(ad_group_id, keyword_text, kw_type):
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


def create_adgroup(campaign_id, adgroupName, cpc_bid=10000000):
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

def create_campaign(campaignName, budgetName, budgetDollars):
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


def do_everything():
    info_dict = {
        'campaign_id': list(),
        'adgroup_id': list(),
        'keyword_id': list(),
        'keyword_id2': list()
    }
    try:
        df = pd.read_csv(df_path)
        df = df[df['similarity'] >= threshold].reset_index(drop=True)
        seed_keywords = df.groupby(['Keywords2']).groups
        for k, d in seed_keywords.items():
            campaign = create_campaign(campaignName=k,
                                       budgetName=k+'_budget_', budgetDollars=1000000)
            campaign_id = campaign.split('/')[-1]
            data = df.iloc[d]['Keywords'].tolist()
            for keyword in data:
                ad_group = create_adgroup(campaign_id, adgroupName=keyword)
                if ad_group is None:
                    continue
                ad_group_id = ad_group.split('/')[-1]
                keyword_id1 = create_keyword(
                    ad_group_id, keyword, kw_type='PHRASE')
                keyword_id1 = keyword_id1.split('/')[-1]
                keyword_id2 = create_keyword(
                    ad_group_id, keyword, kw_type='EXACT')
                keyword_id2 = keyword_id2.split('/')[-1]
                info_dict['campaign_id'].append(campaign_id)
                info_dict['adgroup_id'].append(ad_group_id)
                info_dict['keyword_id'].append(keyword_id1)
                info_dict['keyword_id2'].append(keyword_id2)
        info_df = pd.DataFrame.from_dict(info_dict)
        df = pd.concat([df, info_df], axis=1)
        df.to_csv('info_df.csv', index=False)
    except GoogleAdsException as ex:
        _handle_googleads_exception(ex)


if __name__ == '__main__':
    do_everything()
