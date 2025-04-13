import re
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib_venn
from matplotlib_venn import venn3, venn3_circles, venn2, venn2_circles
import numpy as np
from itertools import combinations
import plotly.graph_objects as go
import pandas as pd
import os

def parse_file(filename):
    """Parse a file and return a dictionary of found contracts."""
    found_contracts = set()
    
    with open(filename, 'r') as f:
        for line in f:
            # Extract the contract ID and status
            match = re.search(r'(Fully|Partly) found IntegerBug from (\d+-\d+)', line)
            if match:
                contract_id = match.group(2)
                found_contracts.add(contract_id)
                
    return found_contracts

def get_exclusive_contracts(method_sets):
    """Get contracts found exclusively by each method."""
    exclusive_contracts = {}
    
    for method, contracts in method_sets.items():
        # Get all contracts from other methods
        other_contracts = set()
        for other_method, other_set in method_sets.items():
            if other_method != method:
                other_contracts.update(other_set)
        
        # Exclusive contracts are those not found by any other method
        exclusive_contracts[method] = contracts - other_contracts
        
    return exclusive_contracts

def create_sankey_diagram(method_sets, filename="sankey_diagram.html"):
    """Create a Sankey diagram showing how contracts flow between methods."""
    # Create dataframe for Sankey diagram
    source = []
    target = []
    value = []
    
    method_keys = list(method_sets.keys())
    method_ids = {name: i for i, name in enumerate(method_keys)}
    
    # Add nodes for each method and for "Contracts"
    labels = ["Contracts"] + method_keys
    
    # For each method, add a link from "Contracts" to that method
    contracts_node_id = 0
    for method, contracts in method_sets.items():
        method_id = method_ids[method] + 1  # +1 because "Contracts" is at index 0
        source.append(contracts_node_id)
        target.append(method_id)
        value.append(len(contracts))
    
    # For overlapping contracts, create additional nodes and links
    overlap_node_id = len(labels)
    
    # Calculate all possible overlaps (each region is a unique combination of sets)
    for k in range(2, len(method_keys) + 1):
        for combo in combinations(method_keys, k):
            # Only process if there's an actual overlap
            combo_set = set.intersection(*[method_sets[name] for name in combo])
            if combo_set:
                combo_name = " ∩ ".join(combo)
                labels.append(combo_name)
                
                # Add links from each method in the combo to this overlap
                for method in combo:
                    method_id = method_ids[method] + 1
                    source.append(method_id)
                    target.append(overlap_node_id)
                    # Divide by number of methods to avoid counting multiple times
                    value.append(len(combo_set) / len(combo))
                
                overlap_node_id += 1
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])
    
    fig.update_layout(
        title_text=f"Contract Flow between Fuzzing Methods",
        font_size=10
    )
    
    # Save the Sankey diagram
    fig.write_html(filename)
    print(f"Sankey diagram saved as {filename}")
    
    return fig

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} method1.txt method2.txt [method3.txt method4.txt ...]")
        print("Note: At least 2 files are required.")
        sys.exit(1)
    
    # Get file names from command line arguments
    method_files = sys.argv[1:]
    
    # Limit to maximum 4 files for the four-ellipse Venn diagram
    if len(method_files) > 4:
        print("Warning: More than 4 files provided. Only the first 4 will be used for the Venn diagram.")
        method_files = method_files[:4]
    
    # Get base filenames without path and extension for labels
    method_names = [os.path.splitext(os.path.basename(f))[0] for f in method_files]
    
    # Parse each file
    method_sets = {}
    for i, method_file in enumerate(method_files):
        method_sets[method_names[i]] = parse_file(method_file)
    
    # Get contracts found exclusively by each method
    exclusive_contracts = get_exclusive_contracts(method_sets)
    
    # Create a custom four-ellipse Venn diagram
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Sets are already defined in method_sets dictionary
    sets = method_sets
    
    # Get the method names for labels
    method_keys = list(sets.keys())
    
    # Calculate all possible regions (each region is a unique combination of sets)
    regions = {}
    for k in range(1, 5):
        for combo in combinations(method_keys, k):
            combo_name = '+'.join(combo)  # Use more readable label format
            # Intersection of all sets in the combo
            current_sets = [sets[name] for name in combo]
            intersection = set.intersection(*current_sets)
            # Exclude elements that are in more sets than just this combo
            for other_combo in combinations(method_keys, k+1):
                if all(name in other_combo for name in combo):
                    other_sets = [sets[name] for name in other_combo]
                    other_intersection = set.intersection(*other_sets)
                    intersection -= other_intersection
            regions[combo_name] = intersection
    
    # Count the number of elements in each region
    region_counts = {name: len(elements) for name, elements in regions.items()}
    
    # Generate custom Venn diagram
    # We'll use custom ellipses for this
    
    from matplotlib.patches import Ellipse
    
    # Define ellipse properties based on number of methods
    colors = ['r', 'g', 'b', 'y']  # Colors for each method
    
    # Define positions based on number of methods
    num_methods = len(method_keys)
    
    if num_methods == 2:
        positions = [
            {'center': (0.35, 0.5), 'width': 0.4, 'height': 0.7, 'angle': 0},
            {'center': (0.65, 0.5), 'width': 0.4, 'height': 0.7, 'angle': 0}
        ]
    elif num_methods == 3:
        positions = [
            {'center': (0.33, 0.6), 'width': 0.5, 'height': 0.5, 'angle': 0},
            {'center': (0.67, 0.6), 'width': 0.5, 'height': 0.5, 'angle': 0},
            {'center': (0.5, 0.35), 'width': 0.5, 'height': 0.5, 'angle': 0}
        ]
    else:  # 4 methods
        positions = [
            {'center': (0.35, 0.5), 'width': 0.4, 'height': 0.7, 'angle': 40},
            {'center': (0.65, 0.5), 'width': 0.4, 'height': 0.7, 'angle': -40},
            {'center': (0.5, 0.35), 'width': 0.7, 'height': 0.4, 'angle': 0},
            {'center': (0.5, 0.65), 'width': 0.7, 'height': 0.4, 'angle': 0}
        ]
    
    ellipses = {}
    for i, method_name in enumerate(method_keys):
        ellipses[method_name] = {
            **positions[i],
            'color': colors[i],
            'alpha': 0.3
        }
    
    # Draw ellipses
    for name, props in ellipses.items():
        e = Ellipse(
            xy=props['center'], 
            width=props['width'], 
            height=props['height'],
            angle=props['angle'],
            color=props['color'],
            alpha=props['alpha']
        )
        ax.add_patch(e)
        
        # Add set labels with the actual method names
        plt.text(
            props['center'][0], 
            props['center'][1], 
            name, 
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12,
            fontweight='bold'
        )
    
    # Define a function to dynamically create label positions based on method names and count
    def get_label_position(region_name):
        # Split the region name to get individual method names
        methods = region_name.split('+')
        num_methods = len(method_keys)
        
        # If it's a single method, position it near the edge of its ellipse
        if len(methods) == 1:
            method = methods[0]
            center = ellipses[method]['center']
            # Shift a bit from the center
            offset = 0.15
            idx = method_keys.index(method)
            
            if num_methods == 2:
                # For 2 methods, simple left/right positioning
                if idx == 0:
                    return (center[0] - offset, center[1])
                else:
                    return (center[0] + offset, center[1])
            elif num_methods == 3:
                # For 3 methods triangular positioning
                if idx == 0:
                    return (center[0] - offset, center[1])
                elif idx == 1:
                    return (center[0] + offset, center[1])
                else:
                    return (center[0], center[1] - offset)
            else:  # 4 methods
                if idx == 0:
                    return (center[0] - offset, center[1])
                elif idx == 1:
                    return (center[0] + offset, center[1])
                elif idx == 2:
                    return (center[0], center[1] - offset)
                else:
                    return (center[0], center[1] + offset)
        
        # For intersections, calculate average positions
        x_sum = sum(ellipses[method]['center'][0] for method in methods)
        y_sum = sum(ellipses[method]['center'][1] for method in methods)
        avg_pos = (x_sum / len(methods), y_sum / len(methods))
        
        # Small adjustments based on number of methods in the diagram
        if len(methods) == 2:
            # For 2-method intersection in a 2-method diagram
            if num_methods == 2:
                return (0.5, 0.5)  # Center
            else:
                return avg_pos
        elif len(methods) == 3:
            # For 3-method intersection in a 3 or 4-method diagram
            return (avg_pos[0], avg_pos[1])
        else:  # All methods (3 or 4)
            return (0.5, 0.5)  # Center of the diagram
    
    # Generate label positions dynamically
    label_positions = {region: get_label_position(region) for region in regions.keys()}
    
    # Add counts for each region
    for region, count in region_counts.items():
        if count > 0:  # Only show non-empty regions
            pos = label_positions.get(region, (0.5, 0.5))  # Default position if not defined
            plt.text(
                pos[0], 
                pos[1], 
                str(count), 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=14,
                fontweight='bold'
            )
    
    # Set plot properties
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title and legend
    # Set title based on number of methods
    num_methods = len(method_keys)
    plt.title(f'{num_methods}-way Venn Diagram of Contracts Found by Different Fuzzing Methods', fontsize=18)
    
    # Create legend for the fuzzing methods
    handles = [plt.Rectangle((0,0),1,1, color=ellipses[name]['color'], alpha=ellipses[name]['alpha']) for name in method_keys]
    plt.legend(handles, method_keys, loc='upper right', fontsize=10)
    
    # Calculate total found contracts across all methods
    total_found = len(set.union(*method_sets.values()))
    
    # Add annotation for total contracts found
    plt.figtext(0.5, 0.02, f"Total unique contracts found: {total_found}", ha="center", fontsize=14)
    
    # Save with filename based on number of methods
    num_methods = len(method_keys)
    plt.savefig(f'{num_methods}_way_venn_diagram.png', dpi=300, bbox_inches='tight')
    
    # Print some statistics
    print(f"Total unique contracts found across all methods: {total_found}")
    
    # Print breakdown by fuzzing method
    print("\nBreakdown by fuzzing method:")
    for method, contracts in method_sets.items():
        print(f"{method}: {len(contracts)}")
    
    # Print exclusive contracts by method
    print("\nContracts found EXCLUSIVELY by each method:")
    for method, contracts in exclusive_contracts.items():
        print(f"{method}: {len(contracts)}")
        if contracts:
            print(f"  Contracts: {', '.join(sorted(contracts))}")
        else:
            print("  No exclusive contracts found")
    
    # Print breakdown by intersection regions
    print("\nBreakdown by intersection regions:")
    for region, contracts in sorted(regions.items()):
        if len(contracts) > 0:
            print(f"{region}: {len(contracts)}")
    
    # Create and save Sankey diagram
    create_sankey_diagram(method_sets)
    
    plt.show()

if __name__ == "__main__":
    main()