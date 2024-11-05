from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests

driver = webdriver.Chrome()
url = 'https://code4rena.com/audits'
driver.get(url)

# Collect audit links from 8 pages
c4_audit_links = []
try:
    for page_num in range(8):
        time.sleep(5) 
        soup = BeautifulSoup(driver.page_source, "html.parser")
        completed_audits_section = soup.find("section", id="completed-audits")
        containers = completed_audits_section.find_all("div", class_="c4tilewrapper tile--dark")

        for container in containers:
            link = container.find("a", class_="contest-redirect")
            if link and link.has_attr('href'):
                c4_audit_links.append('https://code4rena.com' + link['href'])

        # Scroll down to make sure pagination button is in view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        print(f"Page {page_num + 1} processed, {len(c4_audit_links)} links collected")
        print(c4_audit_links[-1])
        # TODO: automate with selenium
        print("!waiting for !manual! button to click")
        time.sleep(15)
finally:
    driver.quit()

print(f"Found {len(c4_audit_links)} audit links")
with open("audits_links.txt", mode="w") as auditfile:
    auditfile.write("\n".join(c4_audit_links) + "\n")

report_links=[] 
for audit_url in c4_audit_links:
    response = requests.get(audit_url)
    audit_page_soup = BeautifulSoup(response.content, "html.parser")
    found=False
    available=True
    
    for a_tag in audit_page_soup.find_all("a", href=True):
        if  ('report' in a_tag['href'] and 'github' in a_tag['href']) or 'reports/202' in a_tag['href']:
            report_links.append('https://code4rena.com'+a_tag['href'])
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
    
    # TODO: Details buttom with selenium - todo. +25 reports
    
    # TODO: Check if 'mitigated issues' are already listed, save to folder with issues. + ?? issues with code
    if available and not found:
        print("!Audit report link did not match any template", audit_url)

print("reports found", len(report_links), "out of ", len(c4_audit_links)) #331 out of 380 parsed succesfuly
with open("reports_links.txt", mode="w") as reports_links:
    reports_links.write("\n".join(report_links) + "\n")