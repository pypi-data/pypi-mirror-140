from validators import String


class SendMessageData:
    message = String(minsize=1, maxsize=100)

    def __init__(self, *args):
        assert len(args) > 1, 'send_message command takes name of user and message'
        self.user_name = args[0]
        self.message = ' '.join(args[1::])


class UsersData:
    def __init__(self, *args):
        assert len(args) == 0, 'users command takes exactly 0 arguments'
