

from socket import *
import socket
import sys
import re 


# Globals
index = 0 
value = ""



CLIENTNAME = socket.gethostname()
# Error messages
ERROR500 = "500 Syntax error: command unrecognized"
ERROR501 = "501 Syntax error in parameters or arguments"
ERROR503 = "503 Bad sequence of commands"
# Data Message
DATA354 = "354 Start mail input; end with <CRLF>.<CRLF>"
# Ok Message
OK250 = "250 OK"



def main():
    global port_num, server_name, string, value, index, error

    try:
        server_name = sys.argv[1]
        port_num = sys.argv[2]
        connection = socket.socket(AF_INET, SOCK_STREAM)
        connection.connect((server_name, int(port_num)))
    except socket.error:
        print("Socket Creation/Connection Error")
        return

    # Receive 220 Message
    recv_220_message = connection.recv(2048).decode()
    if not re.compile('^220 .*$').match(recv_220_message):
        print("220 Error")
        send_message("QUIT", connection)
        return

    # Send HELO Message
    send_message("HELO " + CLIENTNAME, connection)

    # Receive 250 Response
    recv_250_message = receive_message(connection)
    if not re.compile('^250 .*$').match(recv_250_message):
        print("250 Error")
        send_message("QUIT", connection)
        return

    # Generate email
    text = generate_email()

    try:
        parse(text, connection)
    except UserWarning:
        print("SMTP protocol error encountered")
    finally:
        send_message("QUIT", connection)
        receive_message(connection)

def parse(text, socket):
    lines = text.split('\n')
    sender = lines[0].split("From: ")[1]
    send_message("MAIL FROM: " + sender, socket)
    if not re.compile('^250 .*$').match(receive_message(socket)):
        raise UserWarning("")

    recipients = re.split('^To: ', lines[1])[1].split(", ")
    for address in recipients:
        send_message("RCPT TO: " + address, socket)
        if not re.compile('^250 .*$').match(receive_message(socket)):
            raise UserWarning("")

    send_message("DATA", socket)
    if not re.compile('^354 .*$').match(receive_message(socket)):
        raise UserWarning("")

    send_message(text, socket)
    if not re.compile('^250 .*$').match(receive_message(socket)):
        raise UserWarning("")

def send_message(message, socket):
    message_text = message + "\n"
    socket.send(message_text.encode())

def receive_message(socket):
    decoded = socket.recv(2048).decode()
    decoded = re.split(r'\n$', decoded)[0]
    return decoded

def generate_email():
    text = ""
    sender_validated = 0
    while not sender_validated:
        sender = input("From:\n")
        try:
            validate_email_address(sender)
            text += "From: <" + sender + ">\n"
            sender_validated = 1
        except UserWarning:
            print("An invalid email address was entered. Please try again.")

    recipients_validated = 0
    while not recipients_validated:
        recipients = re.split(r',[ \t]*',input("To:\n"))
        try:
            for address in recipients:
                validate_email_address(address)
            text += "To: <" + ">, <".join(recipients) + ">\n"
            recipients_validated = 1
        except UserWarning:
            print("An invalid email address was entered. Please try again.")

    text += "Subject: " + input("Subject:\n") + "\n"
    next_line = input("Message:\n")
    while next_line != ".":
        text += "\n"
        text += next_line
        next_line = input()
    text += "\n."
    return text



def validate_email_address(email):
    global string, index, value, error

    string = email
    index = 0
    value = string[index]
    error = ''

    if not mailbox():
        raise UserWarning("Invalid email address: " + error)

def mailbox():
    global string, index, value, error
    if not local_part():
        if error == '':
            error = ERROR501
        return False

    if value != '@':
        if error == '':
            error = ERROR501
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return False

    if not domain():
        if error == '':
            error = ERROR501
        return False

    return True

def local_part():
    return string_check()

def string_check():
    global value, string, index, error
    if not char():
        if error == '':
            error = "string"
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return True

    if not string_check():
        error = ''

    return True

def space():
    global value
    return ((value == ' ') or (value == '\t'))

def special():
    global value
    special_chars: str = ['<', '>', '(', ')', '[', ']', '\\', '.', ',', ';', ':', '@', '\"']
    return value in special_chars

def char():
    return not (space() or special())

def domain():
    global string, index, value
    if not element():
        return False

    if value == '.':
        index += 1
        try:
            value = string[index]
        except IndexError:
            return False
        return domain()

    return True

def element():
    global value, string, index, error
    if not name():
        if error == '':
            error = ERROR501
        return False

    return True

def name():
    global value, string, index
    if not letter():
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return True

    let_dig_str()

    return True

def letter():
    global value
    return value.isalpha()

def let_dig_str():
    global value, string, index
    if not let_dig():
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return True

    let_dig_str()

    return True

def let_dig():
    return (letter() or digit())

def digit():
    global value
    return value.isnumeric()

main()

