# WebScraping

This is a personal respository to house my personal python web-scraping project intended to gather Amazon.co.uk price data, as well as store the data in a MS SQL Server database and manipulate the data with Pandas in a Jupyter Notebook.

In it's current state, this web-scraping programme (scrape.py) will request the desired search item from the user and then pull and navigate the HTML from the appropriate Amazon.co.uk web-link. Revelant data is then pulled, including the description, rating, and price for each item found.
This programme is written bespoke for a particular HTML layout on Amazon.co.uk specifically, and is therefore limited in scope. It is not expected to function as intended with alternative domain names, or even pages with alternative HTML layouts within Amazon.co.uk.

To Do:
- Refactor code to be more functional/modular for improved readability and testability.
  - e.g., Reduce size of function called in main for-loop.
- Write some unit-tests for more tailored and repeatable testing.
- Perform more thorough data-cleaning on web-scrape data with Pandas library, and look to visualise cleaned data using e.g., Matplotlib and Seaborn.

Completed:
- Connect to a database (e.g., MS SQL Server) and export data using SQL queries with Pyodbc module.
- Demonstrate basic functionality of Pandas library using web-scrape data in Jupyter Notebook.
