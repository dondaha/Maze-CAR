import socket

ip_address = '192.168.4.1'
port = 12345

if __name__ == '__main__':
    print("\r\nCommand format: <x,y,z,w>\r\nEnter q to quit\r\n")
    while True:
        cmd = input("Please enter a command: ")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(cmd.encode(), (ip_address, port))
        if cmd == 'q':
            break

        