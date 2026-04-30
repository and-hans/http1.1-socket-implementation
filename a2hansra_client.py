# client_starter.py

import socket
import base64  # imported as required

HOST = '127.0.0.1'
PORT = 8000
BUF_SIZE = 1024  # hard-coded message size limit


def DELETE(resource_path: str, resource_host: str="www.example.com", username=None, password=None):
    auth_line = ""
    if username is not None and password is not None:
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        auth_line = f"Authorization: Basic {token}\r\n"
    return (
        f"DELETE {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"{auth_line}\r\n"
    ).encode("utf-8")


def GET(resource_path: str, resource_host: str="www.example.com"):
    return (
        f"GET {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"\r\n"
    ).encode("utf-8")


def HEAD(resource_path: str, resource_host: str="www.example.com"):
    return (
        f"HEAD {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"\r\n"
    ).encode("utf-8")


def PUT(body: str, resource_path: str, resource_host: str="www.example.com"):
    return (
        f"PUT {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    ).encode("utf-8")


def POST(body: str, resource_path: str, resource_host: str="www.example.com"):
    return (
        f"POST {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    ).encode("utf-8")


def INVALID():
    return (
        "GAME /user HTTP/1.1\r\n"
        "Host: www.example.com\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 3\r\n"
        "\r\n"
        "abc"
    ).encode("utf-8")


def main():
    # request = GET("/user/file1.txt")  # successful (200) GET request
    # request = GET("/user/nonexistentfile.txt")  # unsuccessful (404) GET request

    # request = HEAD("/user/file1.txt")  # successful (200) HEAD request
    # request = HEAD("/user/nonexistentfile.txt")  # unsuccessful (404) HEAD request

    # request = POST("water:bottle", "/simple_form")  # successsful (201) POST request
    # request = POST("water:bottle", "/user")  # unsuccessful (400) POST request (to non-/simple_form path)
    # request = POST("water", "/simple_form")  # unsuccessful (400) POST request (no colon in body)
    # request = POST("water::bottle", "/simple_form")  # unsuccessful (400) POST request (no colon in body)

    # request = PUT("This is the content of the file.", "/user/myfile.txt")  # successful (201) PUT request (creating new file)
    # request = PUT("Short", "/user/myfile.txt")  # successful (200) PUT request (overwriting existing file)
    # request = PUT("Invalid content", "/invalid_dir/myfile.txt")  # unsuccessful (400) PUT request (invalid directory)
    # request = PUT("No filename", "/user/")  # unsuccessful (400) PUT request (no provided filename)

    # request = DELETE("/del.txt", "example.com", "mike", "password")  # unsuccessful (403) DELETE request (file not in user directory)
    # request = DELETE("/user/notexist.txt", "example.com", "mike", "password")  # unsuccessful (404) DELETE request (file does not exist)
    # request = DELETE("/user/del.txt", "example.com", "mike", "wrongpassword")  # unsuccessful (401) DELETE request (invalid password)
    # request = DELETE("/user/del.txt", "example.com", "mo", "password")  # unsuccessful (401) DELETE request (invalid username)
    # request = DELETE("/user/del.txt", "example.com", "mike", "password")  # successful (200) DELETE request

    request = INVALID()  # malformed (405) request

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request)
        response = s.recv(BUF_SIZE)
        print(response.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
