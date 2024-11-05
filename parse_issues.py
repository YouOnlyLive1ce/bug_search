from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import os
# from reports_links,parse github link and download github repositories

driver = webdriver.Chrome()
with open('./project/reports_links.txt') as f:
    reports_links = f.readlines()

for report_link in reports_links:
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
                folder_path = f"./issues_reports/reports_links/{report_link[30:-1]}"
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