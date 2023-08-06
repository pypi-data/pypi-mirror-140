from google.ads.googleads.client import GoogleAdsClient
from google.api_core import protobuf_helpers


def remove_adgroup(client, customer_id, ad_group_id):
    ad_group_service = client.get_service("AdGroupService")
    ad_group_operation = client.get_type("AdGroupOperation")

    resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)
    ad_group_operation.remove = resource_name

    ad_group_response = ad_group_service.mutate_ad_groups(
        customer_id=customer_id, operations=[ad_group_operation]
    )

    print(f"Removed ad group {ad_group_response.results[0].resource_name}.")


def remove_campaign(client, customer_id, campaign_id):
    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")

    resource_name = campaign_service.campaign_path(customer_id, campaign_id)
    campaign_operation.remove = resource_name

    campaign_response = campaign_service.mutate_campaigns(
        customer_id=customer_id, operations=[campaign_operation]
    )

    print(f"Removed campaign {campaign_response.results[0].resource_name}.")
    

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
    

def update_adgroup(client, customer_id, ad_group_id, **kwargs):
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
        

def update_campaign(client, customer_id, campaign_id, **kwargs):
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
        

def update_keyword(client, customer_id, ad_group_id, criterion_id, **kwargs):
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

if __name__ == '__main__':
    path = 'M:/GAds/google-ads_something.yaml'
    customer_id = '6554081276'
    googleads_client = GoogleAdsClient.load_from_storage(
    path=path, version="v9")
    update_keyword(googleads_client, customer_id, 134991344393,
                   517701729268, status='ENABLED', cpc_bid_micro_amount=1000000000)
