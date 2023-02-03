import csv
import pickle
import os.path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from rich.console import Console

# Initiate selenium browser
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

console = Console()
with console.status("[bold green]Processing...") as status:
    # Open linkedin jobs page and logged in
    console.log(f'[green]Login into linkedin account...')
    driver.get('https://linkedin.com/jobs')

    # check is already logged in into linkedin account
    if (os.path.exists('./cookies.txt')):
        # Read cookies
        cookies = pickle.load(open("cookies.txt", "rb"))

        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()
    else:
        email = driver.find_element(By.ID, 'session_key')
        password = driver.find_element(By.ID, 'session_password')
        sign_in = driver.find_element(By.CLASS_NAME, 'sign-in-form__submit-button')
        email.send_keys('email')
        password.send_keys('password')
        sign_in.click()

        # Retrieve cookies and store to cookies.txt
        pickle.dump(driver.get_cookies(), open('cookies.txt', 'wb'))

    # Wait till page fully loaded
    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "careers")))
    except TimeoutException as e:
        print("Wait Timed out")
        print(e)

    console.log(f'[green]Logged in! Start scraping jobs...')

    # Load html page with bs
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Scrape all data
    job_recomendation_el = soup.find('ul', class_='ph3')
    jobs_recomendation = job_recomendation_el.find_all('li', class_='jobs-job-board-list__item')

    # Loop through each job posting and extract the relevant information
    jobs = [['Company', 'Country', 'Job']]

    for job in jobs_recomendation:
        company = job.find('span', class_='job-card-container__primary-description').text
        country = job.find('li', class_='job-card-container__metadata-item').text
        title = job.find('a', class_='job-card-list__title').text

        jobs.append([company.strip(), country.strip(), title.strip()])
        
    # Save result to csv file
    with open('jobs-recomendation.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(jobs)
            console.log(f'[green]Saved to jobs-recomendation.csv')

console.log('[bold][red]Done!')

# done
driver.quit()