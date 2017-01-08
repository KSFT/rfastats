#!/usr/bin/env python

import cgitb; cgitb.enable()

import mwclient
import re
import time

site = mwclient.Site('en.wikipedia.org')

def link(page, text=None):
    if text is None: text = page
    return '<a href="https://en.wikipedia.org/wiki/{}">{}</a>'.format(page, text)

def getcandidates():
    text = mwclient.page.Page(site,'Wikipedia:Requests for adminship').text(1)
    return re.findall('{{Wikipedia:Requests for adminship/(.+)}}',text)

def getvotes(candidate):
    text = mwclient.page.Page(site,'Wikipedia:Requests for adminship/'+candidate).text()
    support = text.split('=====Support=====')[1]
    support, oppose = support.split('=====Oppose=====')[:2]
    oppose, neutral = oppose.split('=====Neutral=====')[:2]
    neutral = neutral.split('=====General comments=====')[0]
    supports = processvotes(support)
    opposes = processvotes(oppose)
    neutrals = processvotes(neutral)
    return supports, opposes, neutrals

def processvotes(text):
    lines = text.split('\n')
    votes = []
    for line in lines:
        try:
            author = re.findall(r'\[\[User(?: talk)?:([^][{}|#<>%+?]+)(?:|[^][]+)?\]\]', line)[-1]
            bold = re.findall("#\s*'''(.*?)'''", line)[0]
            comment = re.split(r'\[\[User( talk)?:{}(|[^][]+)?\]\]'.format(re.escape(author)), re.split("#\s*'''.*?'''", line)[1])[0]
            timestamp = time.strptime(re.findall('\d\d:\d\d, \d [A-Z][a-z]+ \d\d\d\d', line)[-1], '%H:%M, %d %B %Y')
            votes.append([author, bold, comment, timestamp])
        except IndexError:
            continue
    return votes

print 'Content-Type: text/html'
print
print '<!DOCTYPE html>'
print '<html>'
print '<body>'
candidates=getcandidates()
if candidates:
    print '<h1>Current RFAs</h1>'
    print '<div>'
    for candidate in candidates:
        print '<div>'
        print '<h2>{}</h2>'.format(link('Wikipedia:Requests for adminship/'+candidate,candidate))
        votes = getvotes(candidate)
        for i in range(3):
            print '<h3>'
            print ('Support', 'Oppose', 'Neutral')[i]
            print '</h3>'
            print '<table>'
            recentvotes = sorted(votes[i], key = lambda x:x[3], reverse = True)[:10]
            for vote in recentvotes:
                print '<tr>'
                print '<td>{}</td>'.format(vote[0])
                print '<td>{}</td>'.format(vote[1])
                print '<td>{}</td>'.format(vote[2].encode('utf-8'))
                print '<td>{}</td>'.format(time.strftime('%H:%M, %d %B %Y',vote[3]))
                print '</tr>'
            print '</table>'
        print '</div>'
    print '</div>'
else:
    print ''
print '</body>'
print '</html>'
