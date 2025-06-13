from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
import orjson

with open('./data/audits_info.json','r') as f:
    audits_info = orjson.loads(f.read())

repo_links=[]
# For linux
options = webdriver.FirefoxOptions()
serv = webdriver.FirefoxService( executable_path='/snap/bin/geckodriver' )
driver = webdriver.Firefox(options=options,service=serv)

for audit in audits_info:
    if audit.get('repo_link')!=None:
        continue
    driver.get(audit.get('audit_link'))
    time.sleep(3)
    audit_page_soup = BeautifulSoup(driver.page_source, "html.parser")
    a_tags = audit_page_soup.find_all("a", href=True)
    
    found=False
    available=True
    for a_tag in a_tags:
        # fix ..issues link, gist, .md, /audits
        if  ('github' in a_tag['href']) and not ('report' in a_tag['href']) and a_tag['href'][-11:]!='code-423n4/' and a_tag['href'][-9:]!='media-kit':
            audit['repo_link']=a_tag['href']
            found=True
            print("github repository link found", a_tag['href'])
            break

    if found==False:
        # check if details are available
        for h2_tag in audit_page_soup.find_all("h2"):
            if 'not available' in h2_tag.text:
                print("audit details are not available", audit.get('audit_link'))
                available=False
                break

    if available and not found:
        print("!Audit github repository link did not match any template", audit.get('audit_link'))

import json
# with open("./data/repositories_links.txt", "w") as f:
#     f.write("\n".join(repo_links) + "\n")
with open('./data/audits_info.json', 'w') as f:
    json.dump(audits_info,f,indent=2)