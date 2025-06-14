from slither import Slither
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
    project_root = os.path.abspath(os.path.dirname(__file__))
    # left part - from file, right part - library
    remappings = (f"openzeppelin-contracts/={project_root}/node_modules/@openzeppelin/", 
                  f"Solady/={project_root}/node_modules/solady/src/",
                  f"@openzeppelin/={project_root}/node_modules/@openzeppelin/")
    # print(remappings)
    slither = Slither(solidity_file, solc_remaps=remappings)
    
    contract_name = os.path.basename(solidity_file).replace(".sol", "")
    contracts = slither.get_contract_from_name(contract_name=contract_name)
    
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
                    #Contract,HighLevelCall
                    # print(dir(call[1]))
                    # print(dir(call[0]))
                    # contract
                    # print('high',type(call[0].name))
                    output_content["High-Level Calls"].append((call[0].name))

            for call in function.internal_calls:
                if call:
                    # print(dir(call))
                    if hasattr(call,'function_name'):
                        # print('int1',type(call.function_name))
                        output_content["Internal Calls"].append(call.function_name)
                    elif hasattr(call,'function'):
                        # print('int2',type(call.function.name))
                        output_content["Internal Calls"].append(call.function.name)
                    else:
                        print('internal',dir(call.function))

            for call in function.library_calls:
                if call:
                    if hasattr(call,'name'):
                        print('lib1',type(call.name))
                        output_content["Library Calls"].append(call.name)
                    elif hasattr(call,'function_name'):
                        # print('lib2',type(call.function_name))
                        output_content["Library Calls"].append(call.function_name.value)
                    else:
                        print('library',dir(call))
                        
            for call in function.low_level_calls:
                if call:
                    print('low',type(call[0].name))
                    output_content["Low-Level Calls"].append(call[0].name)

            output_content['Code']=function.source_mapping.content

            save_analysis_output(repo_name, contract_name, function.name, output_content)

def main():
    repo_abs=os.getcwd()
    repo_name = repo_abs[repo_abs.rfind('/')+1:]

    # Dependencies
    try:
        if os.path.isfile("package.json"):
            # with open("package.json", "r") as f:
            #     package_json = json.load(f)
            # if "packageManager" in package_json:
            #     print("pnpm required")
            #     if "pnpm" in package_json["packageManager"]:
            #         subprocess.run(["pnpm", "install"], check=True)
            # else:
            subprocess.run(["npm","install"], check=True)
            if not (os.path.isdir("node_modules/@openzeppelin") or os.path.isdir("node_modules/solady")):
                print("Installing OpenZeppelin/Solady...")
                subprocess.run(["npm", "install", "@openzeppelin/contracts", "solady"], check=True)
        elif os.path.isfile("foundry.toml"):
            subprocess.run(["forge", "i"], check=True) 
    except Exception as e:
        print(e)
        print("!Dependencies install error")
        exit(0)

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
    
    print("solc-select")
    subprocess.run(["solc-select","install",solidity_version], check=True)
    subprocess.run(["solc-select","use",solidity_version], check=True)

    # Analyze each solidity file
    print(f"{len(solidity_file_paths)} files in the scope")
    slither_fail=0
    for solidity_file in solidity_file_paths:
        print(solidity_file)
        try:
            analyze_solidity_file(solidity_file, repo_name)
        except Exception as e:
            print(e)
            slither_fail+=1
    print(f"{len(solidity_file_paths)-slither_fail} analyzed successfully")

if __name__ == "__main__":
    main()

# curl -o- -L https://yarnpkg.com/install.sh | bash
# curl -L https://foundry.paradigm.xyz | bash
# foundryup
# source /home/usr/.bashrc