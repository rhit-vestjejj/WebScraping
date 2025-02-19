import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

import filter

# Redirect Chrome logging to devnull
os.environ['WDM_LOG_LEVEL'] = '0'

# Setup Chrome options with complete silence
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--silent')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

# First navigate to login page
driver.get('https://simplify.jobs/auth/login')

# Wait for login form and enter credentials
try:
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    
    email_input.send_keys("vestjejj@rose-hulman.edu")
    password_input.send_keys("")
    
    # Find and click login button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    
    # Wait for login to complete and add debugging
    print("Attempting login...")
    login_button.click()
    time.sleep(20)  # Increased wait time
    print("Login attempted")
    
    # Now navigate to the jobs page
    print("Navigating to jobs page...")
    driver.get('https://simplify.jobs/jobs?experience=Internship&category=Software%20Engineering&jobId=fffda04f-8c19-4758-8ed6-844ba95a6ea9')
    time.sleep(5)  # Increased wait time
    print("On jobs page")

    # Print page source to debug
    print("Current URL:", driver.current_url)
    
    time.sleep(10)

    # To find selectors:
    # 1. Right click on the scrollable container and Inspect
    # 2. Copy the selector for the scrollable area

    # Add a variable for the scroller container selector (update its value as needed)
    SCROLLER_SELECTOR = "#page-scroll-container > div > div.m-auto.mt-0.flex.w-full.flex-col.px-4.sm\:px-8 > div.h-navscreen.flex.flex-col.gap-2.rounded-lg.bg-gray-50 > div.my-2.flex.overflow-hidden.rounded-lg.border.border-gray-100.bg-white > div > div > div > div.flex.h-screen.flex-col.gap-4.overflow-y-auto.p-4"

    print("Looking for scroll container...")
    scroll_container = driver.find_element(By.CSS_SELECTOR, SCROLLER_SELECTOR)
    print("Found scroll container")

    print("Beginning container scroll process...")
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        time.sleep(2)  # wait for content to load
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        print(f"Scrolled container from {last_height} to {new_height}")
        if new_height == last_height:
            print("Container reached bottom")
            break
        last_height = new_height
        
    print("Container scrolling complete")
    time.sleep(2)

    print("Looking for job links...")
    num_jobs = len(scroll_container.find_elements(By.CSS_SELECTOR, "[data-testid='job-card']"))
    print(f"Found {num_jobs} job links")
    
    jobs_data = []
    for i in range(num_jobs):
        try:
            # Re-fetch job card to avoid stale element issues
            job_links = scroll_container.find_elements(By.CSS_SELECTOR, "[data-testid='job-card']")
            job = job_links[i]
            
            print(f"\nProcessing job {i+1}/{num_jobs}")
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            time.sleep(1)
            try:
                job.click()
            except Exception:
                print("Click intercepted, performing JS click.")
                driver.execute_script("arguments[0].click();", job)
            time.sleep(1)  # giving a little extra time after click

            # Now parse the updated page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Replace fixed details-card id with one matching any id starting with "details-card-"
            base_selector = "[id^='details-card-'] > div > div > div.flex.flex-col.gap-4.lg\\:w-1\\/2.xl\\:w-2\\/5"
            
            job_title_elem = soup.select_one(f"{base_selector} > div.pb-2 > h1")
            if job_title_elem:
                job_title = job_title_elem.text.strip()
            else:
                job_title = "N/A"
                print("Warning: job_title element not found")
            
            #details-card-ffa96602-9741-4ace-b3a6-ec238d59f7e9 > div > div > div.flex.flex-col.gap-4.lg\:w-1\/2.xl\:w-2\/5 > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(3) > div.flex.items-center.gap-2 > p

            #details-card-ffa96602-9741-4ace-b3a6-ec238d59f7e9 > div > div > div.flex.flex-col.gap-4.lg\:w-1\/2.xl\:w-2\/5 > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(2) > div > p
            
            #details-card-fed2d034-619b-4778-b079-0f5fa3c7a918 > div > div > div.flex.flex-col.gap-4.lg\:w-1\/2.xl\:w-2\/5 > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(3) > div.flex.items-center.gap-2

            #details-card-fed2d034-619b-4778-b079-0f5fa3c7a918 > div > div > div.flex.flex-col.gap-4.lg\:w-1\/2.xl\:w-2\/5 > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(3) > div.flex.items-center.gap-2

            place_elem = soup.select_one(f"{base_selector} > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(2) > div.flex.items-center.gap-2")
            if place_elem:
                place = place_elem.text.strip()
            else:
                place = "N/A"
                print("Warning: place element not found")

            if place == "Company Historically Provides H1B Sponsorship" or place == "No H1B Sponsorship":
                place_elem = soup.select_one(f"{base_selector} > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(3) > div.flex.items-center.gap-2")
                if place_elem:
                    place = place_elem.text.strip()
                else:
                    place = "N/A"
                    print("Warning: place element not found")
            
            #details-card-483abaa7-1de4-4701-976f-89e941f9f997 > div > div > div.flex.flex-col.gap-4.lg\:w-1\/2.xl\:w-2\/5 > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div.text-left.text-secondary-400

            if place == "Category":
                place_elem = soup.select_one(f"{base_selector} > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div:nth-child(1) > div.flex.items-center.gap-2")
                if place_elem:
                    place = place_elem.text.strip()
                else:
                    place = "N/A"
                    print("Warning: place element not found")

            
            employer_elem = soup.select_one(f"{base_selector} > div:nth-child(3) > div > div")
            if employer_elem:
                employer = employer_elem.text.strip()
            else:
                employer = "N/A"
                print("Warning: employer element not found")
            
            qualifications_elems = soup.select(f"{base_selector} > div.flex.flex-col.gap-5.border-b.border-gray-100.pb-4 > div.flex.flex-col.justify-start.gap-4 > div.mb-3.ml-6.flex.flex-wrap.justify-start.gap-3.text-sm > div")
            if qualifications_elems:
                qualifications = [elem.text.strip() for elem in qualifications_elems if elem.text.strip()]
            else:
                qualifications = []
                print("Warning: qualifications elements not found")
            
            skills_elems = soup.select(f"{base_selector} > div.flex.flex-col.justify-start.gap-4 > div.mb-3.ml-6.flex.flex-wrap.justify-start.gap-3.text-sm > div")
            if skills_elems:
                skills = [elem.text.strip() for elem in skills_elems if elem.text.strip()]
            else:
                skills = []
                print("Warning: skills elements not found")

            job_url = driver.current_url
            print(f"Found job: {job_title} at {employer}")
            
            jobs_data.append({
                "Job Title": job_title,
                "Place": place,
                "Employer": employer,
                "Qualifications": qualifications,
                "Skills": skills,
                "Job Link": job_url
            })

            
            print("Clicking back arrow to return to job list...")
            # Replace fixed back_button with a dynamic selector matching any overview modal's button

            back_selector = "[id^='overview-'] > div.sticky.left-0.top-0.z-10.flex.w-full.rounded-t-2xl.border-b.border-gray-100.bg-white.p-2.px-4.sm\:flex.sm\:rounded-t-2xl.sm\:p-4.sm\:px-12 > div.flex.w-full.justify-between > div:nth-child(1) > button"
            back_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, back_selector))
            )
            back_button.click()
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, back_selector))
                )
            except Exception as wait_err:
                print("Modal did not close in time, continuing.")
            time.sleep(2)

        except Exception as e:
            print(f"Error processing job: {e}")
            continue

    # Correct file extension to .csv
    with open("simplify_jobs.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Job Title", "Place", "Employer", "Qualifications", "Skills", "Job Link"])
        writer.writeheader()
        for job in jobs_data:
            # Convert qualifications list to a comma-separated string
            job["Qualifications"] = ", ".join(job["Qualifications"]) if isinstance(job["Qualifications"], list) else job["Qualifications"]
            writer.writerow(job)

finally:
    driver.quit()

print("Done with scanning...")
time.sleep(10)
print("Moving to filter to states and remote...")

filter.filter_main()