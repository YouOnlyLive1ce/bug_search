from slither import Slither
import os
import json

def save_analysis_output(repo_name, contract_name, function_name, output_content):
    base_dir = '/home/dima/atllm/d.nekrasov/project'
    output_dir = os.path.join(base_dir, "processed_repositories", repo_name, 'src', contract_name)

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
    slither = Slither(solidity_file)
    
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
                "Low-Level Calls": []
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

            save_analysis_output(repo_name, contract_name, function.name, output_content)

def main():
    repo_abs=os.getcwd()
    repo_name = repo_abs[repo_abs.rfind('/')+1:]
    # solidity_file_paths = find_solidity_files('./src')
    # print(solidity_file_paths)
    with open("scope.txt") as file:
        solidity_file_paths = [line.rstrip() for line in file]
    print(f"{len(solidity_file_paths)} in the scope")
    for solidity_file in solidity_file_paths:
        analyze_solidity_file(solidity_file, repo_name)

if __name__ == "__main__":
    main()