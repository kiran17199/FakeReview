from time import sleep
from random import random
import pandas as pd
import requests
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.parse as urlparse
from urllib.parse import parse_qs

BASE_URL = 'https://www.flipkart.com/'
SEARCH_QUERY = "headphones"
TOP_N_PRODUCTS = 10
REVIEW_PAGES_TO_SCRAPE_FROM_PER_PRODUCT = 100 #10 Reviews exist per page

SAMPLE_URL = "https://www.flipkart.com/boat-rockerz-400-bluetooth-headset/product-reviews/itm14d0416b87d55?pid=ACCEJZXYKSG2T9GS&lid=LSTACCEJZXYKSG2T9GSVY4ZIC&marketplace=FLIPKART&page=1"
r = requests.get(SAMPLE_URL)    
soup = BeautifulSoup(r.content, 'html.parser') 
print(soup.prettify()[:500])

rows = soup.find_all('div',attrs={'class':'col _2wzgFH K0kLPL'})
print(f"Count of rows(reviews):{len(rows)}\n\n\n")
# iteration over all blocks
for row in rows:
    # Print a sample row(review html block)
    # print(f"row:\n{row} \n\n")
    
    # finding all rows within the block
    sub_row = row.find_all('div',attrs={'class':'row'})
        
    # extracting text from 1st and 2nd row
    rating = sub_row[0].find('div').text
    print(f"rating:{rating} \n\n")
    
    summary = sub_row[0].find('p').text
    print(f"summary:{summary} \n\n")
    
    review = sub_row[1].find_all('div')[2].text
    print(f"review:{review} \n\n")
    
    location = sub_row[3].find('p',attrs={'class':'_2mcZGG'}).find_all('span')[1].text
    location = "".join(location.split(",")[1:]).strip()
    print(f"location:{location} \n\n")
    
    date = sub_row[3].find_all('p',attrs={'class':'_2sc7ZR'})[1].text
    print(f"date:{date} \n\n")
    
    
    sub_row_2 = row.find_all('div',attrs={'class':'_1e9_Zu'})[0].find_all('span',attrs={'class':'_3c3Px5'})
    
    upvotes = sub_row_2[0].text
    print(f"upvotes:{upvotes} \n\n")
    
    downvotes = sub_row_2[1].text
    print(f"downvotes:{downvotes} \n\n")
    
    break

def get_popular_product_s_titles_and_urls(search_query : str, popular_products_count_limit : int = None):
    
    search_url = f"{BASE_URL}search?q={search_query}&sort=popularity"
    search_response = requests.get(search_url)
    
    # Pause the loop for 1-3 seconds to simulate natural setting not overwhelm the server with back to back requests without any pause
    # sleep(randint(1,3))
    
    search_html_soup = BeautifulSoup(search_response.content, 'html.parser')
    search_results_products = search_html_soup.find_all('div',attrs={'class':'_4ddWXP'})
    
    product_titles, product_urls = [],[]
    
    product_count = 0
    for product in tqdm(search_results_products, desc="Search Results Iteration"):
        
        ad_mention_subrow = product.find("div", attrs={"class":"_4HTuuX"})
        
        is_ad = not not ad_mention_subrow
        
        if not is_ad:
            
            title_mention_subrow = product.find("a", attrs={"class":"s1Q9rs"})
            
            product_title = title_mention_subrow["title"]
            product_relative_url = title_mention_subrow["href"]
            product_url = urljoin(BASE_URL,product_relative_url)
            
            parsed_url = urlparse.urlparse(product_url)
            parsed_url_path = parsed_url.path
            parsed_url_path_split = parsed_url_path.split("/")
            parsed_url_path_split[2] = "product-reviews"
            parsed_url_path_modified = "/".join(parsed_url_path_split)
            parsed_url_modified = parsed_url._replace(path=parsed_url_path_modified)
            product_url = parsed_url_modified.geturl()
            
            product_titles.append(product_title)
            product_urls.append(product_url)
            
            product_count += 1
            
            if popular_products_count_limit and (product_count >= popular_products_count_limit):
                break
                
    return product_titles, product_urls

product_titles, product_urls = get_popular_product_s_titles_and_urls(SEARCH_QUERY, TOP_N_PRODUCTS)

from prettytable import PrettyTable
x = PrettyTable()
x.field_names = ["# Products", "# Reviews Per Page", "# Pages", "# Total Reviews Count"]
x.add_row([len(product_urls), 10, REVIEW_PAGES_TO_SCRAPE_FROM_PER_PRODUCT, len(product_urls)*10*REVIEW_PAGES_TO_SCRAPE_FROM_PER_PRODUCT])
print(x)


dataset = []

for idx, url in enumerate(tqdm(product_urls, desc='products')):
    # iterating over review pages
    for i in tqdm(range(1,REVIEW_PAGES_TO_SCRAPE_FROM_PER_PRODUCT+1), desc="review pages", position=0, leave=False):
        parsed = urlparse.urlparse(url)
        pid = parse_qs(parsed.query)['pid'][0]
        URL = f"{url}&page={i}"
        
        r = requests.get(URL)
        
        # Pause the loop for 0-1 seconds to simulate natural setting not overwhelm the server with back to back requests without any pause
        sleep(random())
        soup = BeautifulSoup(r.content, 'html.parser') 

        rows = soup.find_all('div',attrs={'class':'col _2wzgFH K0kLPL'})

        for row in rows:

            # finding all rows within the block
            sub_row = row.find_all('div',attrs={'class':'row'})

            # extracting text from 1st 2nd and 4th row
            rating = sub_row[0].find('div').text
            summary = sub_row[0].find('p').text
            summary = summary.strip()
            review = sub_row[1].find_all('div')[2].text
            review = review.strip()
            location=""
            location_row = sub_row[3].find('p',attrs={'class':'_2mcZGG'})
            if location_row:
                location_row = location_row.find_all('span')
                if len(location_row)>=2:
                    location = location_row[1].text
                    location = "".join(location.split(",")[1:]).strip()
            date = sub_row[3].find_all('p',attrs={'class':'_2sc7ZR'})[1].text

            sub_row_2 = row.find_all('div',attrs={'class':'_1e9_Zu'})[0].find_all('span',attrs={'class':'_3c3Px5'})

            upvotes = sub_row_2[0].text
            downvotes = sub_row_2[1].text

            # appending to data
            dataset.append({'product_id':pid, 'product_title':product_titles[idx], 'rating': rating, 'summary': summary, 'review': review, 'location' : location, 'date' : date, 'upvotes' : upvotes, 'downvotes' : downvotes})

            df.to_csv("flipkart_reviews_dataset.csv", index=False)
