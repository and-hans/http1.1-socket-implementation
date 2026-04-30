# Python Simplified HTTP Server

This repository contains a lightweight, custom-built server implemented in Python using raw sockets. It serves as an implementation of a simplified HTTP/1.1 protocol. This project was developed as part of Lab 2 for ECE358: Computer Networks.

## Overview

The goal of this project is to parse bytes sent between a client and a server to facilitate plain text data transfer. The server handles request parsing, validates headers, and issues appropriate HTTP responses and status codes based on the requested operations.

## Supported HTTP Methods

The server implements the following HTTP verbs:

* **GET:** Retrieves the raw bytes of a requested resource. Returns a `200 OK` on success or a `404 Not Found` if the file does not exist.
* **HEAD:** Functions identically to GET, but returns only the headers (including `Content-Length`) and omits the message body.
* **POST:** Processes incoming plain text data directed to the `simple_form` path. It parses a `username:description` formatted string and echoes the data back to the client.
* **PUT:** Allows clients to create new files or overwrite existing ones strictly within the `/user/` directory. 
* **DELETE:** Removes a specified resource from the `/user/` directory. This method implements a basic authentication scheme, requiring a base64 encoded username and password sent via the `Authorization: Basic` header, which is verified against a local `users.txt` file.

## Supported Status Codes

The server handles specific success and error states, intentionally omitting 5xx server errors for simplicity:

* **200 OK:** Request succeeded; response body contains the result.
* **201 Created:** New resource created successfully (used in POST and PUT).
* **400 Bad Request:** Request could not be understood due to malformed syntax.
* **401 Unauthorized:** Client authentication is missing or incorrect (used in DELETE).
* **403 Forbidden:** Client is authenticated but not allowed to perform the action (e.g., trying to delete outside the `/user/` folder).
* **404 Not Found:** Resource does not exist at the given URI.
* **405 Method Not Allowed:** The requested method is not supported by the server.

## Protocol Simplifications & Constraints

To focus on the core mechanics of HTTP, this implementation includes several specific constraints:

* **No Encryption:** Uses plain HTTP, not HTTPS.
* **Size Limits:** All messages (including headers and body) are restricted to a maximum length of 1024 bytes.
* **Data Type:** The server strictly transfers plain text in utf-8 format.
* **File System Roots:** The `/` path refers to the root directory of the server script, not the root of the host machine's file system.
* **Host Header:** While clients must format requests to include a `Host` header, the server parses it but does not implement multiple host routing.

## Usage

*(Note: Add your specific run commands here once your code is finalized)*

1. Clone the repository.
2. Ensure you have Python 3 installed.
3. Run the server script (e.g., `python3 your_server_file.py`), which binds to `localhost` (127.0.0.1) on port 8000.
4. Ensure a `users.txt` file and a `/user/` directory exist in the server's root folder for DELETE and PUT operations to function correctly.
