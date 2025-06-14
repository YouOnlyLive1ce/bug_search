import os
import shutil
import subprocess

script_name = "slither_analyzer_code.py"

base_dir = os.getcwd()
repositories_path = os.path.join(base_dir, 'data/repositories')
processed_repositories_path=os.path.join(base_dir, 'data/processed_repositories')

script_path = os.path.join(base_dir, 'scripts', script_name)

repo_paths=next(os.walk(repositories_path))[1]
fail_analyze=0
for repo_name in repo_paths:
    # if repository was already processed, skip
    if os.path.isdir(os.path.join(processed_repositories_path,repo_name)):
        print(repo_name, "was already successfully processed, deleting")
        repository_path=os.path.join(repositories_path,repo_name)
        # subprocess.run(["rm","-rf",repository_path], check=True)
        continue

    repo_path = os.path.join(repositories_path, repo_name)
    os.chdir(repo_path)
    # Copy the script to the current repo directory
    destination_script_path = os.path.join(repo_path, script_name)
    shutil.copy(script_path, destination_script_path)
    print(f"Copied {script_name} to {repo_path}") 
    print(f"Running scipt in {repo_path}")

    try:
        subprocess.run(["python", script_name], check=True)
        repository_path=os.path.join(repositories_path,repo_name)
        print(f"Delete original repository {repository_path}")
        # subprocess.run(["rm","-rf",repository_path], check=True)
    except:
        fail_analyze+=1
    
    os.chdir(repositories_path)
print(fail_analyze)