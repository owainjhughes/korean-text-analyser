import csv

input_file = "kengdic.tsv"
output_file = "kengdic_cleaned.tsv"

with open(input_file, encoding='utf-8') as infile, open(output_file, "w", encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter='\t')

    for row in reader:
        if len(row) < 7:
            continue
        # Keep only: id, surface, gloss, level (columns 0, 1, 3, 4)
        cleaned_row = [row[0], row[1], row[3], row[4]]
        writer.writerow(cleaned_row)

print("Cleaned TSV saved to", output_file)
