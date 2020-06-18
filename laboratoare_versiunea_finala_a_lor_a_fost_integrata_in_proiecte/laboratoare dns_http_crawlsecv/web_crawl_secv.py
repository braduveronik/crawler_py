from urllib.parse import urljoin
import os
import socket
from bs4 import BeautifulSoup
import requests
import queue


class HtmlParser():

    def __init__(self, file_path, base_url):
        self.fp = file_path
        self.soup = BeautifulSoup(self.fp, "lxml")
        self.url = base_url

    def get_metadata(self):
        title = self.soup.find('title')
        if title:
            title = title.text

        description = keywords = robots = None
        meta_tags = self.soup.find_all('meta')
        for item in meta_tags:
            attr = item.attrs.get('name')
            if attr:
                if attr.lower() == 'robots':
                    robots = item.attrs.get('content')
        return robots

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


def create_dns_message(address):
    dns_message = b''
    # Header
    dns_message += b'\xab\xcd'  # ID
    dns_message += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    # Question
    address = address.split('.')

    for a in address:
        dns_message += bytes([len(a)]) + a.encode('ascii')
    dns_message += b'\x00'  # NULL
    dns_message += b'\x00\x01'  # Question Type
    dns_message += b'\x00\x01'  # Question Class
    return dns_message


def create_html_message(html_host):
    request = 'GET /crawl/ HTTP/1.1\r\n'
    host = 'Host: ' + html_host + '\r\n'
    user_agent = 'User-Agent: CLIENT RIW\r\n'
    connection = 'Connection: close\r\n'
    return bytes(request + host + user_agent + connection + '\r\n', 'utf-8')


def process_dns(response):
    r_code = response[3] & 0x0f
    if r_code != 0:
        print("[error] RCode =", r_code)
        return

    an_count = int(response[6:8].hex(), 16)
    if an_count == 0:
        print("[error]: ANCount = 0")
        return

    name_end = response.find(0x00, 12) + 1  # line 12
    name = response[12:name_end]

    # c2 - if request{IP} => 1
    type = response[name_end: name_end + 2].hex()[-1]

    # if answer{ desired IPv4} => 4
    rd_length = response[-6:-4].hex()[-1]

    r_data = response[-4:].hex()

    ip_address = ''
    for index in range(0, len(r_data), 2):
        ip_address = ip_address + str(int(r_data[index:index + 2], 16)) + '.'
    print(
        "r_code={}, an_code={}, name={}, type={}, rd_length={}, r_data={}, ip_address={}".format(r_code, an_count, name,
                                                                                                 type, rd_length,
                                                                                                 r_data,
                                                                                                 ip_address[:-1]))
    return ip_address[:-1]


def dns_client(website):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 53))
        s.sendall(create_dns_message(website))

        response = s.recv(512)
        print(response)

        ip_address = process_dns(response)
        s.close()
    return ip_address


def http_client(website):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((dns_client(website), 80))
        message = create_html_message(website)
        s.sendall(message)

        process_header = True
        process_content = True
        response = ''
        while True:
            try:
                resp = s.recv(1024)
                len_resp = len(resp)
                response += str(resp)

                if process_header:

                    ok_200 = '200 OK'
                    if ok_200 in response:
                        print('HTTP 200 OK success status response')
                    else:
                        print('Bad Request')
                        break

                    content = response.find('Content-Length')
                    lenght_start = response.find(' ', content)
                    lenght_stop = response.find('\\r', content)
                    content_length = int(response[lenght_start + 1:lenght_stop])

                    doctype_index = int(response.find('\\r\\n\\r\\n'))
                    recv_total = content_length + doctype_index

                    if content_length > 0:
                        process_header = False
                        print('Content-Length: ' + str(content_length))
                        print('Total to recv: ' + str(recv_total))

                else:
                    if process_content:
                        while len_resp < recv_total and '</HTML>' not in response:
                            resp = s.recv(1024)
                            len_resp += len(resp)
                            response += str(resp)
                            end_response = response.find('</HTML>')

                        process_content = False

                        return response[257:end_response+7].replace('\\n', '&#10').replace('\\r', '&#13').replace('\\\'','')

                    else:

                        # output_dir = os.path.join('riweb.tibeica.com', 'crawl')
                        # if not os.path.exists(output_dir):
                        #     os.makedirs(output_dir)
                        # with open(output_dir + '/' + 'crawl.html', 'w') as html:
                        #     html.write(
                        #         response[257:end_response].replace('\\n', '&#10').replace('\\r', '&#13').replace('\\\'',
                        #                                                                                          ''))
                        break
            except:
                print('receive failed')
                break

        s.close()

if __name__ == "__main__":

    content_website = ''
    contor = 0
    queue = queue.Queue()
    visited_set = set()
    url_set = ['http://riweb.tibeica.com/crawl/index.html','http://riweb.tibeica.com/crawl/', 'http://riweb.tibeica.com/crawl/']

    for url in url_set:
        queue.put(url)

    while not queue.empty() and contor<100:
        l = queue.get()
        if l in visited_set:
            print('\n\n\n******-already visited')
            continue
        else:
            visited_set.add(l)
            contor+=1
            website_domain = l[l.find('//')+2:l.find('com')+3]
            content_website = http_client(website_domain)
            website_path = l[l.find('com')+4 : l.find('/', l.find('com')+4)]
            website_query = l[l.find('/', l.find('com')+4)+1:]

            # print('content:\n' + content_website)
            if content_website != '':
                soup = HtmlParser(content_website, base_url=l)
                print('\n\tMetadata: ' + str(soup.get_metadata()) + '\n')
                robots = soup.get_metadata()
                #all in loc de None la 214 si 223
                if robots == None or robots == 'index':

                    if website_path:
                        dir_main = os.path.join(website_domain,website_path)
                    if not os.path.exists(dir_main):
                        os.makedirs(dir_main)
                    if website_query:
                        with open(dir_main + '/' + website_query, 'w') as html:
                            html.write(content_website)
                elif robots == None or robots == 'follow':
                    links = soup.extract_links()
                    print('\n\tFull_links: ' + str(soup.extract_link_absolute(links)) + '\n')
                    for link in links:
                        queue.put(link)

