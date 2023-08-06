from autoads.keywords import get_keywords_from_google
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

df_path = 'data/keywords_to_upload.csv' # specify keywords to uplod csv here
save_path = 'data'
path = '/home/maunish/Upwork Projects/Google-Ads-Project/examples/google-ads.yaml'
customer_id = '6554081276'
seed_keywords = ["crypto 401k", "real estate 401k", "esg 401k", "business 401k", "business crypto 401k", "business esg 401k"] 
    
googleads_client = GoogleAdsClient.load_from_storage(path=path, version="v9")
df_google = get_keywords_from_google(googleads_client,customer_id,seed_keywords)

print(df_google)