import socket
from urllib.parse import urlsplit
import time

cache = {}

def create_dns_message(address):
    dns_message = b''  # Header
    dns_message += b'\xab\xcd'  # ID
    dns_message += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'  # Question
    address = address.split('.')

    for a in address:
        dns_message += bytes([len(a)]) + a.encode('ascii')
    dns_message += b'\x00'  # NULL
    dns_message += b'\x00\x01'  # Question Type
    dns_message += b'\x00\x01'  # Question Class
    return dns_message

def process_dns(response, resp_size):
    r_code = response[3] & 0x0f
    if r_code != 0:
        print("[error] RCode =", r_code)
        return

    an_count = int(response[6:8].hex(), 16)
    if an_count == 0:
        print("[error]: ANCount = 0")
        return

    i = resp_size
    while response[i] != 0xc0 and response[i] != 0x00:
        i += 1

    if response[i] == 0xc0:
        i += 2
    else:
        i += 1

    type = int(response[i:i+2].hex(), 16)
    assert type == 1, "Expected Value: 1"

    rclass = int(response[i+2:i+4].hex(), 16)

    ttl = int(response[i+4:i+8].hex(), 16)
    expires = time.time() + ttl

    rd_length = int(response[i+8:i+10].hex(), 16)
    assert rd_length == 4, "Expected value : 4"

    r_data = response[i+10:i+10+rd_length]

    ip_address = '.'.join([f'{i}' for i in r_data])
    print("r_code={}, an_code={}, type={}, rd_length={}, r_data={}, ip_address={}, ttl={}, expires={}".format(r_code, an_count, type, rd_length, r_data, ip_address, ttl, time.ctime(expires)))
    return ip_address, expires


def dns_socket(netloc):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))  # 81.180.223.1
        dns_msg = create_dns_message(netloc)
        s.sendall(dns_msg)
        response = s.recv(512)
        print('\n')
        print(response)
        ip_address = process_dns(response, len(dns_msg))
    except:
        return None
    finally:
        s.close()

    return ip_address


def dns_client(netloc):
    if netloc in cache and time.time() < cache[netloc][1]:
        return cache[netloc][0]

    ip, expires = dns_socket(netloc)
    cache[netloc] = [ip, expires]
    print(cache)
    return ip

if __name__ == "__main__":

    url_tibeica = 'http://riweb.tibeica.com'
    dns_client(urlsplit(url_tibeica).netloc)

    url_tuiasi = 'http://www.tuiasi.ro'
    dns_client(urlsplit(url_tuiasi).netloc)

