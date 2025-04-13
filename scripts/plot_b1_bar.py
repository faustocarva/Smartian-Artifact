#!/usr/bin/env python3
import os
import re
import sys
import matplotlib.pyplot as plt
import matplotlib
import argparse

# Use a non-interactive backend for PDF output
matplotlib.use('Agg')

# Ensure matplotlib accepts hex color codes
import matplotlib.colors as mcolors

def extract_value(file_path):
    """Extract the value at '60m:' from the given file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Find the 60m value using a regular expression
            match = re.search(r'60m: (\d+\.\d+)', content)
            if match:
                return float(match.group(1))
            else:
                print(f"Warning: No '60m:' value found in {file_path}")
                return 0.0
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0.0

def extract_label_from_filename(filename):
    """Extract the text after the last underscore in the filename."""
    return filename.split('_')[-1] if '_' in filename else filename    

def create_bar_plot(files, model, bar_color='#1f77b4', output_file='time_values_bar_plot.pdf'):
    """Create a bar plot with file names as labels and 60m values as heights."""
    if not files:
        print("No files provided.")
        return

    # Extract data from files
    data = []
    labels = []
    filenames = []
    for file_path in files:
        if os.path.isfile(file_path):
            value = extract_value(file_path)
            filename = os.path.basename(file_path)
            data.append(value)
            filenames.append(filename)
            # Extract the custom label from the filename
            label = extract_label_from_filename(filename)
            labels.append(label)
        else:
            print(f"Warning: {file_path} is not a valid file.")

    if not data:
        print("No valid data found.")
        return

    # Create the bar plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(data)), data, color=bar_color)

    # Add values on top of bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

    # Add a horizontal line at value 44
    plt.axhline(y=44, color='red', linestyle='--', alpha=0.7, label='Baseline (44)')

    # Add a line connecting the tops of all bars
    x_positions = [bar.get_x() + bar.get_width()/2 for bar in bars]
    heights = [bar.get_height() for bar in bars]
    plt.plot(x_positions, heights, marker='o', color='green', linestyle='-', linewidth=2, alpha=0.7)

    # Add legend
    plt.legend()

    # Customize the plot
    plt.xlabel('Temperatures')
    plt.ylabel('Total number of vulnerabilities detected')
    plt.title(f'{model} Fuzzing Results by Temperature')
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.ylim(0, 58)  # Set y-axis limit to 58
    plt.tight_layout()

    # Save the plot as PDF
    plt.savefig(output_file, format='pdf')
    print(f"Plot saved as {output_file}")

    # Don't show the plot (using Agg backend for non-interactive use)
    # plt.show()

def main():
    parser = argparse.ArgumentParser(description='Create a bar plot of 60m values from log files.')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--output', '-o', default='time_values_bar_plot.pdf', 
                        help='Output filename for the plot (PDF format)')
    parser.add_argument('--color', '-c', default='skyblue', 
                        help='Color for the bars (e.g., "#1f77b4" or color name)')

    parser.add_argument('--model', '-m', default='Blah', 
                        help='Model')

    args = parser.parse_args()

    # Handle color input - ensure hex color codes with quotes work properly
    color = args.color
    # If the color is a hex code that was quoted on the command line, strip quotes if present
    if color.startswith("'") and color.endswith("'"):
        color = color[1:-1]
    if color.startswith('"') and color.endswith('"'):
        color = color[1:-1]

    create_bar_plot(args.files, model = args.model, bar_color=color, output_file=args.output)

if __name__ == "__main__":
    main()