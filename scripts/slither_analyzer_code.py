from slither import slither
import os
import json
import subprocess

def save_analysis_output(repo_name, contract_name, function_name, output_content):
    repo_path = os.getcwd()
    base_path=repo_path[0:repo_path.rfind('/',0,repo_path.rfind('/'))]
    output_dir = os.path.join(base_path, "processed_repositories", repo_name, 'src', contract_name)

    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, f"{function_name}.txt")
    with open(output_file_path, "w") as file:
        json.dump(output_content, file, indent=4)

def find_solidity_files(repo_path):
    solidity_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".sol"):
                solidity_files.append(os.path.join(root, file))
    return solidity_files

def analyze_solidity_file(solidity_file, repo_name):
    slither = slither(solidity_file)
    
    contract_name = os.path.basename(solidity_file).replace(".sol", "")
    contracts = slither.get_contract_from_name(contract_name)
    
    for contract in contracts:
        for function in contract.functions_declared:
            output_content = {
                "Function": function.name,
                "File": function.source_mapping.filename.relative,
                "Parent Contracts": [],
                "High-Level Calls": [],
                "Internal Calls": [],
                "Library Calls": [],
                "Low-Level Calls": [],
                "Code":""
            }

            for parent_contract in contract.inheritance:
                output_content["Parent Contracts"].append(parent_contract.source_mapping.filename.relative)

            for call in function.high_level_calls:
                if call:
                    output_content["High-Level Calls"].append((call[1].name, call[0].name))

            for call in function.internal_calls:
                if call:
                    output_content["Internal Calls"].append(call.name)

            for call in function.library_calls:
                if call:
                    output_content["Library Calls"].append(f"{call[1].name}.{call[0].name}")

            for call in function.low_level_calls:
                if call:
                    output_content["Low-Level Calls"].append(f"{call[1]}.{call[0].name}")

            output_content['Code']=function.source_mapping.content

            save_analysis_output(repo_name, contract_name, function.name, output_content)

def main():
    repo_abs=os.getcwd()
    repo_name = repo_abs[repo_abs.rfind('/')+1:]

    # Dependencies
    try:
        if os.path.isfile("package.json"):
            subprocess.run(["yarn","install"], check=True)
        elif os.path.isfile("foundry.toml"):
            subprocess.run(["forge", "i"], check=True) 
    except:
        print("!Dependencies install error")

    # Reducing scope to not include dependecies
    solidity_file_paths=[]
    if os.path.isfile("scope.txt"):
        with open("scope.txt") as file:
            solidity_file_paths = [line.rstrip() for line in file]
    elif os.path.isdir('src'):
        solidity_file_paths = find_solidity_files('./src')
    elif os.path.isdir('contracts'):
        solidity_file_paths = find_solidity_files('./contracts')
    if len(solidity_file_paths)==0:
        print("!Failed to find solidity files")
        return

    # Installing suitable solc compiler
    with open(solidity_file_paths[0]) as f:
        code=f.read()
    index1=code.find('pragma solidity ')
    index2=code.find('\n',index1)
    solidity_version = code[index1 + 16:index2].strip()
    solidity_version = solidity_version.split('//')[0].strip()   # Remove comments
    solidity_version = solidity_version.split('<')[0].strip()
    solidity_version = solidity_version.replace('^', '').strip() # Remove ^
    solidity_version = solidity_version.replace(';', '').strip() # Remove ;
    solidity_version = solidity_version.replace('=', '').strip() # Remove =
    solidity_version = solidity_version.replace('>', '').strip() # Remove >
    
    subprocess.run(["solc-select","install",solidity_version], check=True)
    subprocess.run(["solc-select","use",solidity_version], check=True)

    # Analyze each solidity file
    print(f"{len(solidity_file_paths)} files in the scope")
    slither_fail=0
    for solidity_file in solidity_file_paths:
        try:
            analyze_solidity_file(solidity_file, repo_name)
        except:
            slither_fail+=1
    print(f"{len(solidity_file_paths)-slither_fail} analyzed successfully")

if __name__ == "__main__":
    main()

# curl -o- -L https://yarnpkg.com/install.sh | bash
# curl -L https://foundry.paradigm.xyz | bash
# foundryup
# source /home/usr/.bashrc