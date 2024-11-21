# SMTP Email Client and Server

A simple implementation of an SMTP (Simple Mail Transfer Protocol) client and server system written in Python.

## Overview

This project consists of two main components:
- `Client.py`: An SMTP client that sends emails
- `Server.py`: An SMTP server that receives and processes emails

## Features

- Email address validation
- Support for multiple recipients
- Basic SMTP command implementation (HELO, MAIL FROM, RCPT TO, DATA, QUIT)
- Error handling for various SMTP scenarios
- Local email storage in forward directory

## Requirements

- Python 3.x
- Socket library (built-in)
- Regular expressions library (built-in)

## Usage

### Starting the Server

1. Run the server script:
```python
python Server.py
```

2. The server will start listening on localhost:1025 by default

### Sending Emails via Client

1. Run the client script:
```python
python Client.py
```

2. Follow the interactive prompts to:
   - Enter sender email address
   - Enter recipient email address(es)
   - Enter email subject
   - Enter email content

## Configuration

Default settings can be modified in the respective files:

- Server port: Edit `SERVER_PORT` in Server.py
- Server host: Edit `SERVER_HOST` in Server.py
- Email storage location: Edit `FORWARD_PATH` in Server.py

## Error Codes

- 220: Service ready
- 250: Requested action completed
- 354: Start mail input
- 500: Syntax error
- 550: Requested action not taken

## Project Structure

```
smtp/
│
├── Client.py
├── Server.py
├── README.md
└── forward/
    └── (stored emails)
```
## Acknowledgments

- Based on RFC 5321 SMTP specifications
- Inspired by standard SMTP implementations