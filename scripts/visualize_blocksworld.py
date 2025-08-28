import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import argparse
import sys
from typing import List, Tuple, Dict

def parse_state(pddl_content: str, state_name: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Parses a PDDL string to find 'on-table' and 'on' predicates for a given state.
    This version robustly finds the content of a block by looking for its start
    and end markers relative to other blocks.

    Args:
        pddl_content: The full string content of the PDDL file.
        state_name: The name of the state to parse (e.g., 'init' or 'goal').

    Returns:
        A tuple containing:
        - A list of blocks that are on the table.
        - A list of (block, block_below) tuples representing 'on' relationships.
    """
    try:
        # --- FIX: Implement a robust block-finding logic ---
        # Find the starting position of the desired block (e.g., "(:init")
        start_pattern = re.compile(rf"\s*\(:{state_name}")
        start_match = start_pattern.search(pddl_content)
        if not start_match:
            return [], []
        
        # The content starts right after the block declaration
        content_start_index = start_match.end()

        # To find the end of our block, we look for the beginning of the *next* block.
        # The next block will also start with a '(:'. We search for it *after* our block starts.
        next_block_pattern = re.compile(r"\s*\(:")
        next_match = next_block_pattern.search(pddl_content, pos=content_start_index)
        
        content_end_index = -1
        if next_match:
            # If we found another block, our content ends where that one begins.
            content_end_index = next_match.start()
        else:
            # If no other block is found, this is the last block in the definition.
            # We can assume its content runs until the last closing parenthesis.
            content_end_index = pddl_content.rfind(')')

        # Extract the content of the block
        if content_end_index > content_start_index:
            state_content = pddl_content[content_start_index:content_end_index]
        else:
            # Fallback in case of parsing error
            state_content = pddl_content[content_start_index:]

        # Find all (on-table <block>) predicates within the captured content
        on_table_blocks = re.findall(r'\(\s*on-table\s+([a-zA-Z0-9-]+)\s*\)', state_content)
        
        # Find all (on <block1> <block2>) predicates within the captured content
        on_relations = re.findall(r'\(\s*on\s+([a-zA-Z0-9-]+)\s+([a-zA-Z0-9-]+)\s*\)', state_content)

        return on_table_blocks, on_relations
    except Exception as e:
        print(f"Error parsing state '{state_name}': {e}")
        return [], []


def build_stacks(on_table_blocks: List[str], on_relations: List[Tuple[str, str]]) -> List[List[str]]:
    """
    Constructs stacks of blocks from parsed relationships. Handles partial
    stacks (e.g., in goal states) that may not have a block on the table.

    Args:
        on_table_blocks: A list of blocks that form the base of stacks.
        on_relations: A list of (block, block_below) tuples.

    Returns:
        A list of lists, where each inner list represents a stack of blocks
        from bottom to top.
    """
    if not on_table_blocks and not on_relations:
        return []

    # Create lookup maps for efficient building
    on_map = {below: on_top for on_top, below in on_relations} # {block_below: block_on_top}
    is_on_top_of_something = {on_top for on_top, _ in on_relations}

    stacks = []
    placed_blocks = set()

    # Find bases of "floating" stacks for goal states.
    # A block is a base of a stack if it's underneath another block
    # but is not itself on top of any other block.
    all_bottom_blocks = set(on_map.keys())
    floating_bases = all_bottom_blocks - is_on_top_of_something
    
    # Combine table blocks and floating bases. This ensures we find all stack bases,
    # even if they are not explicitly on the table.
    all_potential_bases = on_table_blocks + sorted(list(floating_bases))

    for base_block in all_potential_bases:
        # Skip if this block has already been placed in another stack
        if base_block in placed_blocks:
            continue

        # Build the stack upwards from the base
        stack = [base_block]
        placed_blocks.add(base_block)
        current_block = base_block
        
        while current_block in on_map:
            top_block = on_map[current_block]
            
            # Cycle Detection
            if top_block in stack:
                print(
                    f"Error: Detected a cycle involving '{top_block}'. Aborting stack.",
                    file=sys.stderr
                )
                break
            
            if top_block in placed_blocks:
                break # This block is part of a structure we've already built

            stack.append(top_block)
            placed_blocks.add(top_block)
            current_block = top_block
            
        stacks.append(stack)
        
    return stacks


def visualize_state(ax, stacks: List[List[str]], title: str, block_colors: Dict[str, Tuple[float, float, float]]):
    """
    Draws the blocks configuration on a given matplotlib axes.

    Args:
        ax: The matplotlib axes object to draw on.
        stacks: The list of stacks to visualize.
        title: The title for the subplot.
        block_colors: A dictionary mapping block names to RGB color tuples.
    """
    ax.set_title(title, fontsize=16)
    
    # Define block dimensions
    block_width = 1.0
    block_height = 1.0
    
    # Draw the table line
    ax.axhline(0, color='black', linewidth=3)
    
    if not stacks:
        ax.text(0.5, 0.5, "No state to display", ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')
        return

    # Draw each block in each stack
    for i, stack in enumerate(stacks):
        for j, block_id in enumerate(stack):
            x_pos = i * (block_width + 0.5)
            y_pos = j * block_height
            
            # Get color for the block
            color = block_colors.get(block_id, (0.5, 0.5, 0.5)) # Default to gray
            
            # Create and add the block rectangle
            rect = patches.Rectangle(
                (x_pos, y_pos), block_width, block_height,
                edgecolor='black', facecolor=color, linewidth=1.5
            )
            ax.add_patch(rect)
            
            # Add the block ID text
            ax.text(
                x_pos + block_width / 2,
                y_pos + block_height / 2,
                block_id,
                ha='center', va='center', fontsize=12, color='white', weight='bold'
            )

    # Set plot limits and appearance
    max_height = max((len(s) for s in stacks), default=0)
    ax.set_xlim(-0.5, len(stacks) * (block_width + 0.5) - 0.5)
    ax.set_ylim(-0.5, max_height + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off') # Hide the axes for a cleaner look


def main():
    """
    Main function to parse command-line arguments and run the visualization.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Visualize Blocksworld PDDL instance files.")
    parser.add_argument("pddl_file", type=str, help="Path to the PDDL instance file.")
    args = parser.parse_args()

    try:
        with open(args.pddl_file, 'r') as f:
            pddl_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{args.pddl_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Extract all unique block names to assign consistent colors
    all_objects = re.findall(r'[bB][\w-]*', pddl_content)
    unique_blocks = sorted(list(set(all_objects)))
    
    # Generate a color map for consistent block colors across plots
    if unique_blocks:
        colors = plt.cm.viridis([i/len(unique_blocks) for i in range(len(unique_blocks))])
        block_colors = {block: color for block, color in zip(unique_blocks, colors)}
    else:
        block_colors = {}

    # Parse initial and goal states
    init_on_table, init_on_relations = parse_state(pddl_content, 'init')
    goal_on_table, goal_on_relations = parse_state(pddl_content, 'goal')

    # Build the stack structures
    init_stacks = build_stacks(init_on_table, init_on_relations)
    goal_stacks = build_stacks(goal_on_table, goal_on_relations)

    # Create the visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Blocksworld Instance Visualization', fontsize=20)
    
    visualize_state(ax1, init_stacks, 'Initial State', block_colors)
    visualize_state(ax2, goal_stacks, 'Goal State', block_colors)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


if __name__ == "__main__":
    main()
