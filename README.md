Spider.io Problem 1
===================

Ghostery and Alexa Data
-----------------------

I found out where to download the Alexa list of the top million websites and the
Ghostery bugs file that has regular expressions for eact tracking script.  I
wrote 2 lines of shell script to import bugs.json and the alexa top 100. The
alexa line streams the zip from wget into `funzip` which can extract a piped zip
file. This meant that when used with `head`, only the top 100k sites needed to
be downloaded.


Crawling Script
---------------

I first made some functions to import the ghostery bugs.json and try to compile
the regex patterns. JS regex is not 100% compatible with python regexes so 4
patterns failed to compile.

Then I made a basic sequential page scraper and function to check the text for
all the patterns in bugs.json. Scraping 100k sites sequentially would take a
very long so I had to change the site fetching to concurrently fetch many sites
at once.

First I used the `requests` library with its async feature which uses `gevent`.
This seemed to work and certainly sped up the processing but I ran into an
apperent bug with the underlying `urllib3` resulted in increasing HTTPPool
errors until the fetching process stalled completely. After trying to work
around the problem I finally decided to use `Tornado's` `AsyncHTTPClient`
instead, which I have used before but requires some more code to have a pool of
clients.

I refactored the code to use a class to manage the clients and store state. The
managing class sends urls each of the client instances and waits for the clients
to say they are ready for more urls. When a client fetches a site it checks for
the tracking scripts and then appends the results to a csv file.

With 15 clients it manages about 6 sites per second at present. Adding more
clients doesn't seem to improve the speed and makes it slower eventually.


Requirements
------------

- Python
- Tornado


    $ pip install tornado


Usage
-----

    $ ./getfiles.sh
    $ python ghostery_search.py


