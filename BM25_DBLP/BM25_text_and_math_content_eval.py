import re
from elasticsearch import Elasticsearch
import warnings
import multiprocessing
import json
import pandas as pd
import os


def count_common_elements(row, my_list): # Calculating the amount of the comon elements
    fos = []
    for i in row['fos']:
        fos.append(i.lower())
    common_elements = set(fos) & set(my_list)
    return len(common_elements)


def BM25_search_math(es, text, sorted_fos_string, art_id, df):
    # Search query using BM25 and size restriction to get recommendations
    search_query = {
        "query": {
            "match": {
                "content": text
            }
        },
        "size": 11
    }
    # Executing a search query.
    index_name = "bm25_rec_text_and_math_content"
    search_results = es.search(index=index_name, body=search_query)
    short_elements = set(sorted_fos_string.split(", ")) # Preprocessing results
    count_threshold = 7 # threshold for the common elements
    matching_rows = df[df.apply(count_common_elements, axis=1, my_list=list(short_elements)) >= count_threshold] # Leave only lines with appropriate amount of the common elements
    num_matching_rows = len(matching_rows) - 1 # amount of the suitable recommendations
    if(num_matching_rows <= 0):
        return 0

    # Calculate results
    at_all = 0
    good_rec = 0
    count_with_elements_5 = 0
    count_with_elements_10 = 0
    for hit in search_results["hits"]["hits"]: # Process each potential recommendation
        ID = hit['_id']
        FOS = hit['_source']['fos']
        if(art_id != int(ID)):
            long_elements = set(FOS.split(", ")) # Preprocess recommendation
            common_elements = long_elements.intersection(short_elements) # Calculate amount of the common elements
            if(len(common_elements) >= count_threshold): # Check if the recommendation is suitable
                count_with_elements_10 += 1
            if(at_all < 5):
                if(len(common_elements) >= count_threshold):
                   count_with_elements_5 += 1
            at_all += 1
    directory_path = "Data"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    file_path = os.path.join(directory_path, "results.txt")
    #  Write recall and precision as a single line
    with open(file_path, "a") as file:
        file.write(f"{count_with_elements_10 / num_matching_rows}, {count_with_elements_5 / num_matching_rows}, {count_with_elements_10 / 10}, {count_with_elements_10 / 5}\n")


def Data_to_str(es, data, title, art_id, sorted_fos_string, df): # Process line from the Dataset
    text = ''
    text = ' '.join(data['InvertedIndex'].keys()) # Convert data into the string
    BM25_search_math(es, text, sorted_fos_string, art_id, df) # Process line from the Dataset



def process_line(es, line, df):
    data = pd.read_json(line, lines=True) # Read line
    if 'indexed_abstract' in data and 'fos' in data: # Preprocessing data
        data.dropna(subset=['indexed_abstract'], inplace=True)
        data['fos'] = data['fos'].apply(lambda x: ', '.join([field['name'].lower() for field in x]))
        sorted_fos_names = data['fos'].str.split(', ').explode().unique()
        sorted_fos_string = ', '.join(sorted(sorted_fos_names))
        data.apply(lambda row: Data_to_str(es, row['indexed_abstract'], row['title'], row['id'], sorted_fos_string, df), axis=1) # Process lines in the Dataset


def main():
    warnings.filterwarnings("ignore", message="The 'body' parameter is deprecated and will be removed in a future version.")
    # Path to the Dataset
    file_path = "Data/dblp_papers_v11.txt"
    data = []

    # Read the file and process each line of the dataset
    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line)
            if 'fos' in record and 'id' in record: 
                fos_names = [entry['name'] for entry in record['fos']]
                data.append({'id': record['id'], 'fos': fos_names}) # Convert line into Pandas dataset line

    df = pd.DataFrame(data) # Convert dataset into Pandas 
    # Conection with the Elasticsearch
    index_name = "bm25_rec_text_and_math_content"
    es = Elasticsearch(hosts=["http://localhost:9200"])

    # Reopen the file to process lines using the 'process_line' function
    with open(file_path, 'r') as file:
        line = file.readline()
        while line:
            process_line(es, line, df)
            line = file.readline()


# Call the main function if the script is executed
if __name__ == "__main__":
    main()
