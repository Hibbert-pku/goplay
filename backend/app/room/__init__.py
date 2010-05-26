from chat import Chat

from protocol.client import ClientRoomCommand

from helper.threads import to_thread


class Room:
    __rooms__ = {}  # {'name' : room_instance}
    
    @classmethod
    def add(cls, room):
        if room.name not in cls.__rooms__:
            cls.__rooms__[room.name] = room
        else:
            raise ValueError("Room 'name' already in use")

    @classmethod
    def remove(cls, room):
        try:
            del cls.__rooms__[room.name]
        except KeyError:
            pass

    def __init__(self, name):
        self.name = name
        Room.add(self)

        self.chat = Chat()
        self.users = {}     # {'name' : connected_user_instance}

    def destroy(self):
        Room.remove(self)

    @to_thread()
    def addUser(self, user):
        username = user.db_tuple.name
        
        self.users[username] = user
        
        for user_in_room in self.users:
            reactor.callFromThread(user_in_room.conn.send,
                                   ClientRoomCommand.adduser(self.id, username))

    @to_thread()
    def removeUser(self, user):
        username = user.db_tuple.name
        
        try:
            del self.users[username]
        except KeyError:
            pass
        
        for user_in_room in self.users:
            reactor.callFromThread(user_in_room.conn.send,
                                   ClientRoomCommand.removeuser(self.id, username))

def get_all_rooms(conn, trans=None):
    conn.send({'rooms':Room.__rooms__.keys()}, trans)

def getUsersFromRoom(conn, name, trans=None):
    print trans
    room = Room.__rooms__.get(name)
    if room:
        response = room.users.keys()
    else:
        response = []
    conn.send({'users':response}, trans)
