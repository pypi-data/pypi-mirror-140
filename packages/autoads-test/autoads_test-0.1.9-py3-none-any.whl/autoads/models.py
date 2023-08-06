import os
import torch
import random
import numpy as np
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics.pairwise import cosine_similarity

def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONASSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

def get_similarity_api(model,keywords1,keywords2):
    keywords1_embed = model.encode(keywords1)
    keywords2_embed = model.encode(keywords2)
    
    results = list()
    for embed1,embed2 in zip(keywords1_embed,keywords2_embed):
        result = cosine_similarity([embed1],[embed2])
        results.append(result)
    return np.array(results).ravel()

def get_similarity_scrape(model,all_keywords,main_keyword):
    
    all_embeddings = model.encode(all_keywords)
    main_embedding = model.encode([main_keyword])

    results = cosine_similarity(
        all_embeddings,
        main_embedding,)
    return np.array(results)

def get_similarity_matrix(model,exisitng_keywords,new_keywords):
    
    exisitng_embeddings = model.encode(exisitng_keywords)
    new_embeddings = model.encode(new_keywords)

    results = cosine_similarity(
        new_embeddings,
        exisitng_embeddings,
    )
    return np.array(results)

class GadsTestDataset(Dataset):
    def __init__(self,df,tokenizer):
        self.keywords = df['Keywords'].to_numpy()
        self.tokenizer = tokenizer
    
    def __getitem__(self,idx):
        encode = self.tokenizer(self.keywords[idx],return_tensors='pt',
                                max_length=10,
                                padding='max_length',truncation=True)
        return encode
    
    def __len__(self):
        return len(self.keywords)


def get_lfmfuf_predictions(df,model,tokenizer):   
    device = "cuda" if torch.cuda.is_available() else "cpu"     
    predictions = list()
    model.to(device)
    model.eval()

    test_ds = GadsTestDataset(df,tokenizer)
    test_dl = DataLoader(test_ds,
                        batch_size = 64,
                        shuffle=False,
                        drop_last=False,
                        pin_memory=True)

    with torch.no_grad():
        pred = list()
        print("making predictions")
        for i, (inputs) in enumerate(tqdm(test_dl)):
            inputs = {key:val.reshape(val.shape[0],-1).to(device) for key,val in inputs.items()}
            outputs = model(**inputs)
            outputs = outputs['logits'].cpu().detach().softmax(axis=1).numpy().tolist()
            pred.extend(outputs)
        predictions.append(pred)
            
    torch.cuda.empty_cache()
    return np.array(predictions).reshape(df.shape[0],3)

