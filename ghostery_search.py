"Socket.io Problem 1"

# for a given site, find which scripts regexexs
# from bugs.json are in the source

import urllib2
import json
import re

from requests import async


def check_for_scripts(html):
    scripts = []
    for bug in bugs:
        if bug['regex']:
            match = bug['regex'].search(html)
            if match:
                scripts.append(bug['id'])
    return scripts

def check_site(domain):
    url = "http://" + domain
    response = urllib2.urlopen(url, timeout=2)
    html = response.read()
    
    return check_for_scripts(html)

nsites = 1
def check_response(response):
    global nsites
    try:
        scripts = check_for_scripts(response.text)
        print nsites, response.url, scripts
        nsites += 1
    except Exception, e:
        print e
        # print  "error"    
    

def check_sites_async(domains):
    "Get html of sites usign requests.async"
    rs = (async.get("http://" + domain, hooks=(dict(response=check_response)),
                    timeout=1.0, prefetch=False)
            for domain in domains)
    
    async.map(rs, size=100)


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



if __name__ == '__main__':
    global bugs
    bugs = compile_regexes(import_bugs())
    #sites = import_sites("top100.txt")
    sites = import_sites("100k.txt")
    import random
    # shuffle list while testing to not spam the same sites all the time
    sitelist = list(sites)
    random.shuffle(sitelist)
    check_sites_async(sitelist)
    # for site in sites:
    #     try:
    #         scripts = check_site(site)
    #         print site, scripts
    #     except Exception, e:
    #         print e
    #         print site, "error"
        
        

    #scripts = check_site("imgur.com")
