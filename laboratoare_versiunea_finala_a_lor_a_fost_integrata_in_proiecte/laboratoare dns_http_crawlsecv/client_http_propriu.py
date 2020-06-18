import socket
import shutil
import os

def create_html_message(site_ip, site_address):

    request = 'GET /crawl/ HTTP/1.1\r\n'
    host = 'Host: riweb.tibeica.com\r\n'
    user_agent = 'User-Agent: CLIENT RIW\r\n'
    connection = 'Connection: close\r\n'
    riw_request = request + host + user_agent + connection + '\r\n'

    return bytes(riw_request,'utf-8')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # dig @1.1.1.1 riweb.tibeica.com
    # telnet 67.207.88.228 80
    # site_ip trebuie obtinut din dns in faza de crawler
    site_ip = '67.207.88.228'
    site_address = 'http://riweb.tibeica.com/crawl/'

    s.connect((site_ip,80))
    message = create_html_message(site_ip,site_address)
    s.sendall(message)

    #Content-length-9316

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
                content_length = int(response[lenght_start+1:lenght_stop])

                doctype_index = int(response.find('\\r\\n\\r\\n'))
                recv_total = content_length + doctype_index

                if content_length > 0:
                    process_header = False
                    print('Content-Length: ' + str(content_length))
                    print('Total to recv: ' + str(recv_total))

            else:

                    if process_content:
                        #aici se opreste mereu la 8527
                        while len_resp < recv_total and '</HTML>' not in response:
                            resp = s.recv(1024)
                            len_resp += len(resp)
                            response += str(resp)
                            end_response = response.find('</HTML>')

                        process_content = False

                        print(response[257:end_response])
                    else:

                        parent_dir = 'riweb.tibeica.com'
                        child1_dir = 'crawl'
                        output_dir = os.path.join(parent_dir, child1_dir)

                        #nu vrea dir sa scrie in dir si path
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        with open('crawl.html', 'w') as html:
                            html.write(response[257:end_response].replace('\\n', '&#10').replace('\\r', '&#13').replace('\''))
                        break
        except:
            print('receive failed')
            break


