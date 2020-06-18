import socket

def create_dns_message(address):
    msg = b''
    # Header
    msg += b'\xab\xcd' #ID
    msg += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' #
    # Question
    address = address.split('.')
    for a in address:
        msg += bytes([len(a)]) + a.encode('ascii')
    msg += b'\x00'      # NULL
    msg += b'\x00\x01'  # Question Type
    msg += b'\x00\x01'  # Question Class
    return msg


def process_dns(response):

    #a
    r_code = response[3] & 0x0f
    if r_code != 0:
        print("[error] RCode =", r_code)
        return
    #b
    an_count = int(response[6:8].hex(), 16)
    if an_count == 0:
        print("[error]: ANCount = 0")
        return

    #c
    #c1
    name_end = response.find(0x00, 12) + 1 # line 12
    name = response[12:name_end]

    #c2 - if request{IP} => 1
    type = response[name_end: name_end + 2].hex()[-1]

    #if answer{ desired IPv4} => 4
    rd_length = response[-6:-4].hex()[-1]

    # r_data = response[-4:].hex()
    r_data = response[-4:].hex()

    ip_address =''
    for index in range(0,len(r_data),2):
        ip_address = ip_address + str(int(r_data[index:index + 2], 16)) + '.'
    print("r_code={}, an_code={}, name={}, type={}, rd_length={}, r_data={}, ip_address={}".format(r_code, an_count, name, type, rd_length, r_data, ip_address[:-1]))

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 53))
    s.sendall(create_dns_message('riweb.tibeica.com'))

    # s.connect(('8.8.8.8', 53))
    # s.sendall(create_dns_message('www.google.com'))
    response = s.recv(512)
    print(response)
    process_dns(response)