
from socket import *
import socket
import sys
import os
import re 
from time import sleep

# Error messages
ERROR_500 = "500 Syntax error: command unrecognized"
ERROR_501 = "501 Syntax error in parameters or arguments"
ERROR_503 = "503 Bad sequence of commands"

# Data message
DATA_354 = "354 Start mail input; end with <CRLF>.<CRLF>"

# Ok message
OK_250 = "250 OK"

def parse_command(cmd, sock):
    global prev_cmd
    if cmd.startswith("HELO"):
        prev_cmd = "DATA"
        handle_helo(cmd, sock)
    elif cmd.startswith("MAIL FROM:"):
        if prev_cmd != "DATA":
            raise Exception(ERROR_503)
        else:
            handle_mail_from(cmd, sock)
    elif cmd.startswith("RCPT TO:"):
        if prev_cmd == "DATA":
            raise Exception(ERROR_503)
        else:
            handle_rcpt_to(cmd, sock)
    elif cmd.startswith("DATA"):
        if prev_cmd != "TO":
            raise Exception(ERROR_503)
        else:
            handle_data(cmd, sock)
    elif cmd.startswith("QUIT"):
        send_msg("221 " + gethostname() + " closing connection", sock)
        global quit_flag
        quit_flag = 1
        sock.close()
    else:
        raise Exception(ERROR_500)

def handle_helo(cmd, sock):
    parts = re.split(r'^HELO[ \t]+', cmd)
    domain = re.split(r'[ \t\n]', parts[1])[0]
    send_msg("250 Hello " + domain + " pleased to meet you", sock)

def handle_mail_from(cmd, sock):
    parts = re.split(r'^MAIL[ \t]+FROM:', cmd)
    address = nullspace(parts[1])
    address = get_path(address)
    address = add_crlf(address)
    global prev_cmd
    prev_cmd = "FROM"
    result= "From: <" + cmd.split("<")[1].split(">")[0] + ">\n"
    send_msg(OK_250, sock)

def handle_rcpt_to(cmd, sock):
    parts = re.split(r'^RCPT[ \t]+TO:', cmd)
    address = nullspace(parts[1])
    address = get_path(address)
    address = add_crlf(address)
    email_addr = cmd.split("<")[1].split(">")[0]
    global prev_cmd
    prev_cmd = "TO"
    result = "To: <" + email_addr + ">\n"
    domain = email_addr.split("@")[1]
    global recipient_list
    if domain not in recipient_list.split('\n'):
        recipient_list += domain
        recipient_list += "\n"
    send_msg(OK_250, sock)

def handle_data(cmd, sock):
    if not re.compile(r'^DATA[ \t]*$').match(cmd):
        raise Exception(ERROR_500)
    global prev_cmd
    prev_cmd = "DATA"
    send_msg(DATA_354, sock)
    global email_body
    global recipient_list
    done = 0
    while not done:
        text = receive_msg(sock)
        lines = text.split("\n")
        while lines:
            curr_line = lines.pop(0)
            if curr_line == ".":
                done = 1
            else:
                email_body += curr_line + "\n"
    paths = recipient_list.split("\n")
    for path in paths:
        if path:
            try:
                file_path = re.split(r'Server.py$', sys.argv[0])[0] + "forward/" + path
                with open(file_path, 'a') as file:
                    file.write(email_body)
            except IOError:
                print("File error")
                sys.exit()
    email_body = ""
    recipient_list = ""
    send_msg(OK_250, sock)





def nullspace(x):
    if not re.compile('^[ \t]+').match(x):
        return x
    return re.split(r'^[ \t]+', x)[1]


def get_path(string):
    if not re.compile(r'^<').match(string):
        raise Exception(ERROR_501)
    string = re.split(r'^<', string)[1]
    string = get_mailbox(string)
    if not re.compile(r'^>').match(string):
        raise Exception(ERROR_501)
    string = re.split(r'^>', string)[1]
    return string

def get_mailbox(string):
    string = get_local_part(string)
    if not re.compile(r'^@').match(string):
        raise Exception(ERROR_501)
    string = re.split(r'^@', string)[1]
    string = get_domain(string)
    return string

def get_local_part(string):
    if not re.compile(r'^[^ \t<>()\[\]\\.,;:@\"]+').match(string):
        raise Exception(ERROR_501)
    return re.split(r'^[^ \t<>()\[\]\\.,;:@\"]+', string)[1]

def get_domain(string):
    string = get_element(string)
    while re.compile(r'^\.').match(string):
        string = re.split(r'^\.', string)[1]
        string = get_element(string)
    return string

def get_element(string):
    if not re.compile(r'^[a-zA-Z][a-zA-Z0-9]*').match(string):
        raise Exception(ERROR_501)
    return re.split(r'^[a-zA-Z][a-zA-Z0-9]*', string)[1]

def add_crlf(string):
    if not re.compile(r'^[ \t]*$').match(string):
        raise Exception(ERROR_501)
    return string

def send_msg(message, sock):
    msg_text = message + "\n"
    print("SERVER: {" + msg_text + "}")
    sock.send(msg_text.encode())

def receive_msg(sock):
    decoded = sock.recv(2048).decode()
    print("CLIENT: {" + decoded + "}")
    decoded = re.split(r'\n$', decoded)[0]
    return decoded

def greet(sock):
    send_msg("220 " + gethostname(), sock)

try:
    server_port = int(sys.argv[1])
    server_socket = socket.socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
except OSError:
    print("Port bind error")
    sys.exit()
server_socket.listen(1)

prev_cmd = None
email_body = ""
recipient_list = ""
quit_flag = 0

while True:
    try:
        conn_socket, addr = server_socket.accept()
        quit_flag = 0
        greet(conn_socket)
        while not quit_flag:
            message = receive_msg(conn_socket)
            try:
                parse_command(message, conn_socket)
            except Exception as e:
                prev_cmd = "DATA"
                email_body = ""
                if e.args[0] == ERROR_500:
                    error_msg = ERROR_500
                elif e.args[0] == ERROR_501:
                    error_msg = ERROR_501
                elif e.args[0] == ERROR_503:
                    error_msg = ERROR_503
                send_msg(error_msg, conn_socket)
    except ConnectionError:
        print("There was a connection error")
    finally:
        prev_cmd = None
        email_body = ""
        recipient_list = ""
        quit_flag = 0