from socket import *
import socket
import os
import sys
import logging
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO)

class HttpServer:
    def proses(self, request):
        request = request.strip()
        parts = request.split(" ", 2)
        if not parts:
            return b"Error: Permintaan kosong"

        command = parts[0].upper()

        if command == "LIST":
            directory = parts[1] if len(parts) > 1 else "."
            if not os.path.isdir(directory):
                return f"Error: {directory} bukan direktori yang valid".encode()
            try:
                file_list = os.listdir(directory)
                return "\n".join(file_list).encode()
            except Exception as e:
                return f"Error: tidak bisa membaca directory: {e}".encode()

        elif command == "UPLOAD":
            if len(parts) < 3:
                return b"Error: format UPLOAD harus: UPLOAD filename content"
            filename = parts[1]
            content = parts[2]
            try:
                with open(filename, "w") as f:
                    f.write(content)
                return f"File {filename} berhasil diupload".encode()
            except Exception as e:
                return f"Error: gagal mengupload {filename}: {e}".encode()

        elif command == "DELETE":
            if len(parts) < 2:
                return b"Error: filename tidak diberikan untuk DELETE"
            filename = parts[1]
            if not os.path.exists(filename):
                return f"Error: {filename} tidak ditemukan".encode()
            try:
                os.remove(filename)
                return f"File {filename} berhasil dihapus".encode()
            except Exception as e:
                return f"Error: gagal menghapus {filename}: {e}".encode()
        else:
            return b"Error: perintah tidak dikenal"

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                d = data.decode()
                rcv += d
                print(f"[DEBUG] RCV dari {address}: {rcv!r}")
                if '\r\n' in rcv:
                    # Ambil hanya satu perintah pertama
                    request_line, _ = rcv.split('\r\n', 1)
                    hasil = httpserver.proses(request_line)
                    hasil = hasil + "\r\n\r\n".encode()
                    connection.sendall(hasil)
                    connection.close()
                    return
            else:
                break
        except OSError as e:
            logging.error(f"Error pada koneksi dari {address}: {e}")
            break
    connection.close()
    return

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(5)
    logging.info("Server berjalan di port 8889")

    with ProcessPoolExecutor(20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                logging.info(f"Koneksi dari: {client_address}")
                p = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(p)

                # Hitung proses aktif
                jumlah = sum(1 for i in the_clients if i.running())
                print("Jumlah proses aktif:", jumlah)
            except KeyboardInterrupt:
                logging.info("Server dihentikan dengan Ctrl+C")
                break

def main():
    Server()

if __name__ == "__main__":
    main()
