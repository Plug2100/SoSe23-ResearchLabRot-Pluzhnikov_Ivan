from math import nan
import pandas as pd
import chromadb
import json
import sys


def count_common_elements(row, my_list): # Counting the common elements
    common_elements = set(row['fos']) & set(my_list)
    return len(common_elements)


def process_line(line, collection, df): # Processing line in the dataset
    data = pd.read_json(line, lines=True)
    if 'title' in data and 'fos' in data: # Check if data contain all values
        id_of_our_doc = data.at[0, 'id'] # Id of the dockument for which we build the recommendations
        responce = collection.get(ids=[str(id_of_our_doc)], include=['embeddings', 'documents'])
        embedding = responce['embeddings'][0] # embedding of the document for which we build the recommendations
        related_tags = data['fos'] # Extract FOS
        sim_embendings_tags = []
        for i in related_tags[0]: # Saving each FOS
            sim_embendings_tags.append(i['name'])
        elements_in_tags = set(sim_embendings_tags)
        # Receive recommendations from the Collection
        ans = collection.query(
            query_embeddings=[embedding],
            n_results=11
        )        
        count_threshold = 7 # Amount of the similar FOS for the good recommendations
        matching_rows = df[df.apply(count_common_elements, axis=1, my_list=list(elements_in_tags)) >= count_threshold] # delete with less amount of the similar FOS than count_threshold
        # Get the number of matching rows
        num_matching_rows_10 = len(matching_rows) - 1
        if(num_matching_rows_10 <= 0):
            return 0

        new_ids = ans['ids'][0][1:] # Delete document for which we are building recommendations itself.

        # Create counters to count rows that satisfy conditions
        count_with_elements_5 = 0
        count_with_elements_10 = 0

        # calculating the metrics
        now_pos = 0
        for new_id in new_ids: # Process all the recommendations
            # Filter the DataFrame to find the row with the desired id
            filtered_row = df[df['id'] == new_id]
            if not filtered_row.empty and now_pos < 10:
                elements_in_b = set(filtered_row['fos'].values[0])
                if(len(elements_in_tags & elements_in_b) >= count_threshold): # Check the amount of the similar FOS
                    common_elements = 1
                else:
                    common_elements = 0
                
                # Check the amount of the common elements
                if common_elements and now_pos < 5:
                    count_with_elements_5 += 1
                if common_elements:
                    count_with_elements_10 += 1
                now_pos += 1
        # Adding the results to the end of the file
        with open("Data/data_about_good_rec_recall.txt", "a") as file:
            print(count_with_elements_10 / num_matching_rows_10, count_with_elements_5 / num_matching_rows_10, count_with_elements_10 / 10, count_with_elements_5 / 5)
            file.write(f"{count_with_elements_10 / num_matching_rows_10} {count_with_elements_5 / num_matching_rows_10}, {count_with_elements_10 / 10}, {count_with_elements_5 / 5}\n")


def main():
    chroma_client = chromadb.PersistentClient(path="DataBase_with_cos_dist") # Connecting to the Database
    collection = chroma_client.get_collection(name='EMB_FOR_LLM_COS_DIST')  # Connecting to the collection
    file_path = "Data/dblp_papers_v11.txt" # Path to the Dataset
    data = []
    # Read data from the Dataset
    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line)
            if('fos' in record and 'id' in record):
                fos_names = [entry['name'] for entry in record['fos']]
                data.append({'id': record['id'], 'fos': fos_names})
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Processing line in the dataset
    with open(file_path, 'r') as file:
        line = file.readline()
        while line:
            process_line(line, collection, df)
            line = file.readline()

if __name__ == "__main__":
    main()