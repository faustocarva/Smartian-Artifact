#!/usr/bin/env python3
from email.mime import base
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

def extract_values_from_file(file_path):
    """
    Extract the values at '60m:' from the given file.
    Returns two values, one from each section separated by the delimiter.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Split the content into two parts based on the delimiter
            parts = content.split('-----------------------------------')
            
            values = []
            for part in parts:
                if part.strip():  # Only process non-empty parts
                    # Find the 60m value using a regular expression
                    match = re.search(r'60m: (\d+\.\d+)', part)
                    if match:
                        values.append(float(match.group(1)))
                    else:
                        print(f"Warning: No '60m:' value found in section of {file_path}")
                        values.append(0.0)
            
            # Ensure we always return two values (pad with 0 if needed)
            while len(values) < 2:
                values.append(0.0)
                print(f"Warning: Missing section in {file_path}, using 0.0 as placeholder")
                
            return values
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return [0.0, 0.0]

def extract_label_from_filename(filename):
    """Extract the text after the last underscore in the filename."""
    return filename.split('_')[-1] if '_' in filename else filename    

def create_side_by_side_bar_plots(files, baseline1, baseline2,  models, bar_colors=['#1f77b4', '#ff7f0e'], output_file='time_values_bar_plot.pdf'):
    """Create side-by-side bar plots for two models with file names as labels and 60m values as heights."""
    if not files:
        print("No files provided.")
        return
    
    if len(models) != 2:
        print("Exactly two models must be provided.")
        return

    # Extract data from files
    data_model1 = []
    data_model2 = []
    labels = []
    filenames = []
    
    for file_path in files:
        if os.path.isfile(file_path):
            model1_value, model2_value = extract_values_from_file(file_path)
            filename = os.path.basename(file_path)
            
            data_model1.append(model1_value)
            data_model2.append(model2_value)
            filenames.append(filename)
            
            # Extract the custom label from the filename
            label = extract_label_from_filename(filename)
            labels.append(label)
        else:
            print(f"Warning: {file_path} is not a valid file.")

    if not data_model1 or not data_model2:
        print("No valid data found.")
        return

    # Create the figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Model 1 Plot
    x = range(len(data_model1))
    bars1 = ax1.bar(x, data_model1, color=bar_colors[0])
    
    # Add values on top of bars for Model 1
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=11)
    
    #ax1.axhline(y=44, color='red', linestyle='--', alpha=0.7, label='Baseline (44)')
    ax1.axhline(y=float(baseline1), color='#555555', linestyle='--', alpha=0.9)
    ax1.axhline(y=float(baseline2), color='#555555', linestyle='-', alpha=0.9)
    
    # Add a line connecting the tops of all bars for Model 1
    x_positions = [bar.get_x() + bar.get_width()/2 for bar in bars1]
    heights = [bar.get_height() for bar in bars1]
    #ax1.plot(x_positions, heights, marker='o', color='green', linestyle='-', linewidth=2, alpha=0.7)
    ax1.plot(x_positions, heights, marker='o', color='#ffc107', linestyle='-', linewidth=4, alpha=0.7)
    
    # Customize Model 1 plot
    ax1.set_xlabel('Temperature')
    ax1.set_ylabel('Total # of bugs detected')    
    ax1.set_title(f'{models[0]} fuzzing results by Temperature', fontsize=16)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, ha='right')
    ax1.set_ylim(0, 58)
    ax1.set_yticks([float(baseline1)] + list(ax1.get_yticks()))
    ax1.set_yticks([float(baseline2)] + list(ax1.get_yticks()))    
    
    # Model 2 Plot
    bars2 = ax2.bar(x, data_model2, color=bar_colors[1])
    
    # Add values on top of bars for Model 2
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=11)
    
    # Add a horizontal line at value 44 for Model 2
    #ax2.axhline(y=44, color='red', linestyle='--', alpha=0.7, label='Baseline (44)')
    ax2.axhline(y=float(baseline1), color='#555555', linestyle='--', alpha=0.9)
    ax2.axhline(y=float(baseline2), color='#555555', linestyle='-', alpha=0.9)    
    
    # Add a line connecting the tops of all bars for Model 2
    x_positions = [bar.get_x() + bar.get_width()/2 for bar in bars2]
    heights = [bar.get_height() for bar in bars2]
    #ax2.plot(x_positions, heights, marker='o', color='green', linestyle='-', linewidth=2, alpha=0.7)
    ax2.plot(x_positions, heights, marker='o', color='#ffc107', linestyle='-', linewidth=4, alpha=0.7)
    
    # Customize Model 2 plot
    ax2.set_xlabel('Temperature')
    #ax2.set_ylabel('Number of vulnerabilities detected')
    ax2.set_title(f'{models[1]} fuzzing results by Temperature', fontsize=16)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, ha='right')
    ax2.set_ylim(0, 58)
    ax2.set_yticks([float(baseline1)] + list(ax1.get_yticks()))    
    ax2.set_yticks([float(baseline2)] + list(ax1.get_yticks()))        
    
    plt.tight_layout()
    
    # Save the plot as PDF
    #plt.savefig(output_file, format='pdf')
    plt.savefig(output_file)    
    print(f"Plot saved as {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Create side-by-side bar plots of 60m values from log files with two data sections.')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--output', '-o', default='time_values_bar_plot.pdf', 
                        help='Output filename for the plot (PDF format)')
    parser.add_argument('--colors', '-c', default='skyblue,orange', 
                        help='Colors for the bars (comma-separated, e.g., "skyblue,orange" or "#1f77b4,#ff7f0e")')
    parser.add_argument('--models', '-m', default='Model1,Model2', 
                        help='Model names (comma-separated, e.g., "Claude,GPT4")')
    parser.add_argument('--baseline1', '-b1', default='44', 
                        help='')
    parser.add_argument('--baseline2', '-b2', default='52.8', 
                        help='')
    


    args = parser.parse_args()

    # Parse model names
    models = args.models.split(',')
    if len(models) != 2:
        print("Error: You must specify exactly two model names separated by a comma.")
        return

    # Parse colors
    colors = args.colors.split(',')
    if len(colors) != 2:
        print("Warning: You must specify exactly two colors separated by a comma. Using default colors.")
        colors = ['skyblue', 'orange']
    
    # Clean up colors (remove quotes if present)
    for i in range(len(colors)):
        color = colors[i]
        if (color.startswith("'") and color.endswith("'")) or (color.startswith('"') and color.endswith('"')):
            colors[i] = color[1:-1]

    create_side_by_side_bar_plots(args.files, args.baseline1, args.baseline2, models=models, bar_colors=colors, output_file=args.output)

if __name__ == "__main__":
    main()