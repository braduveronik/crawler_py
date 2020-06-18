import socket
import os


def create_dns_message(address):

    dns_message = b''
    # Header
    dns_message += b'\xab\xcd' #ID
    dns_message += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' #
    # Question
    address = address.split('.')

    for a in address:
        dns_message += bytes([len(a)]) + a.encode('ascii')
    dns_message += b'\x00'      # NULL
    dns_message += b'\x00\x01'  # Question Type
    dns_message += b'\x00\x01'  # Question Class
    return dns_message

def create_html_message():

    request = 'GET /crawl/ HTTP/1.1\r\n'
    host = 'Host: riweb.tibeica.com\r\n'
    user_agent = 'User-Agent: CLIENT RIW\r\n'
    connection = 'Connection: close\r\n'
    return bytes(request + host + user_agent + connection + '\r\n','utf-8')


def process_dns(response):

    r_code = response[3] & 0x0f
    if r_code != 0:
        print("[error] RCode =", r_code)
        return

    an_count = int(response[6:8].hex(), 16)
    if an_count == 0:
        print("[error]: ANCount = 0")
        return

    name_end = response.find(0x00, 12) + 1 # line 12
    name = response[12:name_end]

    #c2 - if request{IP} => 1
    type = response[name_end: name_end + 2].hex()[-1]

    #if answer{ desired IPv4} => 4
    rd_length = response[-6:-4].hex()[-1]

    r_data = response[-4:].hex()

    ip_address =''
    for index in range(0,len(r_data),2):
        ip_address = ip_address + str(int(r_data[index:index + 2], 16)) + '.'
    print("r_code={}, an_code={}, name={}, type={}, rd_length={}, r_data={}, ip_address={}".format(r_code, an_count, name, type, rd_length, r_data, ip_address[:-1]))
    return  ip_address[:-1]

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 53))
    s.sendall(create_dns_message('riweb.tibeica.com'))

    response = s.recv(512)
    print(response)

    ip_address = process_dns(response)
    s.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((ip_address,80))
    message = create_html_message()
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
                content_length = int(response[lenght_start+1:lenght_stop])

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

                        print(response[257:end_response])
                    else:

                        output_dir = os.path.join('riweb.tibeica.com', 'crawl')
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        with open(output_dir+'/' +'crawl.html', 'w') as html:
                            html.write(response[257:end_response].replace('\\n', '&#10').replace('\\r', '&#13').replace('\\\'', ''))
                        break
        except:
            print('receive failed')
            break

    s.close()