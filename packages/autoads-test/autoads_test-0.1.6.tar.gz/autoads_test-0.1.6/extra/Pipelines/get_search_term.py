import pandas as pd
import datetime


from google.ads.googleads.client import GoogleAdsClient

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


def main(client, customer_id, start_date='2022-01-01', end_date='2022-01-10'):
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
            ad_group.campaign
        FROM search_term_view
        """
        query2 = f"WHERE segments.date >= '{str(start)[0:10]}' AND segments.date < '{str(start+step)[0:10]}'"
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
    df.to_csv(f'search_term_dfx.csv', index=False)

if __name__ == "__main__":
    # path = 'M:/GAds/google-ads_something.yaml'
    # customer_id = '6554081276'
    path = 'M:/GAds/hubspot_andrew/google-ads.yaml'
    customer_id = '8306215642'
    googleads_client = GoogleAdsClient.load_from_storage(
        path=path, version="v9")

    main(googleads_client, customer_id)
