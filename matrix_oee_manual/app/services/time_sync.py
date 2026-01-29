import socket
import struct
import time
from datetime import datetime, timedelta

def get_network_time(host="pool.ntp.org"):
    """
    Fetches the current time from an NTP server.
    Returns a datetime object.
    Falls back to system time if connection fails.
    """
    port = 123
    buf = 1024
    address = (host, port)
    msg = '\x1b' + 47 * '\0'
    
    # 1970-01-01 00:00:00
    TIME1970 = 2208988800

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(1.0) # Fast timeout
    
    try:
        client.sendto(msg.encode('utf-8'), address)
        msg, address = client.recvfrom(buf)
        t = struct.unpack("!12I", msg)[10]
        t -= TIME1970
        return datetime.fromtimestamp(t)
    except Exception as e:
        print(f"NTP Error: {e}, using system time.")
        return datetime.now()

if __name__ == "__main__":
    print("Network Time:", get_network_time())
