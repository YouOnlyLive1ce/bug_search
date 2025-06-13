import os
import git
import re
import orjson

base_dir = "./data/repositories"
with open('./data/audits_info.json','r') as f:
    audits_info = orjson.loads(f.read())

for audit in audits_info[:5]:
    if not audit['repo_link']:
        continue
    link = audit['repo_link'].strip()
    repo_name = link.split("/")[-1].replace(".git", "")
    repo_name = re.sub(r'[\\/:"*?<>|]', "_", repo_name).strip()
    
    repo_path = os.path.join(base_dir, repo_name)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_name} into {repo_path}...")
        try:
            git.Repo.clone_from(link, repo_path)
        except:
            print("!Cloning error")
    else:
        print(f"Repository {repo_name} already exists at {repo_path}.")