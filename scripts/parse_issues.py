from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import os
import json
# from list of github/codearena pages, extract issues in folder with structure:
# issues\
#        link\
#            High\
#                H-01-code    <-buggy code
#                H-01-explain <-human explanation
#                H-02-code
#                H-03-explain
#                ...
#            Medium\
#                M-01-code
#                ...
#            Low\
#                ...
#            NC\
#                ...
#         link\
# Embedded code snippets with context will be used in rag to find similar bugs

# For linux
options = webdriver.FirefoxOptions()
serv = webdriver.FirefoxService( executable_path='/snap/bin/geckodriver' )
driver = webdriver.Firefox(options=options,service=serv)

with open('./data/audits_info.json', 'r') as file:
    reports_links = json.load(file)
new_reports_links=[]

# add report_local_path
for report_dict in reports_links:
    report_link=report_dict['report_link']
    print(f"parsing {report_link}")
    if report_link==None:
        continue
    folder_path = f"./data/reports/{report_link[30:]}"
    # if os.path.isdir(folder_path):
    #     print(f"Already parsed {folder_path}")
    #     continue
    driver.get(report_link)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # codearena report issue page 
    id_pattern = re.compile(r"^(h-|0-|m-|l-|[0-9]{2}-)")
    h2_tags = soup.find_all("h2", id=id_pattern)
    
    # TODO: github report issue page handler (+10 reports)

    p_texts = []
    pre_texts = []

    # If the <h2> is found, we can now iterate over its next siblings to capture <p> and <pre> tags
    for h2_tag in h2_tags:
        
        for sibling in h2_tag.find_next_siblings():
            
            # If next tag is new issue, save current
            if sibling.name == "h2":
                os.makedirs(folder_path, exist_ok=True)

                # Explain file contains human readable explanation
                with open(f"{folder_path}/{h2_tag.get('id')[:4]}_explain.txt", mode="w") as reports_links:
                    text='\n'.join(p_texts)+'\n'
                    text=text.encode("ascii", errors="ignore").decode()
                    reports_links.write(text)
                
                # Code file contains code of the function with imports
                with open(f"{folder_path}/{h2_tag.get('id')[:4]}_code.txt", mode="w") as reports_links:
                    text='\n'.join(pre_texts)+'\n'
                    text=text.encode("ascii", errors="ignore").decode()
                    reports_links.write(text)
                p_texts=[]
                pre_texts=[]
                break
            
            # Capture tag text
            if sibling.name == "p":
                p_texts.append(sibling.get_text())
            elif sibling.name == "pre":
                pre_texts.append(sibling.get_text())
                
    print(f"{len(h2_tags)} issues parsed from {report_link}")
    if len(h2_tags)==0:
        print(f"!page did not match template {report_link}")
    else:
        report_dict['report_local_path']="./"+folder_path[7:]
        new_reports_links.append(report_dict)

with open('./data/audits_info_updated.json', 'w') as file:
    json.dump(new_reports_links, file, indent=2)