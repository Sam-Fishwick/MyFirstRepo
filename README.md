# MyFirstRepo

This is a personal respository to house my personal projects.

Currently this repository contains a python web-scraping program intended to gather price data from Amazon.co.uk via its HTML.

This project is intended to demonstrate data-gathering capabilities in python as well as eventually providing a small data-set with which to demonstrate SQL querying, and python data-cleaning, data-manipulation, and data-visualisation capabilities (pandas, numpy, matplotlib, etc.).

In it's current state, this web-scraping programme (scrape.py) will request the desired search item from the user and then pull and navigate the HTML from the appropriate Amazon.co.uk web-link. Revelant data is then pulled, including the description, rating, and price for each item found.
This programme is written bespoke for a particular HTML layout on Amazon.co.uk domain name specifically, and is therefore limited in scope. It is not expected to function as intended with alternative domain names, or even pages with alternative HTML layouts within the Amazon.co.uk domain name.

To Do:
- Refactor code to be more functional/modular for improved readability and testability.
  - e.g., Reduce size of function called in main for-loop.
- Write some unit-tests for more tailored and repeatable testing.
- Perform more thorough data-cleaning on web-scrape data with pandas library, and look to visualise cleaned data using e.g., matplotlib and seaborn.

Completed:
- Connect to a database (e.g., MS SQLServer) and export data using SQL queries with pyodbc module.
- Demonstrate basic functionality of pandas library using web-scrape data in Jupyter notebook.
