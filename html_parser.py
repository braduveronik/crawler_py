from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import namedtuple

Meta = namedtuple('Meta',['all', 'index', 'follow'])
class HtmlParser():

    def __init__(self,content, base_url):
        self.soup = BeautifulSoup(content,"lxml")
        self.url = base_url

    def get_metadata(self):

        robots = None
        meta_tags = self.soup.find_all('meta')
        for meta in meta_tags:
            if not meta.attrs.get('name'):
                continue

            if meta.attrs.get('name').lower() == 'robots':
                    robots = meta.attrs.get('content')
        meta_all = meta_index = meta_follow = True
        if robots:

            if 'none' in robots:
                meta_all = meta_index = meta_follow = False
            if 'all' in robots:
                meta_all = meta_index = meta_follow = True
            meta_follow = False if 'nofollow' in robots else True
            meta_index = False if 'noindex' in robots else True

        return Meta(all = meta_all,index=meta_index,follow=meta_follow)

    def extract_links(self):
        all_links = []
        for link in self.soup.findAll('a'):
            all_links.append(link.get('href'))
        return [x for x in all_links if x]

    def extract_link_absolute(self, all_links):
        for link in all_links:
            if link.find('/') == -1 or './' in link or '../' in link:
                full_link = urljoin(self.url, link)
                index = all_links.index(link)
                all_links[index] = full_link.split('#')[0]
        for link in reversed(all_links):
            if link == self.url or (self.url + '#') in link:
                all_links.remove(link)
        return set(all_links)

    def extract_text(self):
        return self.soup.body.text
