#!/bin/python
import signal
import os
import sys
import socket
import select
import coverage
coverage.process_startup()

#Use this variable for your loop
daemon_quit = False

# Checking a port has been provided
if len(sys.argv) < 2:
    print("Need to input a port.")
    exit()

# Checking the port is valid
try:
    int(sys.argv[1])
except ValueError:
    print("Port must be an integer.")
    exit()

# Setting up the local IP and Port
IP = "127.0.0.1"
PORT = int(sys.argv[1])

# Creating the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))
server.listen()

#Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True


# Main function
def run():
    #Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)

    sockets_list = [server] # All current sockets connected to serever
    users = {}  # Dict of users and their corresponding sockets
    logins = {} # Dict of logins and passwords
    channels = [] # List of all channel names
    current_logins = [] # List of current logins
    channel_users = {}  # Dict of channels and users on those channels
    accepted_cmds = ["LOGIN", "REGISTER", "JOIN", "CREATE", "SAY", "RECV",
                      "CHANNELS"]

    # A function that sends a result message for the login and register commands
    def result_login_register(login_or_register, result, user_socket):
        return_message = "RESULT "
        return_message += login_or_register + " " + result + "\n"
        user_socket.send(return_message.encode('utf-8'))

    # A function that sends a result message for the join and create commands
    def result_join_create(join_or_create, channel, result, user_socket):
        return_message = "RESULT "
        return_message += join_or_create + " " + channel + " " + result + "\n"
        user_socket.send(return_message.encode('utf-8'))

    # A function that removes any disconnected sockets from given lists/dicts
    def connection_lost(user_socket):
        sockets_list.remove(user_socket)
        for channel in channel_users:
            if user_socket in channel_users[channel]:
                channel_users[channel].remove(user_socket)
        for user in users:
            if users[user] == user_socket:
                users[user] = ""
                current_logins.remove(user)

    # A function that sends a given error message
    def error_msg(user_socket, cmd):
        if cmd[0] == "JOIN":
            result_join_create("JOIN", cmd[1], "0", user_socket)
        elif cmd[0] == "CREATE":
            result_join_create("CREATE", cmd[1], "0", user_socket)
        elif cmd[0] == "SAY":
            return_message = "Please login first.\n"
            user_socket.send(return_message.encode('utf-8'))
        elif cmd[0] == "LOGIN":
            result_login_register("LOGIN", "0", user_socket)

    # Main loop
    while True:
        signal.signal(signal.SIGINT, quit_gracefully)
        if (daemon_quit):
            return
        # Waits for an incoming connection
        read_sockets, _, exception_sockets = select.select(sockets_list, [],
                                                            sockets_list, 0.1)

        for user_socket in read_sockets:
            try:
                if user_socket == server: # If it is a new connection
                    user_socket, client_address = server.accept()
                    sockets_list.append(user_socket)
                message = user_socket.recv(1024).decode('utf-8').strip()
            except ConnectionResetError:
                pass
            # If the connection is lost
            if message == "":
                connection_lost(user_socket)
                continue

            # Splitting the command into a list
            cmd = message.split(" ")
            if cmd[0] not in accepted_cmds: # Checking the command is valid
                return_message = "Please provide a valid command.\n"
                user_socket.send(return_message.encode('utf-8'))
                continue

            # Checking if their are any users regiestered
            if ((len(logins) == 0) and (cmd[0] != "CHANNELS") and
                (cmd[0] != "REGISTER")):
                error_msg(user_socket, cmd)
                continue

            # Checking if the user is logged in for certain commands
            logged_in = False
            for user in users:
                if users[user] == user_socket:
                    logged_in = True
            if logged_in == False:
                 if ((cmd[0] != "CHANNELS") and (cmd[0] != "REGISTER") and
                    (cmd[0] != "LOGIN")):
                      error_msg(user_socket, cmd)
                      continue
            try:
                # If the command is login
                if cmd[0] == "LOGIN":
                    if (len(logins) == 0):  # If their are no registered users
                        result_login_register("LOGIN", "0", user_socket)
                        continue
                    if len(cmd) != 3: # If the command isn't correct
                        result_login_register("LOGIN", "0", user_socket)
                        continue
                    # If the user is already logged in or the user doesn't exist
                    if (cmd[1] not in logins) or (cmd[1] in current_logins):
                        result_login_register("LOGIN", "0", user_socket)
                        continue
                    login_fail = False
                    for user in users:
                        # If the current socket is already logged in
                        if users[user] == user_socket:
                            result_login_register("LOGIN", "0", user_socket)
                            login_fail = True
                    if login_fail:
                        continue
                    if hash(cmd[2]) != logins[cmd[1]]:  # Incorrect password
                        result_login_register("LOGIN", "0", user_socket)
                        continue
                    else:
                        # Log in
                        current_logins.append(cmd[1])
                        users[cmd[1]] = user_socket
                        result_login_register("LOGIN", "1", user_socket)

                # If the command is register
                elif cmd[0] == "REGISTER":
                    if len(cmd) != 3: # If the command isn't correct
                        result_login_register("REGISTER", "0", user_socket)
                        continue
                    if cmd[1] in logins:  # If username already exists
                        result_login_register("REGISTER", "0", user_socket)
                        continue
                    logins[cmd[1]] = hash(cmd[2]) # Register the new user
                    result_login_register("REGISTER", "1", user_socket)

                # If the command is join
                elif cmd[0] == "JOIN":
                    if len(cmd) != 2: # If the command isn't correct
                        result_join_create("JOIN", "N/A", "0", user_socket)
                        continue
                    if cmd[1] not in channels:  # If the channel doesn't exist
                        result_join_create("JOIN", cmd[1], "0", user_socket)
                        continue
                    join_channel = True
                    for channel in channel_users:
                        if cmd[1] == channel:
                            for socket in channel_users[channel]:
                                # If the user is already in this channel
                                if user_socket == socket:
                                    join_channel = False
                    if not join_channel:  # Send the given error message
                        result_join_create("JOIN", cmd[1], "0", user_socket)
                        continue
                    # Otherwise, join the channel
                    channel_users[cmd[1]].append(user_socket)
                    result_join_create("JOIN", cmd[1], "1", user_socket)
                    continue

                # If the command is create
                elif cmd[0] == "CREATE":
                    if len(cmd) != 2: # If the command isn't correct
                        result_join_create("CREATE", "N/A", "0", user_socket)
                        continue
                    if cmd[1] in channels:
                        result_join_create("CREATE", cmd[1], "0", user_socket)
                        continue
                    channel_users[cmd[1]] = []
                    channels.append(cmd[1])
                    result_join_create("CREATE", cmd[1], "1", user_socket)

                # If the command is say
                elif cmd[0] == "SAY":
                    if len(cmd) < 3:
                        return_message = "Incorrect command.\n"
                        user_socket.send(return_message.encode('utf-8'))
                        continue
                    channel_exists = False
                    user_in_channel = False
                    for user in users:
                        # Who is sending the message
                        if users[user] == user_socket:
                            sender = user
                    for channel in channels:
                        if cmd[1] == channel:
                            channel_exists = True
                            # If the user is not in the given channel
                            if user_socket in channel_users[channel]:
                                user_in_channel = True


                            msg = cmd[2] + "\n"
                            # If the message is more than one word
                            if len(cmd) > 3:
                                msg = ""
                                i = 2
                                while (i < len(cmd)):
                                    msg += (cmd[i] + " ")
                                    i+=1
                                msg = msg[:-1] + "\n"
                            # Concatenating the message
                            return_message = "RECV "+sender+" "+channel+" "+msg
                            # Send the message to everyone in the channel
                            for socket in channel_users[channel]:
                                socket.send(return_message.encode('utf-8'))

                    # If the channel doesn't exist
                    if not channel_exists:
                        reuturn_message = "Channel does not exist.\n"
                        user_socket.send(reuturn_message.encode('utf-8'))
                        continue
                    # If the user isn't in the channel
                    if not user_in_channel:
                        return_message = ("User has not joined this "
                                          "channel.\n")
                        user_socket.send(return_message.encode
                                        ('utf-8'))
                        continue

                # If the command is channels
                elif cmd[0] == "CHANNELS":
                    channel_ls = ""
                    # Sorting the list alphabetically
                    sorted_channels = sorted(channels)
                    # Concatenating the channel names into one string
                    for channel in sorted_channels:
                        channel_ls += (channel + ", ")
                    channel_ls = channel_ls[:-2] + "\n"
                    # Sending the message to the user
                    return_message = "RESULT CHANNELS " + channel_ls
                    user_socket.send(return_message.encode('utf-8'))

            except BrokenPipeError:
                connection_lost(user_socket)

if __name__ == '__main__':
    run()
