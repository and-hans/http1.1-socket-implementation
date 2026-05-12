# server_starter.py
# Code Written by Andrew Hansraj (20884857) for ECE358 Lab 2
import socket
import os
import re
import base64

HOST = '127.0.0.1' # DO NOT CHANGE THIS
PORT = 8000 # DO NOT CHANGE THIS
BUF_SIZE = 1024  # hard-coded message size limit
SERVER_ROOT = os.getcwd()  # server root directory
VERBS = ["GET", "HEAD", "POST", "PUT", "DELETE"]  # HTTP verbs

# read users from users.txt into a dictionary
users_pth: str = os.path.join(os.getcwd(), "users.txt")  # path to users.txt file
auth_users = {}
with open(users_pth, 'r') as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(',')]
        if len(parts) == 2:
            user, value = parts
            auth_users[user] = value


def process_head(content: dict) -> str:
    """Process HEAD HTTP requests.

    Args:
        content (dict): request content dictionary.

    Returns:
        str: response string.
    """        
    success: int = 0  # success flag (0 if fail, 1 if success)
    file_pth: str = os.path.join(os.getcwd(), content["resource_path"])  # construct file path
    
    try:
        # open file and retrieve contents
        with open(file_pth, 'r') as file:  # status code 200
            _ = file.read()  # read file contents
        success = 1  # raise sucess flag 
    except FileNotFoundError:
        # print(f"Error: The file '{file_pth}' was not found.")  # status code 404
        success = 0  # reset success flag if file not found
    except Exception as e:
        # print(f"An error occurred: {e}")
        success = 0  # reset success flag if other error occurs
    
    # create return string
    ret_str: str = f"HTTP/1.1 {'200 OK' if success else '404 Not Found'}\r\n" + \
    "Content-Type: text/plain\r\n"

    return ret_str


def process_get(content: dict) -> str:
    """Process GET HTTP requests.

    Args:
        content (dict): request content dictionary.

    Returns:
        str: response string.
    """
    file_contents: str = ""
    success: int = 1  # success flag (0 if fail, 1 if success)

    if ".." in content["resource_path"] or content["resource_path"].startswith("/"):
        file_contents = "404 Not Found"
        success = 0  # reset success flag if path traversal or absolute path detected
    else:
        file_pth: str = os.path.join(os.getcwd(), content["resource_path"])  # construct file path

        if not os.path.abspath(file_pth).startswith(os.getcwd()):
            file_contents = "404 Not Found"
            success = 0  # reset success flag if path traversal detected
        else:
            try:
                # open file and retrieve contents
                with open(file_pth, 'r', encoding="utf-8") as file:  # status code 200
                    file_contents = file.read()  # read file contents
                success = 1  # raise sucess flag 
            except FileNotFoundError:
                # print(f"Error: The file '{file_pth}' was not found.")
                file_contents = "404 Not Found"
                success = 0  # reset success flag if file not found
            except Exception as e:
                # print(f"An error occurred: {e}")
                file_contents = "404 Not Found"
                success = 0  # reset success flag if other error occurs
    
    # create return string
    ret_str: str = f"HTTP/1.1 {'200 OK' if success else '404 Not Found'}\r\n" + \
    f"Content-Length: {len(file_contents)}\r\n" + \
    "Content-Type: text/plain\r\n" + \
    "\r\n" + \
    f"{file_contents}"
    
    return ret_str


def process_post(content: dict) -> str:
    """Process POST HTTP requests.

    Args:
        content (dict): request content dictionary.

    Returns:
        str: response string.
    """    
    success: int = 1  # success flag (0 if fail, 1 if success)

    # validate Content-Type header
    if "Content-Type" not in content or content["Content-Type"] != "text/plain":
        success = 0

    # check body format and resource path 
    if content["body"].count(":") != 1:
        success = 0  # reset success flag if not exactly one colon present
    if (content["resource_path"] != "simple_form"):
        success = 0  # reset success flag if incorrect resource path
    
    # split the body into username and description components
    match = re.match(r'^(.*?)\s*:\s*(.*)$', content["body"])
    if match:
        username = match.group(1)
        description = match.group(2)
    else:
        success = 0  # reset success flag if body format is incorrect
    
    # construct body string
    if success:
        body_str: str = f"Name is: {username} and Description is {description}"
    else:
        body_str: str = "400 Bad Request"
    
    # construct response string
    ret_str: str = f"HTTP/1.1 {'200 OK' if success else '400 Bad Request'}\r\n" + \
    "Content-Type: text/plain\r\n" + \
    f"Content-Length: {len(body_str)}\r\n" + \
    "\r\n" + \
    f"{body_str}"

    return ret_str


def process_put(content: dict) -> str:
    """Process PUT HTTP requests.

    Args:
        content (dict): request content dictionary.

    Returns:
        str: response string.
    """
    success: int = 1  # success flag (0 if fail, 1 if success, 2 if file overwritten)
    # parse resource path
    rsrc_path_parts = content["resource_path"].strip("/").split("/")

    # check if requested directory is valid 
    if rsrc_path_parts[0] != "user":
        success = 0  # reset success flag if not in /user directory
    elif len(rsrc_path_parts) == 1:  # only /user provided, no filename
        success = 0  # reset success flag if filename not provided
    else:
        filename = rsrc_path_parts[-1]  # get filename from resource path
        if not filename or filename in [".", ".."]:
            success = 0  # reset success flag if invalid filename
        elif "/" in filename or "\0" in filename or "\\" in filename:
            success = 0  # reset success flag if filename contains path separators
    
    # proceed only if checks passed
    if success:
        file_pth: str = os.path.join(os.getcwd(), *rsrc_path_parts)  # construct file path
        # check if file exists to determine if it will be created or overwritten
        if os.path.exists(file_pth):
            success = 2  # set success flag to 2 if file will be overwritten
        else:
            success = 1  # set success flag to 1 if file will be created

        try:
            # write body content to file
            with open(file_pth, 'w') as file:
                file.write(content["body"])
        except Exception as e:
            # print(f"An error occurred while writing the file: {e}")
            success = 0  # reset success flag if file write fails
    
    # construct body string
    if success == 1:
        body_str: str = "201 Created"
    elif success == 2:
        body_str: str = "200 OK"
    else:
        body_str: str = "400 Bad Request"
    
    # construct response string
    ret_str: str = f"HTTP/1.1 {body_str}\r\n" + \
    "Content-Type: text/plain\r\n" + \
    f"Content-Length: {len(body_str)}\r\n" + \
    "\r\n" + \
    f"{body_str}"

    return ret_str


def process_delete(content: dict) -> str:
    """Process DELETE HTTP requests.

    Args:
        content (dict): request content dictionary.

    Returns:
        str: response string.
    """        
    success: int = 1  # success flag (0 if fail, 1 if success, 2 if auth fail, 3 if invalid directory)
    file_pth: str = os.path.join(os.getcwd(), content["resource_path"])  # construct file path
    rsrc_dir = content["resource_path"].split("/")[0]  # get directory of resource path

    if ("Authorization" not in content):
        success = 2  # set success flag to 2 for auth failure
    else:
        try:
            # grab authentication credentials
            auth_header: str = content["Authorization"] # get Authorization header
            cred_enc: str = auth_header.split(" ")[1]  # extract base64 encoded credentials
            cred_dec: str = base64.b64decode(cred_enc).decode()  # decode base64 to get "username:password"
            username, password = cred_dec.split(":", 1)  # split into username and password
            
            # verify credentials and attempt file deletion
            if username in auth_users and auth_users[username] == password:
                if (rsrc_dir != "user"):
                    success = 3  # set success flag to 3 for invalid directory
                elif (os.path.exists(file_pth)):
                    os.remove(file_pth)  # delete the file if it exists and in /user directory
                    success = 1  # set success flag to 1 for successful deletion
                else:
                    # print(f"Error: The file '{file_pth}' was not found.")  # status code 404
                    success = 0  # set success flag to 0 for file not found
            else:
                # print("Authentication failed.")
                success = 2  # set success flag to 2 for auth failure
        except Exception as e:
            # print(f"Error parsing authorization: {e}")
            success = 2  # set success flag to 2 for auth failure
    
    # create return string based on success flag
    if success == 0:
        ret_status: str = "404 Not Found"
    elif success == 1:
        ret_status: str = "200 OK"
    elif success == 2:
        ret_status: str = "401 Unauthorized"
    else:
        ret_status: str = "403 Forbidden"

    # construct return string
    ret_str: str = f"HTTP/1.1 {ret_status}\r\n" + \
    "Content-Type: text/plain\r\n" + \
    f"Content-Length: {len(ret_status)}\r\n" + \
    "\r\n" + \
    f"{ret_status}"

    return ret_str


def parse_http_request(req: str) -> dict:
    """Parse HTTP request string and store each field in a dictionary.

    Args:
        req (str): request string.

    Returns:
        dict: organized reqeuest content.
    """
    content = {}

    # check if the request contains the required separator
    if "\r\n\r\n" not in req:
        content["verb"] = "INVALID"
        content["body"] = ""
        return content  # return dictionary for malformed request
    
    # parse body and headers
    header, body = req.split("\r\n\r\n", 1)
    header_lines = header.split("\r\n")

    # check if header lines are present
    if not header_lines:
        content["verb"] = "INVALID"
        content["body"] = ""
        return content  # return dictionary for malformed request

    # parse request line
    request_line = header_lines[0].strip()
    verb = next((v for v in VERBS if request_line.startswith(v)), None)
    if verb:
        content["verb"] = verb
        match = re.search(rf'{verb}\s+(.*?)\s+HTTP/1\.1', request_line)
        if match:
            content["resource_path"] = match.group(1)[1:]
        else:
            content["verb"] = "INVALID"
    else:
        content["verb"] = "INVALID"

    # parse headers
    for line in header_lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            content[key.strip()] = value.strip()

    # add body
    content["body"] = body.strip()

    return content


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f"Listening on {HOST}:{PORT}...")

        while True:
            conn, addr = srv.accept()
            try:
                data = conn.recv(BUF_SIZE)
                if not data:
                    continue
                # Decode to string and print to console - this is what you
                # will be working with to extract the HTTP request
                request_str = data.decode("utf-8", errors="replace")
                # print(request_str, end="")
                
                # Now you should put logic in here to see what kind of request it is, what the 
                # parameters are etc, and then call a function to handle the request correctly
                content = parse_http_request(request_str)  # parse the request

                # Process based on verb
                response_str: str = ""
                if content["verb"] == "GET":
                    response_str = process_get(content)
                elif content["verb"] == "HEAD":
                    response_str = process_head(content)
                elif content["verb"] == "POST":
                    response_str = process_post(content)
                elif content["verb"] == "PUT":
                    response_str = process_put(content)
                elif content["verb"] == "DELETE":
                    response_str = process_delete(content)
                else:
                    response_str = "HTTP/1.1 405 Method Not Allowed\r\n" + \
                    "Content-Type: text/plain\r\n" + \
                    "Content-Length: 22\r\n" + \
                    "\r\n" + \
                    "405 Method Not Allowed"
                
                # Send response back to client
                conn.sendall(response_str.encode("utf-8", errors="replace"))

                # Echo back exactly what was received (string re-encoded as bytes)
                # This is how you will send stuff back to the server once you
                # Properly format it
                # conn.sendall(request_str.encode("utf-8", errors="replace"))
            finally:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                conn.close()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        print("Server socket closed.")


if __name__ == "__main__":
    main()
