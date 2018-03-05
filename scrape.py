import sys, re, csv
import urllib2
from bs4 import BeautifulSoup

scrape_file = 'scrapings.csv'
base_url = "http://www.spitzer.caltech.edu"  # no trailing slash
index_url = base_url + "/search/image_set/100?by_type=astronomical&page={}"

# get all page urls
page_no = 1
all_page_urls = []
while True:
    
    url = index_url.format(page_no)    
    print("checking {}".format(url))

    try:
        soup = BeautifulSoup(urllib2.urlopen(url).read() ,"html.parser")
    except urllib2.HTTPError, e:
        print(e)
        sys.exit()

    if not len(soup.find_all("td", class_="item")):
        print("No more pages we done.")
        break  # we done
        
    for cell in soup.find_all("td", class_="item"):  # this layout uses tables 
        page_url = cell.find('a')['href']
        print("adding {}".format(base_url + page_url))
        all_page_urls.append(base_url + page_url)
    
    page_no += 1
    
# find all item images and content
for url in all_page_urls:
    try:
        soup = BeautifulSoup(urllib2.urlopen(url).read() ,"html.parser")
    except urllib2.HTTPError, e:
        print(e)
        sys.exit()
    
    # find img url 
    img_url = ''
    all_download_links = soup.find("div", {"class": "download"}).find_all('a')
    for link in all_download_links:
        if 'lrg' in link['href'].lower():
            img_url = base_url + link['href']
            break  # got it
    if not img_url:
        # just take the last download link that is a jpeg
        all_download_links.reverse()
        for link in all_download_links:
            if 'jpg' in link['href'].lower():
                img_url = base_url + link['href']
    
    # find content
    tweet = soup.find("div", {"class": "item-content"}).find('p').text.split('.')[0] + '.'
    if len(tweet) > 280:
        # if first sentence of content is too long just use the title only
        tweet = soup.find("h2").text  
    tweet = tweet.encode('utf-8').strip()
    
    # write to csv
    if img_url and tweet:
        with open(scrape_file, 'a') as csvfile:
            print("writing: {}, {}, {}".format(url, img_url, tweet))
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([url, img_url, tweet])    
        
    del img_url, tweet        