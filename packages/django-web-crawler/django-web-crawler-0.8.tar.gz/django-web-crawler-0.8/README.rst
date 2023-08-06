==================
Django Web Crawler
==================

Crawler is a Django app to help connect to a website and gather as much links as you want.

Quick start
-----------

1. Add "gatherlinks" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'gatherlinks',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('crawl/', include('crawl.urls')),

3. Import the "main" module like this::

    from gatherlinks.crawler import main


4. Initialize the StartPoint class like this::

    crawler = main.StartPoint(https://example.com, max_crawl=50, number_of_threads=10)

5. The StartPoint class can be initialized with three arguments.
    a. homepage (a positional argument of the website to gather it's link.)

    b. max_crawl (maximum number of links to gather from the website. Default is 50)

    c. number_of_threads (Number of threads to be doing the work simultaneously. Default is 10)
6. After initialising the class, you can then call the "start" method like this::

    crawler.start()

7. When the crawler must have finished gathering the link, you can access the gathered links like this::

    crawler.result

That result attribute is a "set" datatype that holds all the links that the crawler could gather.
You can then loop through the "crawler.result" and do whatever you want with it (write to file or save to database).