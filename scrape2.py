#   ----------    import libraries
from bs4 import BeautifulSoup
import requests
import re
import webbrowser as web

#   ----------    get user_agent key:value for headers
headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
}

#   ----------    determine search item keyword
search_item = input('What product do you want to search for on Amazon?\n')

#   ----------    get url html and convert to BS object
url = f'https://www.amazon.co.uk/s?k={search_item}'
url_get = requests.get(url, headers = headers1)
soup = BeautifulSoup(url_get.content, 'lxml')

#   ----------    pull number of pages of website
pages_text = soup.find(attrs={'class':'s-pagination-item s-pagination-disabled'}).text
pages = int(pages_text)

#   ----------    execute code for each page of website
for page in range(1, pages + 1):
    #   ----------    get url html and convert to BS object
    url = f'https://www.amazon.co.uk/s?k={search_item}&page={page}'
    url_get = requests.get(url, headers = headers1)
    soup = BeautifulSoup(url_get.content, 'lxml')

    #    ----------    open weblink
    web.open(url)

    #    ----------    pull current page number
    page_text = soup.find(attrs={'class':'s-pagination-item s-pagination-selected'}).text
    current_page = str(page_text)+'/'+str(pages_text)

    #    ----------    pull tag containing all results 
    try:
        rslt_span = soup.find('span', attrs={'data-component-type':'s-search-results'})
        rslt_span_msg = 'successful'
    except:
        rslt_span_msg = 'failed'

    #    ----------    pull list of all result tags
    try:
        rslt_lildivs = rslt_span.findAll('div', attrs={'class':'sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 AdHolder sg-col s-widget-spacing-small sg-col-4-of-20'})
        rslt_lildivs_msg = 'successful'
    except:
        rslt_lildivs_msg = 'failed'

    #    ----------    open file for each page, clears contents if already exists
    with open(f'Amazon_{search_item}_page{page}.txt', 'w') as file:
        file.write(f"span request: {rslt_span_msg},\n")
        file.write(f"lildivs request: {rslt_lildivs_msg},\n\n")

    #    ----------    pre-declare dictionary
    lildict = {}

    # #    ----------    iterate through list of result tags and pull information
    for index, lildiv in enumerate(rslt_lildivs):
        #    ----------    try/except clauses in case of missing information
        try:
            rslt_rating = lildiv.find('span', attrs={'class':'a-icon-alt'}).text
        except:
            rslt_rating = 'N/A'

        try:
            rslt_reviews = lildiv.find('span', attrs={'class':'a-size-base s-underline-text'}).text 
        except:
            rslt_reviews = 'N/A'

        try:
            rslt_desc = lildiv.find('span', attrs={'class': re.compile('a-size-base.* a-color-base a-text-normal')}).text
        except:
            rslt_desc = 'N/A'

        try:
            rslt_price = lildiv.find('span', attrs={'a-offscreen'}).text
            rslt_price_float = float(rslt_price[1:])
        except:
            rslt_price = 'N/A'    
            rslt_price_float = 0.00

        try:
            rslt_href = lildiv.find('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).get('href')
            rslt_link = 'https://www.amazon.co.uk'+rslt_href
        except:
            rslt_href = 'N/A'
            rslt_link = 'N/A'

        try:
            rslt_brand = lildiv.find('span', attrs={'class':'a-size-base-plus a-color-base'}).text
        except:
            rslt_brand = 'N/A'

        #    ----------    insert pulled data into pre-declared dictionary
        lildict[index+1] = {'rating':rslt_rating, 'reviews':rslt_reviews, 'brand':rslt_brand, 'description':rslt_desc, 'price':rslt_price, 'price float': rslt_price_float, 'link':rslt_link}

    #    ----------    sort dictionary into list of key:value tuples in ascending price
    sorted_dict = sorted(lildict.items(), key=lambda x: x[1]['price float'])


    #    ----------    declare function to append results to file
    def write_dict(input):
        f1.write(f"Brand: {input[1]['brand']},\n")
        f1.write(f"Description: {input[1]['description']},\n")
        f1.write(f"Price: {input[1]['price']},\n")
        f1.write(f"Rating: {input[1]['rating']} from {input[1]['reviews']} reviews,\n")
        f1.write(f"Link: {input[1]['link']}\n")
        f1.write("-------------------------------------\n\n")

    #    ----------    iterate through sorted list of tuples
    for rslt in sorted_dict:
        #    ----------    append results to .txt file
        with open(f'Amazon_{search_item}_page{page}.txt', 'a', encoding='utf-8') as f1:
            #    ----------    call function to append results to file
            write_dict(rslt)
  
    #    ----------    print page number and number of items
    print(f'Page: {page}/{pages} contains {len(sorted_dict)} items')

#    ----------    state when program is done
print('Scrape complete')
