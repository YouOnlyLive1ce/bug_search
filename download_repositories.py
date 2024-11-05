import os
import git
import re

root_dir = "./repositories"
with open('./repositories_links.txt') as f:
    repo_links = f.readlines()

for link in repo_links[:]:
    link = link.strip()
    repo_name = link.split("/")[-1].replace(".git", "")
    repo_name = re.sub(r'[\\/:"*?<>|]', "_", repo_name).strip()
    
    repo_path = os.path.join(root_dir, repo_name)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_name} into {repo_path}...")
        try:
            git.Repo.clone_from(link, repo_path)
        except:
            print("!Cloning error")
    else:
        print(f"Repository {repo_name} already exists at {repo_path}.")