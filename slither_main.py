import os
import shutil
import subprocess

script_name = "slither_analyzer_code.py"

base_dir = os.getcwd()
repositories_path = os.path.join(base_dir, 'repositories')

script_path = os.path.join(base_dir, script_name)

repo_paths=next(os.walk(repositories_path))[1]
for repo_name in repo_paths:
    repo_path = os.path.join(repositories_path, repo_name)
    os.chdir(repo_path)

    # Copy the script to the current repo directory
    destination_script_path = os.path.join(repo_path, script_name)
    shutil.copy(script_path, destination_script_path)
    print(f"Copied {script_name} to {repo_path}")

    print(f"Installing dependencies in {repo_path}")
    subprocess.run(["forge", "i"], check=True)  

    print(f"Running scipt in {repo_path}")
    subprocess.run(["python", script_name], check=True)  

    os.chdir(repositories_path)
