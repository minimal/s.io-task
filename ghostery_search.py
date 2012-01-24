"Socket.io Problem 1"

# for a given site, find which scripts regexexs
# from bugs.json are in the source


import json
import re
import csv

from requests import async

DEBUG = False
bugs = outcsv = None


def check_for_scripts(html):
    scripts = []
    for bug in bugs:
        if bug['regex']:
            match = bug['regex'].search(html)
            if match:
                scripts.append(bug['id'])
    return scripts


nsites = 1
def check_response(response):
    global nsites
    if not response.status_code == 200:
        print response.url, "error"
        print response.ok
        return
    try:
        scripts = check_for_scripts(response.text)
        print nsites, response.url, scripts
        outcsv.writerow([response.url] + scripts)
        nsites += 1
    except Exception, e:
        print e


def check_sites_async(domains):
    "Get html of sites using requests.async"
    rs = (async.get(domain, hooks=(dict(response=check_response)),
                    timeout=10)
            for domain in domains)
    # TODO: multiple smaller maps to get over urlib3 pool perpetual error
    async.map(rs, prefetch=True, size=5)


def import_bugs(bugsfile="bugs.json"):
    with open(bugsfile) as bf:
        bugs = json.load(bf)["bugs"]
    return bugs


def compile_regexes(bugs):
    errs = 0
    for bug in bugs:
        try:
            bug['regex'] = re.compile(bug['pattern'])
        except Exception as exc:
            errs += 1
            print "error: ", bug['pattern'], bug['id']
            bug['regex'] = None
    print "regex compile Errors:", errs
    return bugs


def import_sites(filename):
    with open(filename) as sitesf:
        for site in sitesf.readlines():
            yield site.strip()


def main():
    global bugs, outcsv  # TODO: no globals
    bugs = compile_regexes(import_bugs())
    sites = import_sites("top100k")
    outcsv = csv.writer(open('output.csv', 'w'), lineterminator='\n')

    if DEBUG:
        sites = import_sites("top100.txt")
        import random
        # shuffle list while testing to not spam the same sites all the time
        sites = list(sites)
        random.shuffle(sites)

    check_sites_async(sites)

if __name__ == '__main__':
    main()
