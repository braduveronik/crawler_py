import socket
from dns_propriu import dns_client
from html_parser import HtmlParser
from urllib.parse import urlsplit

def create_html_message(path, netloc, user, connection):

    request = 'GET {} HTTP/1.1\r\n'.format(path)
    host = 'Host: {}\r\n'.format(netloc)
    user_agent = 'User-Agent: {}\r\n'.format(user)
    connection = 'Connection: {}\r\n'.format(connection)
    riw_request = request + host + user_agent + connection + '\r\n'

    return bytes(riw_request,'utf-8')

def http_client(website):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        scheme = urlsplit(website).scheme
        netloc = urlsplit(website).netloc
        path = urlsplit(website).path

        s.connect((dns_client(netloc), 80))
        message = create_html_message(path,netloc,'CLIENT RIW', 'close')
        s.sendall(message)

        process_header = True
        process_content = True
        html_content = ''

        while True:
            try:

                resp = s.recv(1024)
                # len_resp = len(resp)
                html_content += resp.decode() # sau las cu str(resp)

                while process_header:
                    #TODO coduri http handle
                    # b'HTTP/1.1 200 OK\r\nServer: nginx/1.10.2\r\nDate: Fri, 29 May
                    # HTTP/1.1 200 OK [0] si split la astea 2 si iau [1]
                    status = resp.split(b'\r\n')[0].split()[1]
                    if status == '':
                        #pt 301
                        #
                        pass


                    process_header = False

                if process_content:
                        #while len_resp > 0 and '</HTML>' not in html_content:
                        while len(resp) > 0:
                            resp = s.recv(1024)
                            # len_resp += len(resp)
                            html_content += resp.decode()
                            # end_response = html_content.find('</HTML>')

                        process_content = False
                        html_content = html_content.split('\r\n\r\n')[1]
                        base_url = website[:website.find('/',7)]
                        html_parser = HtmlParser(html_content,base_url)
                        return html_parser ,html_parser.get_metadata()
                else:

                        break
            except:
                print('receive failed')
                return None, None
            finally:
                s.close()

if __name__ == '__main__':

    http_client('http://riweb.tibeica.com/crawl')