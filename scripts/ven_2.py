import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3, venn3_circles
import numpy as np
import re
import sys
from collections import defaultdict
import matplotlib.patches as patches
import matplotlib.path as path

def parse_file(file_path):
    """Parse the input file and extract bug status information."""
    bug_status = {"found": [], "never": []}
    
    with open(file_path, 'r') as f:
        for line in f:
            if "Fully found IntegerBug" in line or "Partly found IntegerBug" in line:
                bug_id = re.search(r'IntegerBug from (\d+-\d+)', line).group(1)
                bug_status["found"].append(bug_id)
            elif "Never found IntegerBug" in line:
                bug_id = re.search(r'IntegerBug from (\d+-\d+)', line).group(1)
                bug_status["never"].append(bug_id)
    
    return bug_status

def create_two_ellipse_venn(sets, set_labels, output_file="venn_diagram.png"):
    """Create a simple two-ellipse Venn diagram from the given sets."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define colors with some transparency
    colors = ['rgba(255, 0, 0, 0.5)', 'rgba(0, 0, 255, 0.5)']
    
    # Convert rgba to matplotlib format
    colors_matplotlib = [
        (1, 0, 0, 0.5),
        (0, 0, 1, 0.5)
    ]
    
    # Define ellipse parameters for the two sets
    # Parameters: (center_x, center_y, width, height, angle)
    ellipses = [
        (0.4, 0.5, 0.5, 0.4, 0),
        (0.6, 0.5, 0.5, 0.4, 0)
    ]
    
    # Create ellipses for each set
    patches_list = []
    for i, (cx, cy, w, h, angle) in enumerate(ellipses):
        ellipse = patches.Ellipse((cx, cy), w, h, angle=angle, 
                                  fc=colors_matplotlib[i], ec='black', lw=1)
        ax.add_patch(ellipse)
        patches_list.append(ellipse)
        
        # Add set labels
        label_angle = np.radians(angle)
        label_x = cx + np.cos(label_angle) * (w/2 - 0.05)
        label_y = cy + np.sin(label_angle) * (h/2 - 0.05)
        ax.text(label_x, label_y, set_labels[i], fontsize=14, fontweight='bold',
                ha='center', va='center')
    
    # Find all possible regions
    import itertools
    regions = {}
    
    # Convert sets to sets (if they aren't already)
    sets = [set(s) for s in sets]
    
    # Get all possible combinations of sets
    for r in range(1, len(sets) + 1):
        for combo in itertools.combinations(range(len(sets)), r):
            # Find elements in this specific region (intersection of included sets, minus union of excluded sets)
            included_sets = [sets[i] for i in combo]
            excluded_sets = [sets[i] for i in range(len(sets)) if i not in combo]
            
            region_set = set.intersection(*included_sets)
            if excluded_sets:
                region_set -= set.union(*excluded_sets)
            
            if region_set:
                regions[combo] = region_set
    
    # Draw counts in each region
    for combo, elements in regions.items():
        # Calculate approximate center of this region
        x, y = 0, 0
        for i in combo:
            cx, cy = ellipses[i][0], ellipses[i][1]
            x += cx
            y += cy
        x /= len(combo)
        y /= len(combo)
        
        # Add a small offset to avoid overlapping
        if len(combo) > 1:
            # Apply a slight offset to the label position
            offset = 0.05 * (len(combo) - 1)
            if 0 in combo and 1 in combo:
                y -= offset
            if 2 in combo and 3 in combo:
                y += offset
        
        # Add count text
        count = len(elements)
        ax.text(x, y, str(count), fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
    
    # Add legend for each set
    for i, label in enumerate(set_labels):
        ax.plot([], [], color=colors_matplotlib[i], marker='o', markersize=10, label=label)
    
    # Set limits and remove axis
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Add title and legend
    plt.title('Venn Diagram of Contract Bug Detection', fontsize=16)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=4)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Venn diagram saved as {output_file}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <file1> <file2> <output_file>")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    output_file = sys.argv[3]
    
    # Parse both files
    file1_status = parse_file(file1_path)
    file2_status = parse_file(file2_path)
    
    # Create sets for each category and each file
    set1_found = set(file1_status["found"])
    set2_found = set(file2_status["found"])
    
    # Create the two ellipse sets
    sets = [set1_found, set2_found]
    set_labels = ["File 1 Found", "File 2 Found"]
    
    # Create the Venn diagram
    create_two_ellipse_venn(sets, set_labels, output_file)
    
    # Calculate some useful metrics
    only_in_file1 = set1_found - set2_found
    only_in_file2 = set2_found - set1_found
    in_both = set1_found.intersection(set2_found)
    
    # Print summary statistics
    print(f"File 1 - Found: {len(set1_found)}, Never found: {len(file1_status['never'])}")
    print(f"File 2 - Found: {len(set2_found)}, Never found: {len(file2_status['never'])}")
    print(f"Bugs found only in File 1: {len(only_in_file1)}")
    print(f"Bugs found only in File 2: {len(only_in_file2)}")
    print(f"Bugs found in both files: {len(in_both)}")
    
    # Find bugs that were never found in both files
    never_found_both = set(file1_status["never"]).intersection(set(file2_status["never"]))
    print(f"Bugs never found in both files: {len(never_found_both)}")
    if never_found_both:
        print("Bug IDs:", ", ".join(sorted(never_found_both)))

if __name__ == "__main__":
    main()
