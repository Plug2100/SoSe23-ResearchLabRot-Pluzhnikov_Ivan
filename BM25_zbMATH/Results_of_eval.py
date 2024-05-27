def main():
    # Initialize dictionaries to store cumulative precision and recall for each amount of recs
    precision_accumulator = {"top5": 0, "top10": 0}
    recall_accumulator = {"top5": 0, "top10": 0}

    # Initialize counters for the number of lines (entries) in the file
    line_count = 0

    # Open the file for reading
    with open('Data/precision_recall_results.txt', 'r') as file:
        # Iterate through each line in the file
        for line in file:
            # Split the line into precision and recall values (comma-separated)
            values = line.strip().split(' ')
            if len(values) == 4:
                top5_precision, top5_recall, top10_precision, top10_recall = map(float, values)
                
                # Update cumulative precision and recall
                precision_accumulator["top5"] += top5_precision
                recall_accumulator["top5"] += top5_recall
                precision_accumulator["top10"] += top10_precision
                recall_accumulator["top10"] += top10_recall
                
                # Increment the line count
                line_count += 1

    # Calculate the average precision and recall for each amount of recs
    if line_count > 0:
        avg_precision_top5 = precision_accumulator["top5"] / line_count
        avg_recall_top5 = recall_accumulator["top5"] / line_count
        avg_precision_top10 = precision_accumulator["top10"] / line_count
        avg_recall_top10 = recall_accumulator["top10"] / line_count

        print(f"Average Precision (Top-5): {avg_precision_top5:.5f}")
        print(f"Average Recall (Top-5): {avg_recall_top5:.5f}")
        print(f"Average Precision (Top-10): {avg_precision_top10:.5f}")
        print(f"Average Recall (Top-10): {avg_recall_top10:.5f}")
    else:
        print("No data found in the file.")


if __name__ == "__main__":
    main()
