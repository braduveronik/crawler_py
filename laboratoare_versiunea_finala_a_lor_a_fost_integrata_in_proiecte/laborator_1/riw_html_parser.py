import os
import requests
import validators
import re
from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class HtmlParser():

  def __init__(self, file_path, base_url):
        self.fp = open(file_path)
        self.soup = BeautifulSoup(self.fp.read(), "lxml")
        self.url = base_url
        
  def extract_content(self):
         title = self.soup.find('title')
         if title:
             title = title.text

         description = keywords = robots =  None
         meta_tags = self.soup.find_all('meta')
         for item in meta_tags:
             attr = item.attrs.get('name')
             if attr:
                 if attr.lower() == 'keywords':
                     keywords = item.attrs.get('content')
                 elif attr.lower() == 'description':
                     description = item.attrs.get('content')
                 elif attr.lower() == 'robots':
                     robots = item.attrs.get('content')
         return title, keywords, description, robots

  def extract_links(self):
        all_links = []
        for link in self.soup.findAll('a'):
            all_links.append(link.get('href'))
        return [x for x in all_links if x]

  def extract_link_absolute(self, all_links):
        for link in all_links:
            if link.find('/') == -1 or './' in link or '../' in link:
                full_link = urljoin(self.url, link)
                index = links.index(link)
                all_links[index] = full_link
        return links
        
  def extract_text(self):
      return self.soup.body.text
      
if __name__== "__main__":

    output = open("riw_html_output.txt", "w")
    file = os.path.join(os.getcwd(), 'riw_html_input.html')
    soup = HtmlParser(file,base_url='http://tiberius.byethost13.com/pcw_lab' )

    output.write('\n\tTitle&Metadata: ' + str(soup.extract_content()) + '\n')
    output.write('\n\tText: ' + str(soup.extract_text()) + '\n')
    links = soup.extract_links()
    output.write('\n\tLinks: ' + str(links) + '\n')
    output.write('\n\tFull_links: ' + str(soup.extract_link_absolute(links)) + '\n')
    
    output.close()
