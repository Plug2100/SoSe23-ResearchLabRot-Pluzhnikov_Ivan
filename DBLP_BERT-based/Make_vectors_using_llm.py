import torch
from transformers import BertTokenizer, BertModel
import pandas as pd
import chromadb
import json
import subprocess


def convert_to_emb_and_save(text, id_, collection, model, tokenizer): # Building embeddings and saving them
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    max_length = 512
    encoded_text = tokenizer(text, padding=True, truncation=True, max_length=max_length, return_tensors="pt") # Tokenizing text
    encoded_text = encoded_text.to(device)
    with torch.no_grad(): # Building embeddings
        model_output = model(**encoded_text) # Building embeddings
        embedding = model_output.last_hidden_state.mean(dim=1) # Building embeddings
        collection.add(
            embeddings=[embedding.tolist()[0]],
        ids=[str(id_)] # Adding embeddings to the collection
    )

def process_line(line, collection, model, tokenizer):
    line = json.loads(line) # Preprocessing
    convert_to_emb_and_save(line['title'], line['id'], collection, model, tokenizer) # Building embeddings and saving them



def main():
    file_path = "Data/dblp_papers_v11.txt"  # Path to the DBLP v11 dataset
    databas = "DataBase_with_cos_dist"
    collection_name = "EMB_FOR_LLM_COS_DIST"
    chroma_client = chromadb.PersistentClient(path=databas) # Make Database
    collection = chroma_client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"}) # Make collection in the Database
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = BertTokenizer.from_pretrained('tbs17/MathBERT', output_hidden_states=True) # Load MathBERT tokenizer
    model = BertModel.from_pretrained("tbs17/MathBERT") # Load MathBERT model
    model = model.to(device)
    with open(file_path, 'r') as file: # Processing data from file
        line = file.readline()
        while line:
            process_line(line, collection, model, tokenizer)
            line = file.readline()
    process_to_calc_rec = subprocess.run(['python3', 'Recommendations_validation.py', file_path, databas, collection_name])
    process_to_calc_rec = subprocess.run(['python3', 'Results_of_evaluation.py'])
    

if __name__ == "__main__":
    main()
