# --- import libraries/modules
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import re
import webbrowser as web
import pyodbc as db

load_dotenv()

# --- instantiate pyodbc database connection and cursor objects
cnxn = db.connect(f'Driver={os.getenv("DRIVER")};'
                  'Server={os.getenv("SERVER")};'
                  'Database={os.getenv("DATABASE")};'
                  'Trusted_Connecton=yes;')
crsr = cnxn.cursor()

# --- pull names of table in database and convert to list of strings
tables = crsr.tables()
table_names = []
for table in tables:
    table_names.append((str(table.table_name)))

# --- create 'scrapes' table if not already present in database
if 'scrapes' not in table_names:
    create_query = '''CREATE TABLE scrapes (
                  search_item varchar(100),
                  page_num int,
                  brand varchar(100),
                  description varchar(500),
                  price varchar(10),
                  rating varchar(20),
                  reviews_num varchar(10))'''
    crsr.execute(create_query)
    cnxn.commit()
    print('created table: scrapes')
else:
    print('scrapes table already exists')

# --- get user_agent key:value for headers
headers1 = os.getenv('HEADER')
# --- determine search item keyword
search_item = input('What product do you want to search for on Amazon?\n').replace(" ","+")

# --- define url
url = f'https://www.amazon.co.uk/s?k={search_item}'

# --- define function to instantiate soup object from url
def get_soup(url_input):
    '''get url html and convert to BS object'''
    url_get = requests.get(url_input, headers = headers1)
    soup = BeautifulSoup(url_get.content, 'lxml')
    return soup

# --- define function to pull text from a particular tag with given attribute
# def get_tag(soup_input, attr_name, attr_desc):
#     '''pull relevant tag from given soup object and attribute'''
#     tag = soup_input.find(attrs={attr_name:attr_desc}).text
#     return tag

# --- define function to write data from given data-structure to a given .txt file
def txt_write(input, file_input):
    '''append results to .txt file'''
    file_input.write(f"Brand: {input[1]['brand']},\n")
    file_input.write(f"Description: {input[1]['description']},\n")
    file_input.write(f"Price: {input[1]['price']},\n")
    file_input.write(f"Rating: {input[1]['rating']} from {input[1]['reviews']} reviews,\n")
    file_input.write(f"Link: {input[1]['link']}\n")
    file_input.write("-------------------------------\n\n")
    print('written to file')

# --- define function to insert data from given data-structure to pyodbc database
def db_insert(input, page_input):
    insert_query = '''
        INSERT INTO scrapes (search_item, page_num, brand, description, price, rating, reviews_num)
        VALUES (?,?,?,?,?,?,?)'''
    values = (
        search_item, 
        page_input, 
        input[1]['brand'], 
        input[1]['description'], 
        input[1]['price'], 
        input[1]['rating'], 
        input[1]['reviews'])
    crsr.execute(insert_query, values)
    print(f'{crsr.rowcount} row(s) inserted to scrapes table')
    cnxn.commit()

# --- define function to delete table from database
# def db_delete(table_name, condition):
#     delete_table_query = '''DELETE FROM table_name WHERE condition'''
#     crsr.execute(delete_table_query)
#     print(f'{crsr.rowcount} row(s) were deleted')
#     cnxn.commit()

# --- pull total number of pages from given url
main_soup = get_soup(url)
pages_text = main_soup.find(attrs={'class':'s-pagination-item s-pagination-disabled'}).text
pages = int(pages_text)

# --- declare function to be called for each page of website
def inside_for(page_input, pages_input):
    # --- define url for each page
    page_url = f'{url}&page={page_input}'

    # --- get url html and convert to BS object
    page_soup = get_soup(page_url)

    # --- open weblink
    # web.open(page_url)

    # --- pull current page number
    # page_num = page_soup.find(attrs={'class':'s-pagination-item s-pagination-selected'}).text

    # --- pull span tag containing all results 
    try:
        rslt_span = page_soup.find('span', attrs={'data-component-type':'s-search-results'})
        rslt_span_msg = 'successful'
    except AttributeError:
        rslt_span_msg = 'failed'

    # --- pull list of all result tags
    try:
        rslt_lildivs = rslt_span.findAll('div', attrs={'class':'sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 AdHolder sg-col s-widget-spacing-small sg-col-4-of-20'})
        rslt_lildivs_msg = 'successful'
    except AttributeError:
        rslt_lildivs_msg = 'failed'

    # --- open file for each page, clears contents if already exists
    with open(f'Amazon_{search_item}_page{page_input}.txt', 'w') as file:
        file.write(f"span request: {rslt_span_msg},\n")
        file.write(f"lildivs request: {rslt_lildivs_msg},\n\n")

    # --- iterate through items and pull data
    for index, lildiv in enumerate(rslt_lildivs):
        # --- try/except clauses in case of missing information (AttributeError: 'None' has no .text attribute)
        try:
            rslt_rating = lildiv.find('span', attrs={'class':'a-icon-alt'}).text
        except AttributeError:
            rslt_rating = 'N/A'

        try:
            rslt_reviews = lildiv.find('span', attrs={'class':'a-size-base s-underline-text'}).text 
        except AttributeError:
            rslt_reviews = 'N/A'

        try:
            rslt_desc = lildiv.find('span', attrs={'class': re.compile('a-size-base.* a-color-base a-text-normal')}).text
        except AttributeError:
            rslt_desc = 'N/A'

        try:
            rslt_price = lildiv.find('span', attrs={'a-offscreen'}).text
            rslt_price_float = float(rslt_price[1:])
        except AttributeError:
            rslt_price = 'N/A'    
            rslt_price_float = 0.00

        try:
            rslt_href = lildiv.find('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).get('href')
            rslt_link = 'https://www.amazon.co.uk'+rslt_href
        except AttributeError:
            rslt_href = 'N/A'
            rslt_link = 'N/A'

        try:
            rslt_brand = lildiv.find('span', attrs={'class':'a-size-base-plus a-color-base'}).text
        except AttributeError:
            rslt_brand = 'N/A'

        # --- insert pulled data into pre-declared dictionary
        lildict = {}
        lildict[index+1] = {
            'rating':rslt_rating,
            'reviews':rslt_reviews, 
            'brand':rslt_brand,
            'description':rslt_desc,
            'price':rslt_price,
            'price float': rslt_price_float,
            'link':rslt_link}

    # --- sort dictionary into list of key:value tuples in ascending price
    sorted_dict = sorted(lildict.items(), key=lambda x: x[1]['price float'])

    # --- iterate through sorted list of tuples
    for rslt in sorted_dict:
        with open(f'Amazon_{search_item}_page{page_input}.txt', 'a', encoding='utf-8') as f1:
            # --- call function to append results to file
            txt_write(rslt, f1)
        db_insert(rslt, page_input)

    # --- print page number and number of items
    print(f'Page: {page_input}/{pages_input} contains {len(sorted_dict)} items')

# --- iterate through each page, pull data, and record in .txt file and database
for page in range(1, pages + 1):
    inside_for(page, pages)

# --- close pyodbc cursor and connection
crsr.close()
cnxn.close()

# --- state when program is done
print('Scrape complete')
