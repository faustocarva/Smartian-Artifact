import os
import shutil
import csv
import argparse

def read_csv(csv_file):
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def group_entries(data, group_size):
    groups = []
    for i in range(0, len(data), group_size):
        groups.append(data[i:i+group_size])
    return groups

def create_subdirectories(groups, output_dir):
    for i, group in enumerate(groups):
        subdir = os.path.join(output_dir, f'subdir{i+1}')
        os.makedirs(subdir, exist_ok=True)
        for j, entry in enumerate(group):
            source_file = entry[0] + ".sol"
            destination_file = os.path.join(subdir, os.path.basename(source_file))
            shutil.copy(source_file, destination_file)
        write_csv(group, subdir)

def write_csv(data, output_dir):
    csv_file = os.path.join(output_dir, 'contracts.csv')
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def main(csv_file, group_size, output_dir):
    data = read_csv(csv_file)
    groups = group_entries(data, group_size)
    create_subdirectories(groups, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Group CSV entries into subdirectories.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('group_size', type=int, help='Number of entries per group')
    parser.add_argument('output_dir', type=str, help='Output directory path')
    args = parser.parse_args()

    main(args.csv_file, args.group_size, args.output_dir)

