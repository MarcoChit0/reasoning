import os 
import os
import shutil
def reorganize_directory_structure():
    base_dir = "./data/experiments"
    moves = []  # List to store (old_path, new_path) tuples

    # First, collect all the file paths and their new destinations
    for exp in os.listdir(base_dir):
        exp_path = os.path.join(base_dir, exp)
        if not os.path.isdir(exp_path):
            continue

        for model in os.listdir(exp_path):
            model_path = os.path.join(exp_path, model)
            if not os.path.isdir(model_path):
                continue

            for template in os.listdir(model_path):
                template_path = os.path.join(model_path, template)
                if not os.path.isdir(template_path):
                    continue

                for domain in os.listdir(template_path):
                    domain_path = os.path.join(template_path, domain)
                    if not os.path.isdir(domain_path):
                        continue

                    for instance_type in os.listdir(domain_path):
                        instance_type_path = os.path.join(domain_path, instance_type)
                        if not os.path.isdir(instance_type_path):
                            continue

                        for instance in os.listdir(instance_type_path):
                            if not instance.endswith(".log"):
                                continue

                            # Old path
                            old_path = os.path.join(instance_type_path, instance)
                            
                            # New path
                            new_dir = os.path.join(base_dir, exp, domain, instance_type, model, template)
                            new_path = os.path.join(new_dir, instance)
                            
                            moves.append((old_path, new_path, new_dir))

    print(f"Found {len(moves)} files to reorganize.")
    
    # Now do the moving
    for old_path, new_path, new_dir in moves:
        # Ensure new directory exists
        os.makedirs(new_dir, exist_ok=True)
        
        # Copy the file to the new location
        shutil.copy2(old_path, new_path)
        print(f"Copied: {old_path} -> {new_path}")

    print(f"Total files processed: {len(moves)}")
    print("All files have been copied to the new structure.")
    print("After verifying the new structure, you may want to delete the old structure.")

# Execute the function
reorganize_directory_structure()
                        