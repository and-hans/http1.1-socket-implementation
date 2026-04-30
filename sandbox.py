import os
import re
import base64

users_pth: str = os.path.join(os.getcwd(), "user/users.txt")  # path to users.txt file
users = {}
with open(users_pth, 'r') as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(',')]
        if len(parts) == 2:
            user, value = parts
            users[user] = value

# print(users)

def DELETE(resource_path, resource_host="www.example.com", username=None, password=None):
    auth_line = ""
    if username is not None and password is not None:
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        auth_line = f"Authorization: Basic {token}\r\n"
    return (
        f"DELETE {resource_path} HTTP/1.1\r\n"
        f"Host: {resource_host}\r\n"
        f"{auth_line}\r\n"
    ).encode()

cop = DELETE("/files/file1.txt", "example.com", "user1", "password1")
# print(cop)

hop = cop.decode().split("\r\n")
cod = hop[2][21:]

# print(base64.b64decode(cod).decode())


VERBS = ["GET", "HEAD", "POST", "PUT", "DELETE"]
def parse_http_request(req: str) -> dict:
    """Parse HTTP request string and store each field in a dictionary.

    Args:
        req (str): request string.

    Returns:
        dict: organized reqeuest content.
    """
    content = {}
    # parse body and headers
    header, body = req.split("\r\n\r\n", 1)
    header_lines = header.split("\r\n")

    # parse request line
    request_line = header_lines[0].strip()
    verb = next((v for v in VERBS if request_line.startswith(v)), None)
    if verb:
        content["verb"] = verb
        match = re.search(rf'{verb}\s+(.*?)\s+HTTP/1\.1', request_line)
        if match:
            content["resource_path"] = match.group(1)

    # parse headers
    for line in header_lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            content[key.strip()] = value.strip()

    # add body
    content["body"] = body.strip()

    return content

put_request = (
        "PUT /user/myfile.txt HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "Content-Type: text/plain \r\n"
        "Content-Length: 3\r\n"
        "\r\n"
        "abc"
    ).encode("utf-8")

get_request = (
        "GET /user/users.txt HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    ).encode("utf-8")

post_request = (
        "POST /simple_form HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "Content-Type: text/plain \r\n"
        "Content-Length: 10\r\n"
        "\r\n"
        "sponge:bob"
    ).encode("utf-8")

delete_request = DELETE("/user/newfile.txt", "example.com", "user1", "password1")

head_request = (
        "HEAD /user/users.txt HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    ).encode("utf-8")

parsed_request = parse_http_request(delete_request.decode())
auth_header = parsed_request.get("Authorization", "")
cred = auth_header.split(" ")[1] if auth_header else ""
cred_decoded = base64.b64decode(cred).decode() if cred else ""

# print(cred_decoded.split(":", 1))  # prints the base64 encoded credentials
rsrc = os.path.join(os.getcwd(), parsed_request["resource_path"])
rsrc_dir = os.path.split(rsrc)[0]
# print(rsrc_dir)  # prints the resource path

parsed_request = parse_http_request(post_request.decode())
print(parsed_request)