import urllib
from bs4 import *

uh = urllib.urlopen('https://en.wikipedia.org/wiki/QS_World_University_Rankings#Results')
data=uh.read()
soup=BeautifulSoup(data,'html.parser')
tbl=soup.find('table',{'class':"sortable wikitable"})
sch=tbl.findAll('tr')[1:]
print 'Retrieved', len(sch), 'universities'

top=[]
for univ in sch :
    name=univ.findAll('a')[1].text
    rank=univ.findAll('td')[6].text
    N=name.encode('ascii','ignore')
    R=str(rank)
    top.append((N,R))

print top
    
