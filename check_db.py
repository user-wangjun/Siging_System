import socket, hashlib

def mysql_native_password(password, salt):
    if not password:
        return b''
    sha1_pass = hashlib.sha1(password.encode()).digest()
    sha1_pass2 = hashlib.sha1(sha1_pass).digest()
    sha1_salt = hashlib.sha1(salt + sha1_pass2).digest()
    return bytes(a ^ b for a, b in zip(sha1_pass, sha1_salt))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('8.138.171.197', 3306))
greeting = s.recv(1024)
null1 = greeting.find(b'\x00', 4)
version = greeting[4:null1].decode('latin-1')
print('MySQL version:', version)

pos = null1 + 5
auth_plugin_data_part1 = greeting[pos:pos+8]
pos += 9; pos += 16
auth_data_len = greeting[pos]
pos += 1; pos += 10; pos += 2
part2_len = max(13, auth_data_len - 8)
auth_plugin_data_part2 = greeting[pos:pos+part2_len]
null2 = auth_plugin_data_part2.find(b'\x00')
if null2 >= 0:
    auth_plugin_data_part2 = auth_plugin_data_part2[:null2]
salt = auth_plugin_data_part1 + auth_plugin_data_part2

# Try as root
auth_resp = mysql_native_password('LccjDyiGfCiwL2Az', salt)
cap = 1 | 512 | 32768
packet = b''
packet += cap.to_bytes(4, 'little')
packet += (16777215).to_bytes(4, 'little')
packet += b'\x2d'
packet += b'\x00' * 23
packet += b'root' + b'\x00'
packet += bytes([len(auth_resp)]) + auth_resp

header = len(packet).to_bytes(3, 'little') + b'\x01'
s.send(header + packet)
resp = s.recv(4096)
if resp[4] == 0x00:
    print('Root login OK! Creating database and user...')
    queries = [
        b'CREATE DATABASE IF NOT EXISTS event_system_cs DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;',
        b"CREATE USER IF NOT EXISTS 'event_system_cs'@'%' IDENTIFIED BY 'LccjDyiGfCiwL2Az';",
        b"GRANT ALL PRIVILEGES ON event_system_cs.* TO 'event_system_cs'@'%';",
        b'FLUSH PRIVILEGES;',
    ]
    for q in queries:
        s.send(b'\x01' + len(q).to_bytes(3, 'little') + b'\x00' + q)
        r = s.recv(4096)
        if r[4] == 0xff:
            err_len = r[5] + r[6]*256
            print('ERROR:', r[7:7+err_len].decode('latin-1', errors='replace'))
        else:
            print('OK:', q[:50].decode())
elif resp[4] == 0xff:
    err_len = resp[5] + resp[6]*256
    print('Root login failed:', resp[7:7+err_len].decode('latin-1', errors='replace'))
else:
    print('Unexpected response:', resp[:60].hex())

# Now test login as event_system_cs
s.close()

print('\n--- Testing event_system_cs login ---')
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.settimeout(10)
s2.connect(('8.138.171.197', 3306))
greeting2 = s2.recv(1024)
null1_2 = greeting2.find(b'\x00', 4)
pos2 = null1_2 + 5
auth_plugin_data_part1_2 = greeting2[pos2:pos2+8]
pos2 += 9; pos2 += 16
auth_data_len_2 = greeting2[pos2]
pos2 += 1; pos2 += 10; pos2 += 2
part2_len_2 = max(13, auth_data_len_2 - 8)
auth_plugin_data_part2_2 = greeting2[pos2:pos2+part2_len_2]
null2_2 = auth_plugin_data_part2_2.find(b'\x00')
if null2_2 >= 0:
    auth_plugin_data_part2_2 = auth_plugin_data_part2_2[:null2_2]
salt2 = auth_plugin_data_part1_2 + auth_plugin_data_part2_2

auth_resp2 = mysql_native_password('LccjDyiGfCiwL2Az', salt2)
cap2 = 1 | 512 | 32768 | 8
packet2 = b''
packet2 += cap2.to_bytes(4, 'little')
packet2 += (16777215).to_bytes(4, 'little')
packet2 += b'\x2d'
packet2 += b'\x00' * 23
packet2 += b'event_system_cs' + b'\x00'
packet2 += bytes([len(auth_resp2)]) + auth_resp2
packet2 += b'event_system_cs' + b'\x00'

header2 = len(packet2).to_bytes(3, 'little') + b'\x01'
s2.send(header2 + packet2)
resp2 = s2.recv(4096)
if resp2[4] == 0x00:
    print('event_system_cs login OK! Database is ready.')
elif resp2[4] == 0xff:
    err_len = resp2[5] + resp2[6]*256
    print('event_system_cs login failed:', resp2[7:7+err_len].decode('latin-1', errors='replace'))
s2.close()
print('Done')
