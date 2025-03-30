#!/usr/bin/env python3
"""
Script to analyze two bug-finding results files and create a Venn diagram
showing the overlap between fully and partly found contracts.

Usage:
    python venn_diagram.py <file1> <file2>
"""

import sys
import re
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import numpy as np

def parse_file(file_path):
    """
    Parse the input file and extract bug information.
    
    Returns:
        tuple: (fully_found, partly_found, never_found) sets of bug IDs
    """
    fully_found = set()
    partly_found = set()
    never_found = set()
    
    bug_pattern = re.compile(r'(Fully|Partly|Never) found IntegerBug from (\d{4}-\d{5})')
    
    with open(file_path, 'r') as f:
        for line in f:
            match = bug_pattern.search(line)
            if match:
                status, bug_id = match.groups()
                if status == 'Fully':
                    fully_found.add(bug_id)
                elif status == 'Partly':
                    partly_found.add(bug_id)
                elif status == 'Never':
                    never_found.add(bug_id)
    
    return fully_found, partly_found, never_found

def create_venn_diagram(file1_results, file2_results, file1_name, file2_name):
    """
    Create a Venn diagram showing the overlap between the two result files.
    
    Args:
        file1_results: Tuple of (fully_found, partly_found, never_found) sets from file 1
        file2_results: Tuple of (fully_found, partly_found, never_found) sets from file 2
        file1_name: Name of the first file for labeling
        file2_name: Name of the second file for labeling
    """
    fully1, partly1, never1 = file1_results
    fully2, partly2, never2 = file2_results
    
    # Calculate all bugs found in each file (fully or partly)
    found1 = fully1.union(partly1)
    found2 = fully2.union(partly2)
    
    # Calculate total bugs from both files
    all_bugs = fully1.union(partly1).union(never1).union(fully2).union(partly2).union(never2)
    
    # Main Venn diagram (overall found bugs)
    plt.figure(figsize=(12, 8))
    
    # First subplot: Overall found bugs
    plt.subplot(2, 2, 1)
    venn = venn2([found1, found2], 
                 set_labels=(file1_name, file2_name))
    
    # Set custom colors
    if venn:
        venn.get_patch_by_id('10').set_color('skyblue')
        venn.get_patch_by_id('01').set_color('lightgreen')
        venn.get_patch_by_id('11').set_color('lightgray')
    
    plt.title(f'All Found Bugs (Fully or Partly)\nTotal Unique Bugs: {len(all_bugs)}')
    
    # Second subplot: Fully found bugs
    plt.subplot(2, 2, 2)
    venn2([fully1, fully2], 
          set_labels=(file1_name, file2_name))
    plt.title('Fully Found Bugs')
    
    # Third subplot: Partly found bugs
    plt.subplot(2, 2, 3)
    venn2([partly1, partly2], 
          set_labels=(file1_name, file2_name))
    plt.title('Partly Found Bugs')
    
    # Fourth subplot: Never found bugs
    plt.subplot(2, 2, 4)
    venn2([never1, never2], 
          set_labels=(file1_name, file2_name))
    plt.title('Never Found Bugs')
    
    plt.tight_layout()
    
    # Add a detailed summary as text
    plt.figtext(0.05, 0.01, f"""
    Summary:
    - Total unique bugs: {len(all_bugs)}
    - Found in {file1_name} only: {len(found1 - found2)}
    - Found in {file2_name} only: {len(found2 - found1)}
    - Found in both: {len(found1.intersection(found2))}
    - Never found in either: {len(never1.intersection(never2))}
    
    {file1_name} breakdown:
    - Fully found: {len(fully1)} ({len(fully1)/len(all_bugs)*100:.1f}%)
    - Partly found: {len(partly1)} ({len(partly1)/len(all_bugs)*100:.1f}%)
    - Never found: {len(never1)} ({len(never1)/len(all_bugs)*100:.1f}%)
    
    {file2_name} breakdown:
    - Fully found: {len(fully2)} ({len(fully2)/len(all_bugs)*100:.1f}%)
    - Partly found: {len(partly2)} ({len(partly2)/len(all_bugs)*100:.1f}%)
    - Never found: {len(never2)} ({len(never2)/len(all_bugs)*100:.1f}%)
    """, fontsize=10)
    
    plt.subplots_adjust(bottom=0.35)
    plt.savefig('contract_bugs_venn_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main function to process files and create the Venn diagram."""
    if len(sys.argv) != 3:
        print("Usage: python venn_diagram.py <file1> <file2>")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    # Use filenames without extensions for labels
    file1_name = file1_path.split('/')[-1].split('.')[0]
    file2_name = file2_path.split('/')[-1].split('.')[0]
    
    # Parse files
    file1_results = parse_file(file1_path)
    file2_results = parse_file(file2_path)
    
    # Create Venn diagram
    create_venn_diagram(file1_results, file2_results, file1_name, file2_name)
    
    # Print summary statistics and detailed differences
    fully1, partly1, never1 = file1_results
    fully2, partly2, never2 = file2_results
    
    # Calculate found bugs (fully or partly)
    found1 = fully1.union(partly1)
    found2 = fully2.union(partly2)
    
    # Get bugs only found in one file and not the other
    only_in_file1 = found1 - found2
    only_in_file2 = found2 - found1
    
    print(f"File: {file1_path}")
    print(f"  Fully found: {len(fully1)}")
    print(f"  Partly found: {len(partly1)}")
    print(f"  Never found: {len(never1)}")
    print(f"  Total: {len(fully1) + len(partly1) + len(never1)}")
    print()
    
    print(f"File: {file2_path}")
    print(f"  Fully found: {len(fully2)}")
    print(f"  Partly found: {len(partly2)}")
    print(f"  Never found: {len(never2)}")
    print(f"  Total: {len(fully2) + len(partly2) + len(never2)}")
    print()
    
    # Print bugs found only in file1
    print(f"Bugs found only in {file1_name} ({len(only_in_file1)}):")
    if only_in_file1:
        sorted_bugs = sorted(only_in_file1)
        for bug_id in sorted_bugs:
            status = "Fully" if bug_id in fully1 else "Partly"
            print(f"  {status} found: {bug_id}")
    else:
        print("  None")
    print()
    
    # Print bugs found only in file2
    print(f"Bugs found only in {file2_name} ({len(only_in_file2)}):")
    if only_in_file2:
        sorted_bugs = sorted(only_in_file2)
        for bug_id in sorted_bugs:
            status = "Fully" if bug_id in fully2 else "Partly"
            print(f"  {status} found: {bug_id}")
    else:
        print("  None")

if __name__ == "__main__":
    main()
