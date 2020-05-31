import os
from queue import Queue
import urllib.robotparser as robot
from urllib.parse import urlparse
import validators
from http_propriu import http_client
from multiprocessing import Manager, Process, cpu_count
import time
import shutil


content_website = None
visited_contor = 0
# initial 2-3 link-uri
queue = Queue()
queue.put('http://riweb.tibeica.com/crawl/')
visited_set = set()

def crawler():
    global visited_contor
    # https://docs.python.org/3/library/urllib.robotparser.html
    robot_parser = robot.RobotFileParser()
    riw_tibeica_robots = 'http://riweb.tibeica.com/robots.txt'
    robot_parser.set_url(riw_tibeica_robots)
    robot_parser.read()

    while not queue.empty() and visited_contor < 100:
        link = queue.get()
        if not validators.url(link):
            print('\n\tInvalid link\t', link + '\n')
            continue
        if link in visited_set:
            print('\n\tAlready visited\t', link + '\n')
            continue

        soup, rep = http_client(link)
        content_website = soup.extract_text()
        if content_website:
            visited_set.add(link)
            visited_contor += 1
            # print(visited_contor)

            if rep.all or rep.index:

                root = urlparse(link).netloc
                child = urlparse(link).path.replace('/', '')
                if child[-5:] != '.html':
                    child += '.html'
                if not child:
                    child = 'index.html'
                path = os.path.join(root,child)
                os.makedirs(os.path.dirname(path), exist_ok= True)
                with open(path,'w') as file:
                    file.write(soup.soup.prettify())

            if rep.all or rep.follow:
                # Extrage din P o lista noua de legaturi N
                links = soup.extract_links()
                absolute_links = soup.extract_link_absolute(links)

                # Adauga N la Q
                for link in absolute_links:

                    if link not in visited_set and robot_parser.can_fetch('RIWEB_CRAWLER', link):

                        if root in link:
                            queue.put(link)
    print('number of pages: ' + str(visited_contor))

def remove_child_dirs(parent_dir):
    for child in os.listdir(parent_dir):
        if os.path.isdir(os.path.join(parent_dir,child)) and child != '__pycache__':
            shutil.rmtree(os.path.join(parent_dir,child))
            print('we deleted ' + os.path.join(parent_dir,child) )

if __name__ == '__main__':

    #region SEQUENTIAL
    print('Sequential')
    remove_child_dirs(os.getcwd())
    #endregion
    start = time.time()
    crawler()
    print(" Sequential --- %s seconds ---" % (time.time() - start))
