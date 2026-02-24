import socket
import struct
import time

def get_ntp_time(host="pool.ntp.org"):
    port = 123
    buf = 1024
    address = (host, port)
    msg = '\x1b' + 47 * '\0'

    # connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
    try:
        client.sendto(msg.encode('utf-8'), address)
        msg, address = client.recvfrom(buf)
        t = struct.unpack("!12I", msg)[10]
        t -= 2208988800 # 1970-01-01 00:00:00
        return time.ctime(t)
    except Exception as e:
        return str(e)

print(get_ntp_time())
