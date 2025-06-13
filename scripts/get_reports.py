from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver

# For linux
options = webdriver.FirefoxOptions()
serv = webdriver.FirefoxService( executable_path='/snap/bin/geckodriver' )
driver = webdriver.Firefox(options=options,service=serv)
url = 'https://code4rena.com/audits'
driver.get(url)

# Collect audit links from 9 pages
c4_audit_links = []
try:
    for page_num in range(9):
        time.sleep(5) 
        soup = BeautifulSoup(driver.page_source, "html.parser")
        audit_tile_list = soup.find("span", id="completed-audits").find_next_sibling("div", class_="audit-tile-list")
        
        # Find all audit tiles
        tiles_container = audit_tile_list.find("div", class_="audit-tile-list__tiles")
        containers = tiles_container.find_all("div", class_="audit-tile variant-extended")

        for container in containers:
            link = container.find("a", class_="audit-tile__link")
            if link and link.has_attr('href'):
                c4_audit_links.append('https://code4rena.com' + link['href'])

        # Scroll down to make sure pagination button is in view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        print(f"Page {page_num + 1} processed, {len(c4_audit_links)} links collected")
        print(c4_audit_links[-1])
        # TODO: automate with selenium
        print("!waiting for !manual! button to click")
        time.sleep(5)
finally:
    driver.quit()

print(f"Found {len(c4_audit_links)} audit links")
with open("./data/audits_links.txt", mode="w") as auditfile:
    auditfile.write("\n".join(c4_audit_links) + "\n")

# Load existing data if file exists
import os
import json
audits_info = []
json_file = "./data/audits_info.json"
if os.path.exists(json_file):
    with open(json_file, "r") as f:
        audits_info = json.load(f)

# Get existing audit URLs to avoid duplicates
existing_audits = {item["audit_link"] for item in audits_info}

report_links=[] 
for audit_url in c4_audit_links:
    if audit_url in existing_audits:
        continue
        
    audit_data = {
        "audit_link": audit_url,
        "report_link": None,
        "repo_link":None,
        "repo_local_path":None,
    }

    response = requests.get(audit_url)
    audit_page_soup = BeautifulSoup(response.content, "html.parser")
    found=False
    available=True
    
    for a_tag in audit_page_soup.find_all("a", href=True):
        if  ('report' in a_tag['href'] and 'github' in a_tag['href']) or 'reports/202' in a_tag['href']:
            report_links.append('https://code4rena.com'+a_tag['href'])
            audit_data["report_link"] = 'https://code4rena.com' + a_tag['href']
            found=True
            # print("github report link found", audit_url)
            break

    if found==False:
        # check if details are available
        for h2_tag in audit_page_soup.find_all("h2"):
            if 'not available' in h2_tag.text:
                # print("audit details are not available", audit_url)
                available=False
                break
    audits_info.append(audit_data)

    # TODO: Details buttom with selenium - todo. +25 reports
    
    # TODO: Check if 'mitigated issues' are already listed, save to folder with issues. + ?? issues with code
    if available and not found:
        print("!Audit report link did not match any template", audit_url)

with open(json_file, "w") as f:
    json.dump(audits_info, f, indent=2)
print("reports found", len(report_links), "out of ", len(c4_audit_links)) #341 out of 392 parsed succesfuly
with open("./data/reports_links.txt", mode="w") as reports_links:
    reports_links.write("\n".join(report_links) + "\n")