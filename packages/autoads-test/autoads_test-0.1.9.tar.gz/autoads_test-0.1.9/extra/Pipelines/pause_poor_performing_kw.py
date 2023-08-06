import pandas as pd
import datetime
from modify_everything import update_keyword


from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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
        
df_dict = {
    'date': list(),
    'camp_id': list(),
    'camp_name': list(),
    'camp_status': list(),
    'adgroup_id': list(),
    'adgroup_name': list(),
    'adgroup_status': list(),
    'ad_group_criterion_resource_name': list(),
    'adgroup_criterion_id': list(),
    'ad_group_criterion_keyword_text': list(),
    'ad_group_criterion_keyword_match_type': list(),
    'adgroup_criterion_status': list(),
    'metrics_impressions': list(),
    'metrics_clicks': list(),
    'metrics_cost': list(),
    'metrics_cpc': list(),
    'metrics_cost_per_conversion': list(),
    'metrics_cost_per_all_conversions': list(),
    'metrics_all_conversions_by_conversion_date': list(),
    'metrics_all_conversions': list(),
}

df_dict2 = {
    'date': list(),
    'stv_resource_name': list(),
    'stv_status': list(),
    'stv_search_term': list(),
    'stv_adgroup': list(),
    'adgroupad_resource_name': list(),
    'adgroupad_ad_resource_name': list(),
    'adgroupad_ad_id': list(),
    'adgroup_resource_name': list(),
    'adgroupad_status' : list(),
    'adgroup_id': list(),
    'adgroup_status': list(),
    'adgroup_camp': list(),
    'metrics_clicks': list(),
    'metrics_conversion_value': list(),
    'metrics_conversions': list(),
    'metrics_cost': list(),
    'metrics_cpa': list(),
    'metrics_ctr': list(),
    'metrics_engagements': list(),
    'metrics_all_conversions': list(),
    'metrics_avg_cost': list(),
    'metrics_avg_cpc': list(),
    'metrics_impressions': list(),
    'metrics_interactions': list(),

}


def search_term_report(client, customer_id, start_date='2021-12-01', end_date='2022-01-20'):
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
            ad_group_ad.status,
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

                df_dict2['date'].append(start)
                df_dict2['stv_resource_name'].append(stv.resource_name)
                df_dict2['stv_status'].append(stv.status.name)
                df_dict2['stv_search_term'].append(stv.search_term)
                df_dict2['stv_adgroup'].append(stv.ad_group)

                df_dict2['adgroupad_resource_name'].append(
                    adgroupad.resource_name)
                df_dict2['adgroupad_ad_resource_name'].append(
                    adgroupad.ad.resource_name)
                df_dict2['adgroupad_ad_id'].append(adgroupad.ad.id)
                df_dict2['adgroupad_status'].append(adgroupad.status.name)

                df_dict2['adgroup_resource_name'].append(adgroup.resource_name)
                df_dict2['adgroup_status'].append(adgroup.status.name)
                df_dict2['adgroup_id'].append(adgroup.id)
                df_dict2['adgroup_camp'].append(adgroup.campaign)

                df_dict2['metrics_clicks'].append(metrics.clicks)
                df_dict2['metrics_conversion_value'].append(
                    metrics.conversions_value)
                df_dict2['metrics_conversions'].append(metrics.conversions)
                df_dict2['metrics_cost'].append(metrics.cost_micros)
                df_dict2['metrics_cpa'].append(metrics.cost_per_conversion)
                df_dict2['metrics_ctr'].append(metrics.ctr)
                df_dict2['metrics_engagements'].append(metrics.engagements)
                df_dict2['metrics_all_conversions'].append(
                    metrics.all_conversions)
                df_dict2['metrics_avg_cost'].append(metrics.average_cost)
                df_dict2['metrics_avg_cpc'].append(metrics.average_cpc)
                df_dict2['metrics_impressions'].append(metrics.impressions)
                df_dict2['metrics_interactions'].append(metrics.interactions)
        start += step
    df = pd.DataFrame.from_dict(df_dict2)
    return df


def main(client, customer_id, start_date='2021-12-01', end_date='2022-02-27'):
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
                df_dict['ad_group_criterion_resource_name'].append(
                    criterion.resource_name)
                df_dict['adgroup_criterion_id'].append(criterion.criterion_id)
                df_dict['ad_group_criterion_keyword_text'].append(
                    criterion.keyword.text)
                df_dict['ad_group_criterion_keyword_match_type'].append(
                    criterion.keyword.match_type.name)
                df_dict['adgroup_criterion_status'].append(
                    criterion.status.name)
                df_dict['metrics_impressions'].append(metrics.impressions)
                df_dict['metrics_clicks'].append(metrics.clicks)
                df_dict['metrics_cost'].append(metrics.cost_micros)
                df_dict['metrics_cpc'].append(metrics.average_cpc)
                df_dict['metrics_cost_per_conversion'].append(
                    metrics.cost_per_conversion)
                df_dict['metrics_cost_per_all_conversions'].append(
                    metrics.cost_per_all_conversions)
                df_dict['metrics_all_conversions'].append(
                    metrics.all_conversions)
                df_dict['metrics_all_conversions_by_conversion_date'].append(
                    metrics.all_conversions_by_conversion_date)
        start = start+step
    df = pd.DataFrame.from_dict(df_dict)
    return df


if __name__ == "__main__":
    # path = 'M:/GAds/google-ads_something.yaml'
    # customer_id = '6554081276'
    path = 'M:/GAds/hubspot_andrew/google-ads.yaml'
    customer_id = '8306215642'
    googleads_client = GoogleAdsClient.load_from_storage(
        path=path, version="v9")
    
    aors = -1
    while aors < 1 or aors > 2:
        aors = int(input('Select 1 for adgroups or 2 for search term view : '))
    
    start_date = (input('Enter start_date : (YYYY-MM-DD) : ')).strip()
    end_date = (input('Enter start_date : (YYYY-MM-DD) : ')).strip()
    
    save = input('save full df? y or Y for yes : ')
        
    if aors == 1:
        print('Extracting info from adgroups')
        df = main(
            googleads_client, customer_id, start_date=start_date, end_date=end_date)
        filename = 'adgroups'
        
        
    elif aors == 2:
        print('Extracting info from Search term report')
        df = search_term_report(
            googleads_client, customer_id, start_date=start_date, end_date=end_date)
        filename = 'search_term'
        
    # start_date = df['date'].values[0]
    # end_date = df['date'].values[-1]
    
    if save == 'y' or save == 'Y':
        df.to_csv(
            f'full_keyword_stats for {filename} from {str(start_date)[0:10]} to {str(end_date)[0:10]}.csv', index=False)
    
    if aors == 1:
        df = df[df['camp_status'].isin(['ENABLED']) & 
                df['adgroup_status'].isin(['ENABLED']) & 
                df['adgroup_criterion_status'].isin(['ENABLED'])
            ]
    
    elif aors == 2:
        df = df[#df['stv_status'].isin(['ENABLED']) &
                df['adgroup_status'].isin(['ENABLED']) &
                df['adgroupad_status'].isin(['ENABLED'])
                ]
        
    df = df.reset_index(drop=True)
    
    if aors == 1: 
        grps = df.groupby(['ad_group_criterion_resource_name']).groups
        var_resource_name = 'ad_group_criterion_resource_name'
        var_cost = 'metrics_cost_per_conversion'
        var_conversion = 'metrics_all_conversions'

    
    elif aors == 2:
        grps = df.groupby(['adgroupad_resource_name']).groups
        var_resource_name = 'adgroupad_resource_name'
        var_cost = 'metrics_cpa'
        var_conversion = 'metrics_all_conversions'
    
    full_range = []
    half_range = []
    for k, d in grps.items():
        if end_date in df.iloc[d]['date'].to_list():
            if start_date in df.iloc[d]['date'].to_list():
                full_range.append(k)
        else:
            half_range.append(k)
    
    to_pause = []
    
    # full_range
    # if cp conv > 2 * target
    # pause
    cpa_target = int(input('Enter CPA Target | Enter -1 to ignore : ')) * 1000000
    # cpa_target = 10000 * 50 # mock CPA Target 
    if cpa_target >= 0:
        for f in full_range:
            ad = df[df[var_resource_name] == f]
            ad = ad.sum(axis=0)
            if float(ad[var_cost]) >= 2 * cpa_target:
                # pause
                to_pause.append(f)
        
        for f in full_range:
            ad = df[df[var_resource_name] == f]
            ad = ad.sum(axis=0)
            if int(ad[var_cost]) >= 2 * cpa_target and ad[var_conversion] == 0:
                # pause
                to_pause.append(f)
            
    # half_range
    # if 100 clicks with 0 conv
    # pause
    for h in full_range:
        ad = df[df[var_resource_name] == h]
        ad = ad.sum(axis=0)
        if int(ad['metrics_clicks']) >= 100 and int(ad[var_conversion]) == 0:
            to_pause.append(f)
    
    if len(to_pause) == 0:
        print('Nothing to pause with given criteria')
    else:
        to_pause = list(set(to_pause))
        check_df = pd.DataFrame(columns=df.columns)
        for col in df.columns:
            if 'metrics' in col:
                df[col] = df.groupby([var_resource_name])[col].transform(sum)
        df = df.drop_duplicates(subset=[var_resource_name], keep='last')
        for f in to_pause:
            check_df = check_df.append(df[df[var_resource_name] == f])
        check_df.to_csv(f'check_poor_performance_{filename}.csv', index=False)
        print(f'please check --> check_poor_performance_{filename}.csv')
    
        inp = input('y or Y to pause or upload in negative list : ')
        if inp == 'y' or inp == 'Y':
            if aors == 1:
                for kw in to_pause:
                    full_name = kw.split('/')[-1].split('~')
                    # print(full_name)
                    update_keyword(client=googleads_client, customer_id = customer_id,
                                ad_group_id=full_name[0], criterion_id=full_name[1],
                                status = 'PAUSED')
            elif aors == 2:
                shared_set_id = int(input('Please provide negative keyword list id : '))
                PHRASE_kw = check_df[check_df['ad_group_criterion_keyword_match_type'] == 'PHRASE']
                add_negative_keywords(
                    googleads_client, customer_id, shared_set_id, PHRASE_kw['ad_group_criterion_keyword_text'].unique().tolist(), kw_type='PHRASE')
                EXACT_kw = check_df[check_df['ad_group_criterion_keyword_match_type'] == 'EXACT']
                add_negative_keywords(
                    googleads_client, customer_id, shared_set_id, PHRASE_kw['ad_group_criterion_keyword_text'].unique().tolist(), kw_type='EXACT')