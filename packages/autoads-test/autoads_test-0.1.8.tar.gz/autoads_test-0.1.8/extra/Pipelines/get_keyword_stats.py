import pandas as pd
import datetime


from google.ads.googleads.client import GoogleAdsClient


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


def main(client, customer_id, start_date = '2020-09-01', end_date = '2022-02-25'):
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
    df.to_csv('fin_metrics.csv', index=False)
            


if __name__ == "__main__":
    # path = 'M:/GAds/google-ads_something.yaml'
    # customer_id = '6554081276'
    path = 'M:/GAds/hubspot_andrew/google-ads.yaml'
    customer_id = '8306215642'
    googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")
    
    main(googleads_client, customer_id)
