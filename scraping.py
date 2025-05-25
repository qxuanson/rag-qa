import requests
from bs4 import BeautifulSoup
import json
import urllib3
import os
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_article_links_from_page(driver):
    # Wait for the content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "post-item"))
    )
    
    # Get all article links
    article_links = []
    
    # Find all detail buttons
    detail_buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn.btn-default.btn-lighter")
    
    for button in detail_buttons:
        try:
            link = button.get_attribute('href')
            if link:
                article_links.append(link)
                print(f"Found article: {link}")
        except Exception as e:
            print(f"Error getting link from button: {e}")
            continue
    
    return article_links

def get_all_article_links(category_url):
    try:
        driver = setup_driver()
        print(f"Accessing category page: {category_url}")
        driver.get(category_url)
        
        all_article_links = []
        current_page = 1
        max_pages = 5  # Limit to 5 pages
        
        while current_page <= max_pages:
            print(f"\nProcessing page {current_page} of {max_pages}")
            # Get links from current page
            page_links = get_article_links_from_page(driver)
            all_article_links.extend(page_links)
            
            # Try to find next page button if not on last page
            if current_page < max_pages:
                try:
                    next_page = driver.find_element(By.CSS_SELECTOR, f"a.page.larger[href*='page/{current_page + 1}/']")
                    if next_page:
                        print(f"Moving to page {current_page + 1}")
                        next_page.click()
                        # Wait for the new page to load
                        time.sleep(2)  # Add a small delay to ensure page loads
                        current_page += 1
                    else:
                        print("No more pages available")
                        break
                except:
                    print("No more pages available")
                    break
            else:
                print("Reached maximum page limit")
                break
        
        driver.quit()
        return all_article_links
            
    except Exception as e:
        print(f"An error occurred while processing category page: {e}")
        if 'driver' in locals():
            driver.quit()
        return []

def crawl_website(url):
    try:
        # Send HTTP request with verify=False to bypass SSL verification
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First try to find content with class 'single-page-content'
        content = soup.find('article', class_='single-page-content')
        
        # If not found, try to find content with class 'single-post-content single-content'
        if not content:
            content = soup.find('article', class_='single-post-content single-content')
        
        if content:
            # Remove meta div if it exists
            meta_div = content.find('div', class_='item-meta single-post-meta content-pad')
            if meta_div:
                meta_div.decompose()
            
            # Get text while preserving line breaks and paragraphs
            text_content = ""
            for element in content.stripped_strings:
                text_content += element + "\n"
            
            return text_content
        else:
            print(f"Could not find content in either class in {url}")
            return None
            
    except requests.RequestException as e:
        print(f"Error occurred while fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        return None

def crawl_multiple_websites(urls):
    # Create a directory for storing results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"crawl_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a summary file
    summary_file = os.path.join(output_dir, "summary.txt")
    
    with open(summary_file, 'w', encoding='utf-8') as summary:
        for i, url in enumerate(urls, 1):
            print(f"\nProcessing website {i}/{len(urls)}: {url}")
            content = crawl_website(url)
            
            if content:
                # Create a filename from the URL
                filename = f"content_{i}.txt"
                filepath = os.path.join(output_dir, filename)
                
                # Save content to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write to summary
                summary.write(f"Website {i}: {url}\n")
                summary.write(f"Status: Success\n")
                summary.write(f"File: {filename}\n")
                summary.write("-" * 80 + "\n")
                
                print(f"Successfully saved content to {filepath}")
            else:
                # Write failure to summary
                summary.write(f"Website {i}: {url}\n")
                summary.write(f"Status: Failed\n")
                summary.write("-" * 80 + "\n")
    
    print(f"\nCrawling completed. Results saved in directory: {output_dir}")
    print(f"Summary file: {summary_file}")

def crawl_category(category_url):
    print(f"Getting article links from category: {category_url}")
    article_links = get_all_article_links(category_url)
    
    if article_links:
        print(f"Found {len(article_links)} articles in total")
        crawl_multiple_websites(article_links)
    else:
        print("No articles found in the category")

if __name__ == "__main__":
    # Category URL to crawl
    category_url = "https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/"
    
    # Crawl the category
    crawl_category(category_url)