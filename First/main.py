# Required libraries for web scraping and data handling
import requests  # For making HTTP requests to the website
from bs4 import BeautifulSoup  # For parsing HTML content
import csv  # For writing data to CSV files


def scrape_uci_datasets():
    # Base URL of the UCI Machine Learning Repository
    base_url = "https://archive.ics.uci.edu/datasets"

    # Define the column headers for the CSV file
    headers = [
        "Dataset Name", "Donated Date", "Description",
        "Dataset Characteristics", "Subject Area", "Associated Tasks",
        "Feature Type", "Instances", "Features"
    ]

    # Initialize empty list to store all scraped dataset information
    data = []

    def scrape_dataset_details(dataset_url):
        # Function to scrape detailed information from individual dataset pages
        response = requests.get(dataset_url)
        soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

        # Extract dataset name from the page header
        dataset_name = soup.find(
            'h1', class_='text-3xl font-semibold text-primary-content')
        dataset_name = dataset_name.text.strip() if dataset_name else "N/A"

        # Extract donation date
        donated_date = soup.find('h2', class_='text-sm text-primary-content')
        donated_date = donated_date.text.strip().replace(
            'Donated on ', '') if donated_date else "N/A"

        # Extract dataset description
        description = soup.find('p', class_='svelte-17wf9gp')
        description = description.text.strip() if description else "N/A"

        # Find all detail sections containing dataset information
        details = soup.find_all('div', class_='col-span-4')

        # Extract various dataset characteristics with error handling
        # If a detail is not found, return "N/A"
        dataset_characteristics = details[0].find('p').text.strip() if len(
            details) > 0 else "N/A"
        subject_area = details[1].find('p').text.strip() if len(
            details) > 1 else "N/A"
        associated_tasks = details[2].find('p').text.strip() if len(
            details) > 2 else "N/A"
        feature_type = details[3].find('p').text.strip() if len(
            details) > 3 else "N/A"
        instances = details[4].find('p').text.strip() if len(
            details) > 4 else "N/A"
        features = details[5].find('p').text.strip() if len(
            details) > 5 else "N/A"

        # Return all extracted information as a list
        return [
            dataset_name, donated_date, description, dataset_characteristics,
            subject_area, associated_tasks, feature_type, instances, features
        ]

    def scrape_datasets(page_url):
        # Function to scrape all dataset links from a single page
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all dataset links on the page
        dataset_list = soup.find_all(
            'a', class_='link-hover link text-xl font-semibold')

        # Exit if no datasets are found on the page
        if not dataset_list:
            print("No dataset links found")
            return

        # Iterate through each dataset link and scrape its details
        for dataset in dataset_list:
            dataset_link = "https://archive.ics.uci.edu" + dataset['href']
            print(f"Scraping details for {dataset.text.strip()}...")
            dataset_details = scrape_dataset_details(dataset_link)
            data.append(dataset_details)

    # Implement pagination to scrape multiple pages
    skip = 0  # Starting page offset
    take = 10  # Number of items per page
    while True:
        # Construct URL with pagination parameters
        page_url = f"https://archive.ics.uci.edu/datasets?skip={skip}&take={take}&sort=desc&orderBy=NumHits&search="
        print(f"Scraping page: {page_url}")
        initial_data_count = len(data)
        scrape_datasets(page_url)
        # Break the loop if no new data was added (reached the last page)
        if len(data) == initial_data_count: 
            break
        skip += take

    # Write all collected data to a CSV file
    with open('uci_datasets.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write column headers
        writer.writerows(data)    # Write all dataset information

    print("Scraping complete. Data saved to 'uci_datasets.csv'.")


# Execute the main scraping function
scrape_uci_datasets()