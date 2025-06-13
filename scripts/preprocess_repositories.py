import os

# Define the source and destination folders
destination_dir = './processed_repositories'

source_dir = './repositories'
for root, _, files in os.walk(source_dir):
    repository_dir=root
    # Walk through the source directory
    for root, _, files in os.walk(repository_dir):
        for file in files:
            if file.endswith('.sol'):
                # Construct full file paths
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                destination_path = os.path.join(destination_dir, relative_path)
                
                # Ensure the destination directory exists
                os.makedirs(destination_path, exist_ok=True)
                
                # Read .sol file and write to .txt file
                with open(source_path, 'r', encoding='utf-8') as sol_file:
                    content = sol_file.read()
                txt_file_path = os.path.join(destination_path, file.replace('.sol', '.txt'))
                with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(content)

print("Conversion complete!")
# TODO: external, override keywords in embeddings
# TODO: normalization from paper