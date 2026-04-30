# automated_client_tests.py

import socket
import base64
import time

HOST = '127.0.0.1'
PORT = 8000
BUF_SIZE = 1024


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


def send_request(request, description):
    """Send a request and print the response with description"""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(request)
            response = s.recv(BUF_SIZE)
            print(response.decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"ERROR: {e}")
    
    time.sleep(0.1)  # Small delay between requests


def main():
    print("Starting automated HTTP client tests...")
    print(f"Connecting to {HOST}:{PORT}")
    
    # GET Tests
    send_request(GET("/user/file1.txt"), "GET - Successful (200) request")
    send_request(GET("/user/nonexistentfile.txt"), "GET - Not Found (404) request")
    
    # HEAD Tests
    send_request(HEAD("/user/file1.txt"), "HEAD - Successful (200) request")
    send_request(HEAD("/user/nonexistentfile.txt"), "HEAD - Not Found (404) request")
    
    # POST Tests
    send_request(POST("water:bottle", "/simple_form"), "POST - Successful (201) request")
    send_request(POST("water:bottle", "/user"), "POST - Bad Request (400) - non-/simple_form path")
    send_request(POST("water", "/simple_form"), "POST - Bad Request (400) - no colon in body")
    send_request(POST("water::bottle", "/simple_form"), "POST - Bad Request (400) - multiple colons")
    
    # PUT Tests
    send_request(PUT("This is the content of the file.", "/user/myfile.txt"), 
                 "PUT - Created (201) - new file")
    send_request(PUT("Short", "/user/myfile.txt"), 
                 "PUT - Success (200) - overwrite existing file")
    send_request(PUT("Invalid content", "/invalid_dir/myfile.txt"), 
                 "PUT - Bad Request (400) - invalid directory")
    send_request(PUT("No filename", "/user/"), 
                 "PUT - Bad Request (400) - no filename")
    
    # DELETE Tests
    send_request(DELETE("/del.txt", "example.com", "mike", "password"), 
                 "DELETE - Forbidden (403) - file not in user directory")
    send_request(DELETE("/user/notexist.txt", "example.com", "mike", "password"), 
                 "DELETE - Not Found (404) - file does not exist")
    send_request(DELETE("/user/del.txt", "example.com", "mike", "wrongpassword"), 
                 "DELETE - Unauthorized (401) - invalid password")
    send_request(DELETE("/user/del.txt", "example.com", "mo", "password"), 
                 "DELETE - Unauthorized (401) - invalid username")
    send_request(DELETE("/user/del.txt", "example.com", "mike", "password"), 
                 "DELETE - Success (200)")
    
    # INVALID Test
    send_request(INVALID(), "INVALID - Method Not Allowed (405)")
    
    print(f"\n{'='*70}")
    print("All tests completed!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()