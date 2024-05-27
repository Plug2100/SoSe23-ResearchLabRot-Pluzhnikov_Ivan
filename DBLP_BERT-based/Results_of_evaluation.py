def main():
    # Initialize counters for each column
    count_10 = 0
    count_5 = 0
    count_5_pr = 0
    count_10_pr = 0

    lines_with_10 = 0
    lines_with_5 = 0
    lines_with_5_pr = 0
    lines_with_10_pr = 0

    # Open file with the good recommendations for reading
    with open('Data/data_about_good_rec_recall.txt', 'r') as file:
        # Processing the lines
        lines = file.readlines()
        for line in lines:
            # Preprocessing
            values = [num for num in line.replace(',', ' ').split()]
            # Convert to int
            if(values[0] != 'nan'):
                lines_with_10 += 1
                count_10 += float(values[0])
            if(values[1] != 'nan'):
                lines_with_5 += 1
                count_5 += float(values[1])
            if(values[2] != 'nan'):
                lines_with_10_pr += 1
                count_10_pr += float(values[2])
            if(values[3] != 'nan'):
                lines_with_5_pr += 1
                count_5_pr += float(values[3])

    # Calculate average
    average_recall_10 = count_10 / lines_with_10
    average_recall_5 = count_5 / lines_with_5
    average_pr_10 = count_10_pr / lines_with_10_pr
    average_pr_5 = count_5_pr / lines_with_5_pr

    # print the results
    print("Avg recall for 10:", average_recall_10)
    print("Avg recall for 5:", average_recall_5)
    print("Avg precision for 10:", average_pr_10)
    print("Avg precision for 5:", average_pr_5)

if __name__ == "__main__":
    main()
