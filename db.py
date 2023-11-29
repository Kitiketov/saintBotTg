import sqlite3 as sq
import asyncio

import random


db = sq.connect("database.db")
cur = db.cursor()

async def start_db():
    cur.execute("CREATE TABLE IF NOT EXISTS rooms(room_iden TEXT PRIMARY KEY,status BOOLEAN DEFAULT FALSE,admin INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS users(tg_id INTEGER PRIMARY KEY,first_name TEXT,last_name TEXT,username TEXT)")
    db.commit()

async def create_room(room_name,user_id):
    disvalid= ["_saint","_mem","\\",".","/",",",":","'","\""," ","*","+","-","#","@","$","%","^","!","~","`","&","|","<",">","[","]","(",")","{","}"]
    if all([a not in room_name for a in disvalid]) and room_name[0] not in "0123456789" and len(room_name)<=64:
        while True:
            room_id = f"{random.randint(1,9999):04}"
            _room_iden = cur.execute(f"SELECT * FROM rooms WHERE room_iden =='{room_name}{room_id}'").fetchone()
            if not _room_iden:
                break
        cur.execute(f"INSERT INTO rooms (room_iden,admin) VALUES ('{room_name}{room_id}', {user_id})")
        cur.execute(f"CREATE TABLE {room_name}{room_id}_mem (user_id INTEGER PRIMARY KEY)")
        cur.execute(f"CREATE TABLE {room_name}{room_id}_saint (saint_user_id INTEGER PRIMARY KEY,reciver_user_id INTEGER)")

        _room = cur.execute(f"SELECT * FROM rooms_{user_id} WHERE room_iden == '{room_name}{room_id}'").fetchone()
        if not _room:
            cur.execute(f"INSERT INTO rooms_{user_id} (room_iden) VALUES ('{room_name}{room_id}')")
        cur.execute(f"UPDATE rooms_{user_id} SET is_admin == TRUE WHERE room_iden == '{room_name}{room_id}'")

        db.commit()
        return room_id

async def add_user(user):
    _user = cur.execute(f"SELECT * FROM users WHERE tg_id == {user.id}").fetchone()
    if not  _user: 
        cur.execute(f"INSERT  INTO users (tg_id, first_name, last_name,username) VALUES ({user.id}, '{user.first_name}', '{user.last_name}', '{user.username}')")
        cur.execute(f"CREATE TABLE rooms_{user.id} (room_iden TEXT PRIMARY KEY, is_member BOOLEAN DEFAULT FALSE, is_admin BOOLEAN DEFAULT FALSE)")
    db.commit()

async def connect2room(raw_data,user_id):
    raw_data+=":"
    room_name, room_id,*_ = raw_data.split(":")
    _room = cur.execute(f"SELECT * FROM rooms WHERE room_iden == '{room_name}{room_id}'").fetchone()
    if _room:
        _user = cur.execute(f"SELECT * FROM {room_name}{room_id}_mem WHERE user_id == {user_id}").fetchone()
        if not _user:
            cur.execute(f"INSERT INTO {room_name}{room_id}_mem (user_id) VALUES ({user_id})")

            _room = cur.execute(f"SELECT * FROM rooms_{user_id} WHERE room_iden == '{room_name}{room_id}'").fetchone()
            if not _room:
                cur.execute(f"INSERT INTO rooms_{user_id} (room_iden) VALUES ('{room_name}{room_id}')")
            cur.execute(f"UPDATE rooms_{user_id} SET is_member == TRUE WHERE room_iden == '{room_name}{room_id}'")

            db.commit()
            return True
        return "user_error"
    return "room_error"


async def get_members_list(room_iden):
    
    admin_raw = cur.execute(f"SELECT * FROM rooms WHERE room_iden == '{room_iden}'").fetchone()
    *_,admin_id = admin_raw
    isAdminMember = False
    
    member_id_list = cur.execute(f"SELECT * FROM {room_iden}_mem ").fetchall()
    admin = member = cur.execute(f"SELECT * FROM users WHERE tg_id == {admin_id}").fetchone()

    member_list = []
    for member_id in member_id_list:
        if member_id[0]!=admin_id:
            member = cur.execute(f"SELECT * FROM users WHERE tg_id == {member_id[0]}").fetchone()
            member_list.append(member)
        else:
            isAdminMember = True
    return member_list, admin, isAdminMember

async def leave_room(room_iden,user_id):
    cur.execute(f"DELETE FROM {room_iden}_mem WHERE user_id == {user_id}")
    cur.execute(f"UPDATE rooms_{user_id} SET is_member == FALSE WHERE room_iden == '{room_iden}'")
    db.commit()
    cur.execute(f"DELETE FROM rooms_{user_id} WHERE room_iden == '{room_iden}' AND is_member == FALSE AND is_admin == FALSE")
    db.commit()

async def get_my_rooms(user_id,asAdmin):
    if asAdmin:
        rooms_raw = cur.execute(f"SELECT * FROM rooms_{user_id} WHERE is_admin == TRUE").fetchall()
    else:
        rooms_raw = cur.execute(f"SELECT * FROM rooms_{user_id} WHERE is_member == TRUE").fetchall()
    rooms = []
    for room in rooms_raw:
        rooms.append(room[0])
    return rooms
    
async def delete_room(room_iden,admin_id):
    users_id = cur.execute(f"SELECT * FROM {room_iden}_mem").fetchall()
    cur.execute(f"DELETE FROM rooms_{admin_id} WHERE room_iden == '{room_iden}'")
    for user_id in users_id:
        cur.execute(f"DELETE FROM rooms_{user_id[0]} WHERE room_iden == '{room_iden}'")
    cur.execute(f"DROP TABLE IF EXISTS {room_iden}_mem")
    cur.execute(f"DROP TABLE IF EXISTS {room_iden}_saint")
    cur.execute(f"DELETE FROM rooms WHERE room_iden == '{room_iden}'")
    db.commit()

async def write_pairs(pairs,room_iden):
    for pair in pairs:
        cur.execute(f"INSERT INTO {room_iden}_saint (saint_user_id,reciver_user_id) VALUES ({pair}, {pairs[pair]})")
    db.commit()

async def start_event(room_iden):
    cur.execute(f"UPDATE rooms SET status == TRUE WHERE room_iden == '{room_iden}'")
    db.commit()

async def who_gives(room_iden,user_id):
    pair = cur.execute(f"SELECT * FROM {room_iden}_saint WHERE saint_user_id == {user_id}").fetchone()
    return pair[1]

async def isStarted(room_iden):
    _,status,_ = cur.execute(f"SELECT * FROM rooms WHERE room_iden == '{room_iden}'").fetchone()
    return status

async def get_user(user_id):
    return cur.execute(f"SELECT * FROM users WHERE tg_id == {user_id}").fetchone()

async def check_room_and_member(user_id,room_iden):
    _room = cur.execute(f"SELECT * FROM rooms WHERE room_iden =='{room_iden}'").fetchone()
    if not _room:
        return "ROOM NOT EXISTS"
    _user = cur.execute(f"SELECT * FROM {room_iden}_mem WHERE user_id == {user_id}").fetchone()
    if not _user and _room[2] == user_id:
            return "IS ADMIN"
    elif not _user:
        return "MEMBER NOT EXISTS"
    return True

async def count_user_room(user_id):
    return len(cur.execute(f"SELECT * FROM rooms_{user_id}").fetchall())
if __name__ == "__main__":
    asyncio.run(start_db())