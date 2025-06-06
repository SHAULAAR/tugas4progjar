import socket
import logging
import ssl
import os

# Konfigurasi logging
logging.basicConfig(level=logging.WARNING)

# Alamat server
server_address = ('localhost', 8889)

def make_socket(destination_address='localhost', port=8889):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = (destination_address, port)
        logging.warning(f"Menghubungkan ke {server_addr}")
        sock.connect(server_addr)
        return sock
    except Exception as e:
        logging.warning(f"Kesalahan saat membuat socket: {str(e)}")
        return None

def make_secure_socket(destination_address='localhost', port=8889):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = (destination_address, port)
        logging.warning(f"Menghubungkan ke {server_addr} dengan SSL")
        sock.connect(server_addr)
        secure_sock = context.wrap_socket(sock, server_hostname=destination_address)
        return secure_sock
    except Exception as e:
        logging.warning(f"Kesalahan saat membuat secure socket: {str(e)}")
        return None

def send_command(command_str, is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]

    # Pastikan perintah diakhiri dengan \r\n
    if not command_str.endswith("\r\n"):
        command_str += "\r\n"

    sock = make_secure_socket(alamat_server, port_server) if is_secure else make_socket(alamat_server, port_server)
    
    if sock is None:
        logging.warning("Gagal membuat koneksi ke server.")
        return None

    try:
        logging.warning(f"Mengirim perintah: {command_str.strip()}")
        sock.sendall(command_str.encode())

        # Terima data sampai ditemukan \r\n\r\n sebagai akhir response
        buffer = ""
        while True:
            data = sock.recv(2048)
            if not data:
                break
            buffer += data.decode()
            if "\r\n\r\n" in buffer:
                break

        # Hapus \r\n\r\n dari akhir jika ingin
        return buffer.strip()
    except Exception as e:
        logging.warning(f"Kesalahan saat mengirim/menerima: {str(e)}")
        return None
    finally:
        sock.close()

if __name__ == '__main__':
    # Contoh pemakaian
    print("=== Client Command Tester ===")
    print("Contoh: LIST, UPLOAD nama.txt isinya, DELETE nama.txt")
    while True:
        try:
            cmd = input(">> ").strip()
            if not cmd:
                continue
            if cmd.lower() == "exit":
                break
            response = send_command(cmd, is_secure=False)
            print("Response from server:")
            print(response)
        except KeyboardInterrupt:
            print("\nKeluar dari client.")
            break