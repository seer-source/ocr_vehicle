"""import csv
import shutil
import os

# Define the input CSV file path and the output folder for images
csv_file = 'visitor_visitor.csv'
output_folder = 'id_front/'  # Folder name for storing id_front images

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Open the CSV file and read its contents
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for row in reader:
        print(row)
        id_front_path = row['id_front']
        national_id = row['national_id']

        # Copy the id_front image to the new folder with a new name based on national_id
        if id_front_path:
            # Extract the filename from the original path
            filename = id_front_path.split('/')[-1]

            # Build the new path for the image in the output folder
            new_path = os.path.join(output_folder, f'{national_id}.jpg')

            # Copy the image to the new path
            shutil.copy(id_front_path, new_path)

            # Print a message to confirm the copy
            print(f'Copied {filename} to {new_path}')
"""
import pandas as pd
import shutil
import os

# Define the input CSV file path and the output folder for images
csv_file = 'visitor_visitor.csv'
output_folder = 'id_front/'  # Folder name for storing id_front images

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the CSV file using Pandas
df = pd.read_csv(csv_file, encoding='utf-8')

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    print(row)
    id_front_path = row['id_front']
    national_id = row['national_id']

    # Copy the id_front image to the new folder with a new name based on national_id
    if not pd.isna(id_front_path):
        # Extract the filename from the original path
        filename = id_front_path.split('/')[-1]

        # Build the new path for the image in the output folder
        new_path = os.path.join(output_folder, f'{national_id}.jpg')

        # Copy the image to the new path
        shutil.copy(id_front_path, new_path)

        # Print a message to confirm the copy
        print(f'Copied {filename} to {new_path}')

