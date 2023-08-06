import functools

from dictionaries import commands_dict
from data import *


def register_command(func):
    commands_dict[func.__name__] = func
    return func


@register_command
def send_message(sender_info, *args):
    get_data = SendMessageData(*args)
    message = get_data.message
    user_name = get_data.user_name

    dict_with_clients = sender_info['self'].dict_with_clients

    if user_name in dict_with_clients.keys():
        write_file = dict_with_clients[user_name]['write_file']
        write_file.write(f"FROM {sender_info['name']}: {message}'\n")
        write_file.flush()
        return "message successfully sent"

    else:
        return "User does not exist"


@register_command
def users(sender_info, *args):
    get_data = UsersData(*args)
    string_with_users = str(' '.join(sender_info['self'].dict_with_clients.keys()))
    return string_with_users
