#   ----    import libraries
from bs4 import BeautifulSoup
import requests
import re
import webbrowser as web
import pandas as pd
import pyodbc as db

#    ----    instantiate pyodbc connection and cursor objects
cnxn = db.connect('Driver={SQL Server};'
                  'Server=DESKTOP-73Q4UES\SQLEXPRESS;'
                  'Database=gobbledigook;'
                  'Trusted_Connecton=yes;')
crsr = cnxn.cursor()

tables = crsr.tables()
str_tables = []
for table in tables:
    str_tables.append((str(table.table_name)))

if 'scrapes' not in str_tables:
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

#   ----    get user_agent key:value for headers
headers1 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"}

#   ----    determine search item keyword
search_item = input('What product do you want to search for on Amazon?\n').replace(" ","+")

#   ----    define url
url = f'https://www.amazon.co.uk/s?k={search_item}' 

def get_soup(url_input):
    '''get url html and convert to BS object'''
    url_get = requests.get(url_input, headers = headers1)
    soup = BeautifulSoup(url_get.content, 'lxml')
    return soup

def get_tag(soup_input, attr):
    '''pull tag with given attribute from given BS object'''
    tag = soup_input.find(attr)
    return tag

def write_dict(input):
    '''declare function to append results to file'''
    f1.write(f"Brand: {input[1]['brand']},\n")
    f1.write(f"Description: {input[1]['description']},\n")
    f1.write(f"Price: {input[1]['price']},\n")
    f1.write(f"Rating: {input[1]['rating']} from {input[1]['reviews']} reviews,\n")
    f1.write(f"Link: {input[1]['link']}\n")
    f1.write("-------------------------------\n\n")
    print('written to file')

def db_write(input):
    insert_query = '''INSERT INTO scrapes (search_item, page_num, brand, description, price, rating, reviews_num)
                   VALUES (?,?,?,?,?,?,?)'''
    values = (search_item, page, input[1]['brand'], input[1]['description'], input[1]['price'], input[1]['rating'], input[1]['reviews'])
    crsr.execute(insert_query, values)
    print('inserted to scrapes table')

#   ----    pull total number of pages
main_soup = get_soup(url)
pages_text = main_soup.find(attrs={'class':'s-pagination-item s-pagination-disabled'}).text
pages = int(pages_text)

#   ----    execute code for each page of website
for page in range(1, pages + 1):
    #    ----    get url html and convert to BS object
    page_soup = get_soup(f'{url}&page={page}')
    #    ----    open weblink
    web.open(f'{url}&page={page}')
    #    ----    pull current page number
    page_num = get_tag(page_soup, "attrs={'class':'s-pagination-item s-pagination-selected'}.text")
    #    ----    pull span tag containing all results 
    try:
        rslt_span = page_soup.find('span', attrs={'data-component-type':'s-search-results'})
        rslt_span_msg = 'successful'
    except AttributeError:
        rslt_span_msg = 'failed'
    #    ----    pull list of all result tags
    try:
        rslt_lildivs = rslt_span.findAll('div', attrs={'class':'sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 AdHolder sg-col s-widget-spacing-small sg-col-4-of-20'})
        rslt_lildivs_msg = 'successful'
    except AttributeError:
        rslt_lildivs_msg = 'failed'

    #    ----    open file for each page, clears contents if already exists
    with open(f'Amazon_{search_item}_page{page}.txt', 'w') as file:
        file.write(f"span request: {rslt_span_msg},\n")
        file.write(f"lildivs request: {rslt_lildivs_msg},\n\n")

    #    ----    pre-declare dictionary
    lildict = {}

    # #    ----    iterate through list of result tags and pull information
    for index, lildiv in enumerate(rslt_lildivs):
        #    ----    try/except clauses in case of missing information
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

        #    ----    insert pulled data into pre-declared dictionary
        lildict[index+1] = {
            'rating':rslt_rating,
            'reviews':rslt_reviews, 
            'brand':rslt_brand,
            'description':rslt_desc,
            'price':rslt_price,
            'price float': rslt_price_float,
            'link':rslt_link}

    #    ----    sort dictionary into list of key:value tuples in ascending price
    sorted_dict = sorted(lildict.items(), key=lambda x: x[1]['price float'])

    #    ----    create pandas dataframe from sorted_dict data
    # new_dict = {}
    # for tuple in sorted_dict:    #  --  convert dictionary to correct format e.g., {'col1':[0,1,2,3], 'col2':[a,b,c,d]}
    #     new_dict[key].append(value) for key, value in tuple.items():
    # dict_df = pd.DataFrame(new_dict)

    #    ----    iterate through sorted list of tuples
    for rslt in sorted_dict:
        with open(f'Amazon_{search_item}_page{page}.txt', 'a', encoding='utf-8') as f1:
            #    ----    call function to append results to file
            write_dict(rslt)
        db_write(rslt)
        cnxn.commit()
  
    #    ----    print page number and number of items
    print(f'Page: {page}/{pages} contains {len(sorted_dict)} items')


# delete_table_query = '''DROP TABLE new_table'''
# crsr.execute(delete_table_query)
# cnxn.commit()

crsr.close()
cnxn.close()

#    ----    state when program is done
print('Scrape complete')
