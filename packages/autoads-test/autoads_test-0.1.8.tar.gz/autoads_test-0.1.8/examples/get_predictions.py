import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from google.ads.googleads.client import GoogleAdsClient
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from autoads.keywords import get_keywords_from_api_and_url,get_keywords_from_google
from autoads.models import get_similarity_api,get_similarity_scrape,get_lfmfuf_predictions

seed_keywords = ["non dilutive funding", "non dilutive financing"] 

#Credentials/Settings for Dataforseo Api 
email = 'weilbacherindustries@gmail.com' # email in data for seo
api_key = '05f014a493983975' # api key for data for seo
df_api_path = 'data/df_api.csv' # filename for api keywords

#Credentials/Settings for Scraping
scrape = False # keep true if you want to scrape urls
depth = 1 # depth for scraping range from 1 to 4
urls = ['capchase.com','pipe.com'] # urls to scrape 
exclude = ['twitter', 'google', 'facebook', 'linkedin', 'youtube'] # sites to exclude
df_scrape_path = 'data/df_scrape.csv' # file name for scraped keywords

#Credentials/Setting for google
google = True # keep true if you want to download ideas from google keywords api
path = 'data/google-ads.yaml'
customer_id = '8306215642' #google ads customer id
df_google_path = 'data/df_google.csv'

df_final_path = 'data/df_final.csv'

similarity_model_path = 'Maunish/ecomm-sbert' # this model is already uploaded on huggingface so no need to download
lfmfuf_model_path = 'Maunish/kgrouping-roberta-large' # this model is already uploaded on huggingface so no need to download

df_api,df_scrape = get_keywords_from_api_and_url(
        email= email, 
        api_key=api_key, 
        seed_keywords=seed_keywords, 
        depth=depth, 
        scrape=scrape, 
        urls=urls, 
        exclude=exclude, 
)

model = SentenceTransformer(similarity_model_path)

model2 = AutoModelForSequenceClassification.from_pretrained(lfmfuf_model_path,num_labels=3)
tokenizer = AutoTokenizer.from_pretrained(lfmfuf_model_path)

map_group = {
    0:"LF",
    1:"MF",
    2:"UF",
    3:"competitor",
    4:"brand"}

print("Calculating similarity for api keywords")
keywords1 = df_api['Keywords'].tolist()
keywords2 = df_api['Keywords2'].tolist()
df_api['similarity'] = get_similarity_api(model,keywords1,keywords2)

print("Calculating lfmfuf predictions for api keywords")
api_predictions = get_lfmfuf_predictions(df_api,model2,tokenizer)
df_api['lf/mf/uf'] = np.argmax(api_predictions,axis=1)
df_api['lf/mf/uf'] = df_api['lf/mf/uf'].map(map_group)
df_api.loc[:,["LF","MF","UF"]] = api_predictions
df_api.to_csv(df_api_path,index=False)

df_final = df_api
if scrape:
    print("Calculating similarity for scraped keywords")
    scrape_keywords = df_scrape['Keywords'].tolist()
    for keyword in seed_keywords:
        df_scrape[keyword] = get_similarity_scrape(model,scrape_keywords,keyword)
    
    print("Calculating lfmfuf predictions for scrape keywords")
    scrape_predictions = get_lfmfuf_predictions(df_scrape,model2,tokenizer)
    df_scrape['lf/mf/uf'] = np.argmax(scrape_predictions,axis=1)
    df_scrape['lf/mf/uf'] = df_scrape['lf/mf/uf'].map(map_group)
    df_scrape.loc[:,["LF","MF","UF"]] = scrape_predictions
    temp = pd.melt(df_scrape,id_vars=['Keywords'],value_vars=seed_keywords,var_name='Keywords2',value_name='similarity')
    temp = temp.loc[temp.groupby(['Keywords'])['similarity'].idxmax()]  
    df_scrape = temp.merge(df_scrape.drop(seed_keywords,axis=1),how='left',on='Keywords')
    df_final = pd.concat([df_final,df_scrape]).reset_index(drop=True)
    df_scrape.to_csv(df_scrape_path,index=False)

if google:
    googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")
    df_google = get_keywords_from_google(googleads_client,customer_id,seed_keywords)
    df_google = df_google.drop_duplicates("Keywords")
    df_google = df_google.loc[:,["Keywords","Keywords2"]]
    print("Calculating similarity for google keywords")
    keywords1 = df_google['Keywords'].tolist()
    keywords2 = df_google['Keywords2'].tolist()
    df_google['similarity'] = get_similarity_api(model,keywords1,keywords2)
    print("Calculating lfmfuf predictions for google keywords")
    google_predictions = get_lfmfuf_predictions(df_google,model2,tokenizer)
    df_google['lf/mf/uf'] = np.argmax(google_predictions,axis=1)
    df_google['lf/mf/uf'] = df_google['lf/mf/uf'].map(map_group)
    df_google.loc[:,["LF","MF","UF"]] = google_predictions
    df_google.to_csv(df_google_path,index=False)
    df_final = pd.concat([df_final,df_google])
    
df_final.to_csv(df_final_path,index=False)

print(df_api.head())
print(df_scrape.head())
print(df_google.head())
print(df_final.head())
