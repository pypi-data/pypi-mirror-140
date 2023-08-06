import os
import re
import time
import nltk
import argparse
import numpy as np
import pandas as pd
from autoads.client import RestClient
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from urllib.request import urlopen
from base64 import urlsafe_b64decode
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def get_keywords_from_api_and_url(email, 
        api_key, 
        seed_keywords, 
        depth, 
        scrape, 
        urls, 
        exclude):
    
    client = RestClient(email, api_key)

    def get_keywords(keyword, depth=depth, location='United States'):
        post_data = dict()
        post_data[len(post_data)] = dict(
            keyword=keyword,
            location_name=location,
            language_name="English",
            depth=depth,
        )
        post_data2 = dict()
        post_data2[len(post_data2)] = dict(
            keywords=[keyword],
            location_name=location,
            language_name="English",
            depth=depth,
        )
        response = client.post(
            "/v3/dataforseo_labs/related_keywords/live", post_data)
        response2 = client.post(
            "/v3/dataforseo_labs/keyword_ideas/live", post_data2)
        response3 = client.post(
            "/v3/dataforseo_labs/keyword_suggestions/live", post_data)

        return {  
            'related': response,
            'ideas': response2,
            'suggestions': response3
        }
        
    def extract_keywords(responses):
        key_list = []
        sources = []

        # print(responses)
        
        if responses['related']["status_code"] == 20000 and responses['related']['tasks'][0]['result'][0]['items']:
            for x in range(len(responses['related']['tasks'][0]['result'][0]['items'])):
                res = responses['related']['tasks'][0]['result'][0]['items'][x]['related_keywords']
                if res is not None:
                    key_list.extend(res)
            print(f"{len(key_list)} related")
            sources.extend(['related' for _ in range(len(key_list))])
            
        if responses['ideas']["status_code"] == 20000 and responses['ideas']['tasks'][0]['result'][0]['items']:
            # not good ideas
            print(f"{len(responses['ideas']['tasks'][0]['result'][0]['items'])} ideas")
            for x in range(len(responses['ideas']['tasks'][0]['result'][0]['items'])):
                res = responses['ideas']['tasks'][0]['result'][0]['items'][x]['keyword']
                if res is not None:
                    key_list.append(res)
            sources.extend(['ideas' for _ in range(
                len(responses['ideas']['tasks'][0]['result'][0]['items']))])
                    
        if responses['suggestions']["status_code"] == 20000 and responses['suggestions']['tasks'][0]['result'][0]['items']:
            print(f"{len(responses['suggestions']['tasks'][0]['result'][0]['items'])} suggestions")
            for x in range(len(responses['suggestions']['tasks'][0]['result'][0]['items'])):
                res = responses['suggestions']['tasks'][0]['result'][0]['items'][x]['keyword']
                if res is not None:
                    key_list.append(res)
            sources.extend(['suggestions' for _ in range(
                len(responses['suggestions']['tasks'][0]['result'][0]['items']))])
        # else:
        #     print("error. Code: %d Message: %s" %
        #           (responses['all]["status_code"], responses['all']["status_message"]))
        temp = {
            'Keywords' : key_list,
            'Sources' : sources
        }
        df = pd.DataFrame.from_dict(temp)
        return df
    
    def add_spaces(text, thresh = 3, clean_n = False):
        cleaned = ''
        temp = [l.isupper() for l in text]
        chk = 0
        for i, s in enumerate(temp):
            if s and i != 0 and (i - chk) > thresh:
                cleaned += ' ' + ext[chk : i]
                chk = i
        for i, w in enumerate(cleaned):
            if w != ' ':
                cleaned = cleaned[i:]
                break
            else:
                i+=1
        if clean_n:
            cleaned = cleaned.replace('\n', ' ')
        return cleaned.replace('  ', ' ')
    
    def clean(text):
        text = text.replace('*', '')
        text = text.replace('\ufeff', '')
        text = text.replace('\n', '')
        text = text.replace('.', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace('"', '')
        text = text.replace('/', ' ')
        text = text.replace('%', ' ')
        text = text.replace('-', '')
        text = text.replace('”', '')
        text = text.replace('“', '')
        text = text.replace('\'', '')
        text = text.replace('!', '')
        text = text.replace('?', '')
        text = text.replace('&', '')
        text = text.replace('+', '')
        text = text.replace('$', '')
        text = text.replace(',', '')
        return text
    
    def _extract_(urls, depth = 1, return_urls = True, return_redirects = True, exclude = exclude):
        print(urls)
        exclude = exclude
        scrape_urls = urls
        resp = []
        resp_urls = []
        full_text = ''
        depth = depth
        for _ in range(depth):
            temp_urls = []
            for url in scrape_urls:
                try:
                    chk = 0
                    for exc in exclude:
                        if exc in url:
                            # print(url)
                            chk = 1
                    
                    if chk == 0:
                        html = urlopen(url).read()
                        # print(html)
                        soup = BeautifulSoup(html, features="html.parser")
                        
                        for link in soup.find_all('a', attrs = {'href':re.compile('^/')}):
                            uri = link.get('href')
                            temp_urls.append(url + uri)
                            # print(uri)
                        
                        for link in soup.find_all('a', attrs={'href': re.compile('^https://')}):
                            uri = link.get('href')
                            temp_urls.append(uri)
                        
                        for script in soup(['script', 'style']):
                            script.extract()
                        
                        text = soup.get_text()
                        
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = '\n'.join(chunk for chunk in chunks if chunk)
                        full_text += ' ' + text
                        resp_urls.append(url)
                        resp.append(1)
                except:
                    resp_urls.append(url)
                    resp.append(0)
                    continue
        
            scrape_urls = list(set(temp_urls))
            
        if return_urls:
            if return_redirects:
                return full_text, resp_urls, (resp_urls, resp)
            else:
                return full_text, resp_urls
        elif return_redirects:
            return full_text, (resp_urls, resp)
        else:
            return full_text
    
    os.makedirs('data',exist_ok=True)
    keyword_list = seed_keywords
    df_api = pd.DataFrame(columns=['Keywords', 'Keywords2', 'Sources'])

    for keyword in keyword_list:
        try:
            print(f'keyword : {keyword}')
            keywords = get_keywords(keyword, depth=depth)
            extracted = extract_keywords(keywords)
            keywords2 = [keyword for _ in range(extracted.shape[0])]
            extracted['Keywords2'] = keywords2
            df_api = pd.concat([df_api, extracted])
        except:
            print(f"error in {keyword}")
    
    fin_ngrams = []
    if scrape:
        new_urls = []
        for url in urls:
            if not 'http' in url:
                if not 'www' in url:
                    new_urls.append(f'https://www.{url}')
                else:
                    new_urls.append(f'https://{url}')
        urls = new_urls
        fin_ngrams = []
        ext, _, _ = _extract_(urls, depth=depth)
        # print(ext)
        ext = add_spaces(ext, clean_n=True)
        text_path = os.path.join(os.getcwd(),'data/text.txt')
        with open(text_path, 'w', encoding="utf-8") as f:
            f.write(ext)
            
        nltk.download('stopwords')
        stop = set(stopwords.words('english'))
        text = clean(ext)
        splt_text = text.split(' ')
        nw_list = []
        for t in splt_text:
            if t not in stop and not t == '' and not t.isdigit() and len(t) > 1:
                nw_list.append(t)
                
        ngrams = []
        ngrams.extend(nltk.ngrams(nw_list, 3))
        ngrams.extend(nltk.ngrams(nw_list, 4))
        
        # print(fin_ngrams)
        for ngram in ngrams:
            fin_ngrams.append(' '.join([ng for ng in ngram]))
        
    df_scrape = pd.DataFrame(columns=['Keywords'], data=fin_ngrams)

    return df_api,df_scrape


# Location IDs are listed here:
# https://developers.google.com/google-ads/api/reference/data/geotargets
# and they can also be retrieved using the GeoTargetConstantService as shown
# here: https://developers.google.com/google-ads/api/docs/targeting/location-targeting
_DEFAULT_LOCATION_IDS = ["1023191"]  # location ID for New York, NY
# A language criterion ID. For example, specify 1000 for English. For more
# information on determining this value, see the below link:
# https://developers.google.com/google-ads/api/reference/data/codes-formats#expandable-7
_DEFAULT_LANGUAGE_ID = "1000"  # language ID for English


def get_keyword_ideas(
    client, customer_id, location_ids, language_id, keyword_texts, page_url
):
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    keyword_competition_level_enum = (
        client.enums.KeywordPlanCompetitionLevelEnum
    )
    keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    )
    location_rns = _map_locations_ids_to_resource_names(client, location_ids)
    language_rn = client.get_service("GoogleAdsService").language_constant_path(
        language_id
    )

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # Only one of the fields "url_seed", "keyword_seed", or
    # "keyword_and_url_seed" can be set on the request, depending on whether
    # keywords, a page_url or both were passed to this function.
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants = location_rns
    request.include_adult_keywords = False
    request.keyword_plan_network = keyword_plan_network

    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not keyword_texts and page_url:
        request.url_seed.url = page_url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if keyword_texts and not page_url:
        request.keyword_seed.keywords.extend(keyword_texts)

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if keyword_texts and page_url:
        request.keyword_and_url_seed.url = page_url
        request.keyword_and_url_seed.keywords.extend(keyword_texts)

    keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )

    all_keywords = list()
    all_avg_monthly_searches = list()
    all_competitions_values = list()
    for idea in keyword_ideas:
        competition_value = idea.keyword_idea_metrics.competition.name
        # print(
        #     f'Keyword idea text "{idea.text}" has '
        #     f'"{idea.keyword_idea_metrics.avg_monthly_searches}" '
        #     f'average monthly searches and "{competition_value}" '
        #     "competition."
        # )
        all_keywords.append(idea.text)
        all_avg_monthly_searches.append(idea.keyword_idea_metrics.avg_monthly_searches)
        all_competitions_values.append(competition_value)

    df = pd.DataFrame({"Keywords":all_keywords,"Keywords2":keyword_texts[0],
                    "volume":all_avg_monthly_searches,
                    "competition_value":all_competitions_values})
    return df


def map_keywords_to_string_values(client, keyword_texts):
    keyword_protos = []
    for keyword in keyword_texts:
        string_val = client.get_type("StringValue")
        string_val.value = keyword
        keyword_protos.append(string_val)
    return keyword_protos


def _map_locations_ids_to_resource_names(client, location_ids):
    """Converts a list of location IDs to resource names.

    Args:
        client: an initialized GoogleAdsClient instance.
        location_ids: a list of location ID strings.

    Returns:
        a list of resource name strings using the given location IDs.
    """
    build_resource_name = client.get_service(
        "GeoTargetConstantService"
    ).geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]

def get_keywords_from_google(googleads_client,
                            customer_id,seed_keywords,
                            lanugage_id=_DEFAULT_LANGUAGE_ID,
                            location_id=_DEFAULT_LOCATION_IDS):

    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    seed_keywords = [[x] for x in seed_keywords]
    df_google = pd.DataFrame()
    for keyword in seed_keywords:
        print(f"Collecting keyword ideas for {keyword[0]}")
        try:
            df = get_keyword_ideas(
                    googleads_client,
                    customer_id=customer_id,
                    location_ids=location_id,
                    language_id=lanugage_id,
                    keyword_texts=keyword,
                    page_url=None
                )
            df_google = df_google.append(df)
            time.sleep(2)
        except GoogleAdsException as ex:
            print(
                f'Request with ID "{ex.request_id}" failed with status '
                f'"{ex.error.code().name}" and includes the following errors:'
            )
            for error in ex.failure.errors:
                print(f'\tError with message "{error.message}".')
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"\t\tOn field: {field_path_element.field_name}")
            sys.exit(1)

    return df_google

def get_keywords_metrics(email,api_key,df,match_extract):

    client = RestClient(email,api_key)

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

    keywords_list = df['Keywords'].unique().tolist()
    if len(keywords_list) > 1000:
        for i, x in enumerate(range(0, len(keywords_list), 1000)):
            volume = get_volume(keywords_list[i*1000: (i+1)*1000])
            extract_volume(volume)
            for c in match_extract:
                cpc = get_cpc(keywords_list, match=c)
                extract_cpc(cpc)   
    else:
        response = get_volume(keywords_list)
        extract_volume(response)
        for c in match_extract:
            cpc = get_cpc(keywords_list, match=c)
            extract_cpc(cpc)

    fin_df_1 = pd.DataFrame.from_dict(keyword_metrics, orient='index')
    fin_df_1.transpose()
    fin_df_2 = pd.DataFrame.from_dict(cpc_metrics, orient='index')
    fin_df_2.transpose()
    fin_df = pd.merge(left=fin_df_1, right=fin_df_2, how='left', on=['Keywords'])

    df = pd.merge(left=df, right=fin_df, how='left', on=['Keywords'])
    df

    return df

def make_request(keyword, email, api_key):
    client = RestClient(email, api_key)
    post_data = dict()
    post_data[len(post_data)] = dict(
        language_name="English",
        location_name="United States",
        keyword=keyword,
        priority=2,
        depth=5,
        max_crawl_pages=2,
        tag=f"{keyword} google",
    )
    response = client.post(
        "/v3/serp/google/organic/task_post", post_data)
    if response["status_code"] == 20000:
        print('please wait for sometime.. till we gather data')
        return(response, response['tasks'][0]['id'])
    else:
        print("error. Code: %d Message: %s" %
              (response["status_code"], response["status_message"]))


def make_live_request(keyword, email, api_key,priority = 2, depth = 2, max_crawl_pages = 2):
    client = RestClient(email, api_key)
    post_data = dict()
    post_data[len(post_data)] = dict(
        language_name="English",
        location_name="United States",
        keyword=keyword,
        priority=priority,
        depth=depth,
        max_crawl_pages=max_crawl_pages,
        tag=f"{keyword} google",
    )
    response = client.post(
        "/v3/serp/google/organic/live/advanced", post_data)
    if response["status_code"] == 20000:
        print('please wait for sometime.. till we gather data')
        return response
    else:
        print("error. Code: %d Message: %s" %
              (response["status_code"], response["status_message"]))


def get_results(results, tasks, task_params):
    df = {
        'organic_url' : list(),
        'organic_description' : list(),
        'organic_extended_people_also_search' : list(),
    }
    for i, data in enumerate(results['tasks'][0]['result'][0]['items']):
        task = data['type']
        if task == 'organic' and task in tasks:
            # [url, description, extended_people_also_search]
            for key in data.keys():
                if key in task_params[f'{task}']:
                    df[f'{task}_{key}'].append(str(data[f'{key}']))

        if task == 'people_also_ask' and task in tasks:
            all_items = {f'{task}_{param}': list()
                                                 for param in task_params[task]}
            for item in data['items']:
                all_items[f'{task}_title'].append(item[f'title'])
                for key in item['expanded_element'][0].keys():
                    if key in task_params[task]:
                        all_items[f'{task}_{key}'].append(
                            item['expanded_element'][0][f'{key}'])
            all_items = {k: str(v) for k, v in all_items.items()}
            df.update(all_items)

        if task == 'related_searches' and task in tasks:
            df[f'{task}_items'] = str(data[f'items'])

        # put top_stories['items'] params in task_params
        if task == 'top_stories' and task in tasks:
            # [domain, title, date, url]
            all_items = {f'{task}_{param}': list()
                                                 for param in task_params[task]}
            all_items[f'{task}_title'].append(data['title'])
            for item in data['items']:
                for key in item.keys():
                    if key in task_params[f'{task}'] and key != 'title':
                        all_items[f'{task}_{key}'].append(item[f'{key}'])
                    # df[f'{task}_{key}'] = data[f'{key}']
            all_items = {k: str(v) for k, v in all_items.items()}
            df.update(all_items)

        if task == 'knowledge_graph' and task in tasks:
            all_items = {f'{task}_{param}': list()
                                                 for param in task_params[task]}
            #[title, url, text]
            all_items.update({f'{task}_main_title': list(),
                             f'{task}_description': list()})
            all_items[f'{task}_main_title'].append(data[f'title'])
            all_items[f'{task}_description'].append(data[f'description'])
            for item in data['items']:
                try:
                    all_items[f'{task}_text'].append(item[f'text'])
                        
                except:
                    all_items[f'{task}_text'].append(None)
                    for key in item.keys():
                        if key in task_params[f'{task}'] and key != 'text':
                            try:
                                all_items[f'{task}_{key}'].append(item['links'][0][f'{key}'])
                            except:
                                all_items[f'{task}_{key}'].append(None)
            all_items = {k: str(v) for k, v in all_items.items()}
            df.update(all_items)

    return df
