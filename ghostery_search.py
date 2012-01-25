"""Spider.io Problem 1

For a given site, find which scripts regexes from Ghostery's bugs.json are in
the source

"""

import logging
import json
import re
import csv

from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
# curl can be faster
#AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


class CrawlerClient(object):
    '''HTTP async client.

    * keep track of site being processed
    * get the page content
    * check for scripts
    * write csv
    * notfiy manger when finished
    '''

    def __init__(self, manager, client_id):
        self._client = AsyncHTTPClient(io_loop=manager._ioloop, max_clients=15)
        self._client_id = client_id
        self._manager = manager
        self._site = None
        self.logger = logging.getLogger('%s C-%s' %
                (self._manager.logger.name, client_id))

    def is_ready(self):
        return self._site is None

    def fetch_site(self, site):
        self._site = site
        self._client.fetch(site.encode('utf-8'),
                           self.handle_response,
                           follow_redirects=True,
                           max_redirects=10)

    def handle_response(self, response):
        ''''''
        scripts = check_for_scripts(response.body, self._manager.bugs)
        self._manager.csv_writer.writerow([self._site] + scripts)
        self.logger.debug("%s, %s", self._site, scripts)
        self.finish()

    def finish(self):
        '''Inform manager that client is free'''
        self._manager.done(self)
        self._site = None


class SitesCrawler(object):
    '''Process a list of site urls using child clients


    n_clients needs testing and tuning
    '''

    logger = logging.getLogger()

    def __init__(self, ioloop, n_clients, sites, bugs, csv_writer):
        self._ioloop = ioloop
        self._clients = [CrawlerClient(self, i) for i in xrange(n_clients)]
        self._running = False
        self._sites = sites
        self.bugs = bugs
        self.csv_writer = csv_writer
        self.n_handled = 0

    def pick_client(self):
        for client in self._clients:
            if client.is_ready():
                return client
        return None

    def run(self):
        self._running = True
        while self._sites:
            client = self.pick_client()
            if client:
                site = self._sites.next()
                client.fetch_site(site)
            else:
                # no free clients
                break

    def done(self, client):
        '''Site processed, client can handle a new site'''
        self.n_handled += 1
        if self.n_handled % 10 == 0:  # log every 10
            self.logger.info("%i sites processed", self.n_handled)
        if self._running:
            self.run()


def import_bugs(bugsfile="bugs.json"):
    with open(bugsfile) as bf:
        bugs = json.load(bf)["bugs"]
    return bugs


def check_for_scripts(html, bugs):
    if not html:
        return []
    scripts = []
    try:
        for bug in bugs:
            if bug['regex']:
                match = bug['regex'].search(html)
                if match:
                    scripts.append(bug['id'])
    except Exception, e:  # catch all errs for now
        print e
    return scripts


def compile_regexes(bugs):
    """Try to compile the js regexes"""
    for bug in bugs:
        try:
            bug['regex'] = re.compile(bug['pattern'])
        except Exception as exc:
            print "regex error: ", bug['pattern'], bug['id']
            bug['regex'] = None
    return bugs


def import_sites(filename):
    "Get sites from file as generator"
    with open(filename) as sitesf:
        for site in sitesf.readlines():
            yield site.strip()


def main():
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ioloop = IOLoop()

    bugs = compile_regexes(import_bugs())
    sites = import_sites("top100k")
    outcsv = csv.writer(open('output.csv', 'w'), lineterminator='\n')

    SitesCrawler(ioloop, 15, sites, bugs, outcsv).run()
    ioloop.start()


if __name__ == '__main__':
    main()
