"Socket.io Problem 1"

# for a given site, find which scripts regexexs
# from bugs.json are in the source

import urllib2
import json
import re


def check_site(domain):
    url = "http://" + domain
    response = urllib2.urlopen(url, timeout=2)
    html = response.read()
    scripts = []
    for bug in bugs:
        if bug['regex']:
            match = bug['regex'].search(html)
            if match:
                scripts.append(bug['id'])
    return scripts

def import_bugs(bugsfile="bugs.json"):
    with open(bugsfile) as bf:
        bugs = json.load(bf)["bugs"]
    return bugs

def compile_regexes(bugs):
    errs = 0
    for bug in bugs:
        #print "compile", bug['pattern']
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
    sites = import_sites("100k.txt")
    for site in sites:
        try:
            scripts = check_site(site)
            print site, scripts
        except Exception, e:
            print e
            print site, "error"
        
        

    #scripts = check_site("imgur.com")
