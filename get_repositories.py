from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests

with open('./audits_links.txt') as f:
    audits_links = f.readlines()

repo_links=[]
driver = webdriver.Firefox()
for audit_url in audits_links:
    driver.get(audit_url)
    time.sleep(3)
    audit_page_soup = BeautifulSoup(driver.page_source, "html.parser")
    a_tags = audit_page_soup.find_all("a", href=True)
    
    found=False
    available=True
    for a_tag in a_tags:
        # fix ..issues link, gist, .md, /audits
        if  ('github' in a_tag['href']) and not ('report' in a_tag['href']) and a_tag['href'][-11:]!='code-423n4/' and a_tag['href'][-9:]!='media-kit':
            repo_links.append(a_tag['href'])
            found=True
            print("github repository link found", a_tag['href'])
            break

    if found==False:
        # check if details are available
        for h2_tag in audit_page_soup.find_all("h2"):
            if 'not available' in h2_tag.text:
                print("audit details are not available", audit_url)
                available=False
                break

    if available and not found:
        print("!Audit github repository link did not match any template", audit_url)

with open("repositories_links.txt", mode="w") as repositories_links:
    repositories_links.write("\n".join(repo_links) + "\n")