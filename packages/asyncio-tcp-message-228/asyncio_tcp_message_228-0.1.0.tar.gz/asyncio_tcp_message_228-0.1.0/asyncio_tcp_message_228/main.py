import os
import socket
import threading

import dictionaries
import validators
# No inspection is added because these imports register command functions
# noinspection PyUnresolvedReferences


class MySocketServer:
    def __init__(self, port, host='0.0.0.0', max_connections=3, turn_on_messages=False):
        self.port = port
        self.host = host
        self.semaphore = threading.Semaphore(max_connections)

        self.dict_with_clients = {}  # name: {read_file, write_file}

        if turn_on_messages:
            import commands

    def add_client(self, conn, address):
        name = validators.String(minsize=1, maxsize=20)

        read_file = conn.makefile(mode='r', encoding='utf-8')
        write_file = conn.makefile(mode='w', encoding='utf-8')
        write_file.write('Hi client, write you name\n')
        write_file.flush()

        cmd = read_file.readline().strip()
        while cmd:
            error = ''
            name = cmd.split()[0]
            print(name)

            if not name:
                raise StopIteration('User enter stop command')

            if name in self.dict_with_clients.keys():
                error = "this name already in use, try again"

            result = error if error else f"Now you name is {name}"

            write_file.write(result + '\n')
            write_file.flush()

            if error:
                cmd = read_file.readline().strip()
                continue

            break

        self.dict_with_clients[name] = {'read_file': read_file,
                                        'write_file': write_file}

        return name, read_file, write_file

    @staticmethod
    def handle_command(sender_info, cmd, *args):
        try:
            print(dictionaries.commands_dict)
            print(cmd)
            command_func = dictionaries.commands_dict.get(cmd)
            if command_func is None:
                raise ValueError('Unknown command')
            result = command_func(sender_info, *args)
        except (TypeError, ValueError, AssertionError) as e:
            result = str(e)
        except StopIteration:
            result = ''
        return result

    def handle_client(self, conn, address):
        with self.semaphore:
            print('Starting new thread for client:', address)
            name, read_file, write_file = self.add_client(conn, address)
            sender_info = {'self': self, 'name': name}
            cmd = read_file.readline().strip()
            while cmd:
                result = self.handle_command(sender_info, *cmd.split())
                print(result)
                if result == '':
                    break
                write_file.write(result + '\n')
                write_file.flush()
                cmd = read_file.readline().strip()
            conn.close()

    def start(self):
        print(f'Started process with PID={os.getpid()}')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # solution for "[Error 89] Address already in use". Use before bind()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            try:
                while True:
                    with self.semaphore:
                        conn, addr = s.accept()
                        t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                        t.start()
            except (KeyboardInterrupt, SystemExit):
                print('\nReceived keyboard interrupt, quitting threads.\n')


server = MySocketServer(8080, turn_on_messages=True)
server.start()
