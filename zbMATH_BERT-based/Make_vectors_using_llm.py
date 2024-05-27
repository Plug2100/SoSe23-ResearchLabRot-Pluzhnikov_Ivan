import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertModel
import pandas as pd
import chromadb
import os
import shutil
import ast
import math
import subprocess


def convert_to_emb_and_save(text, title, id_, keyword, collection, text_sourse, method, tokenizer, model): # Function to save embeddings into the database
    # text preprocessing
    if text_sourse == 'text':
        pass
    elif text_sourse == 'title':
        text = title
    elif text_sourse == 'keyword':
        if(keyword != 'No keyword available'):
            if isinstance(keyword, float) and math.isnan(keyword):
                text = 'No keyword available'
            elif isinstance(keyword, str):
                text = keyword
            else:
                text = ' '.join(ast.literal_eval(keyword))
        else:
           text = keyword 
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Tokenization of the input text
    max_length = 512
    encoded_text = tokenizer(text, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
    encoded_text = encoded_text.to(device)
    with torch.no_grad():
        model_output = model(**encoded_text)
        # Bert output method
        if method == 'mean':
            embedding = model_output.last_hidden_state.mean(dim=1)
        elif method == 'pooler_output':
            embedding = model_output.pooler_output
        collection.add(
        embeddings=[embedding.tolist()[0]],
        ids=[str(id_)]
    )


def process_line(row, collection, text_sourse, method, tokenizer, model):
    convert_to_emb_and_save(row['text'], row['title'], row['de'], row['keyword'], collection, text_sourse, method, tokenizer, model)


def main():
    file_path = 'Data/out.csv' # Path to the zbMATH dataset
    df = pd.read_csv(file_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    for bert_type in ['Bert', 'SciBert', 'MathBert']: # Choose Bert-based model.
        if bert_type == 'MathBert':
            tokenizer = BertTokenizer.from_pretrained('tbs17/MathBERT', output_hidden_states=True)
            model = BertModel.from_pretrained("tbs17/MathBERT")
        elif bert_type == 'SciBert':
            tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
            model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
        elif bert_type == 'Bert':
            tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")  
            model = AutoModel.from_pretrained("bert-base-uncased") 
        
        for text_sourse in ['keyword', 'title', 'text']: # Choose text sourse for the vector representation. Text in this case is the abstract.
            df = df.dropna(subset=[text_sourse]) # Preprocessing
            for method in ['pooler_output', 'mean']: # Choose method to obtain vector from the BERT-based model.

                path = bert_type + '_' + text_sourse + '_' + method
                if os.path.exists(path):
                    shutil.rmtree(path)
                # Make Database
                chroma_client = chromadb.PersistentClient(path)
            
                model = model.to(device)

                collection = chroma_client.create_collection(name="embedding", metadata={"hnsw:space": "cosine"})  # Make collection in the Database
                df.apply(lambda row: process_line(row, collection, text_sourse, method, tokenizer, model), axis=1)
                                    
                # Run programms for the results evaluation
                process_to_calc_rec = subprocess.run(['python3', 'Read_vectors.py', path, text_sourse, file_path])
                process_for_eval = subprocess.run(['python3', 'Results_of_eval.py'], stdout=subprocess.PIPE, text=True)
                
                output = process_for_eval.stdout
                    
                with open('Data/Results_of_experiments.txt', 'a') as file:
                        # Write precision and recall as a single line
                    file.write(f"{bert_type}, {text_sourse}, {method} \n{output} \n \n \n")


if __name__ == "__main__":
    main()
