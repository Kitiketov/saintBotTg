import asyncio
import random
import sqlite3 as sq
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database.db"
db = sq.connect(DB_PATH)
cur = db.cursor()

ROOM_DEFAULT_PRICE = "не установлен"
ROOM_DEFAULT_EVENT_TIME = "не установлено"
ROOM_DEFAULT_EXCHANGE_TYPE = "централизованый"


async def start_db():
    cur.execute(
        "CREATE TABLE IF NOT EXISTS rooms("
        "room_iden TEXT PRIMARY KEY,"
        "status BOOLEAN DEFAULT FALSE,"
        "admin INTEGER,"
        "gift_price_range TEXT DEFAULT 'не установлен',"
        "event_time TEXT DEFAULT 'не установлено',"
        "exchange_type TEXT DEFAULT 'централизованый'"
        ")"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(tg_id INTEGER PRIMARY KEY,first_name TEXT,last_name TEXT,username TEXT)"
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_rooms(
            tg_id INTEGER,
            room_iden TEXT,
            is_member BOOLEAN DEFAULT FALSE,
            is_admin BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (tg_id, room_iden)
        )
        """
    )
    await migrate_rooms_table()
    db.commit()


async def create_room(room_name, user_id):
    disvalid = [
        "_saint",
        "_mem",
        "\\",
        ".",
        "/",
        ",",
        ":",
        ";",
        "'",
        '"',
        " ",
        "*",
        "+",
        "-",
        "#",
        "@",
        "$",
        "%",
        "^",
        "!",
        "~",
        "`",
        "&",
        "|",
        "<",
        ">",
        "[",
        "]",
        "(",
        ")",
        "{",
        "}",
    ]
    if (
        all([a not in room_name for a in disvalid])
        and room_name[0] not in "0123456789"
        and len(room_name) <= 30
    ):
        while True:
            room_id = f"{random.randint(1, 9999):04}"
            room_iden = f"{room_name}{room_id}"
            _room_iden = cur.execute(
                "SELECT 1 FROM rooms WHERE room_iden = ?", (room_iden,)
            ).fetchone()
            if not _room_iden:
                break
        member_table_name = f"{room_iden}_mem"
        saint_table_name = f"{room_iden}_saint"
        cur.execute(
            "INSERT INTO rooms (room_iden,admin) VALUES (?, ?)", (room_iden, user_id)
        )
        cur.execute(
            f"CREATE TABLE {member_table_name} (user_id INTEGER PRIMARY KEY, wishes TEXT, photo_id TEXT)"
        )
        cur.execute(
            f"CREATE TABLE {saint_table_name} (saint_user_id INTEGER PRIMARY KEY,reciver_user_id INTEGER)"
        )

        cur.execute(
            "INSERT OR IGNORE INTO user_rooms (tg_id, room_iden) VALUES (?, ?)",
            (user_id, room_iden),
        )
        cur.execute(
            "UPDATE user_rooms SET is_admin = TRUE WHERE tg_id = ? AND room_iden = ?",
            (user_id, room_iden),
        )

        db.commit()
        return room_id


async def add_user(user):
    _user = cur.execute("SELECT * FROM users WHERE tg_id = ?", (user.id,)).fetchone()
    if not _user:
        cur.execute(
            "INSERT INTO users (tg_id, first_name, last_name,username) VALUES (?, ?, ?, ?)",
            (user.id, user.first_name, user.last_name, user.username),
        )
        db.commit()


async def update_user(user):
    await add_user(user)
    cur.execute(
        "UPDATE users SET first_name = ?, last_name = ?, username = ? WHERE tg_id = ?",
        (user.first_name, user.last_name, user.username, user.id),
    )
    db.commit()


async def connect2room(raw_data, user_id):
    raw_data += ":"
    room_name, room_id, *_ = raw_data.split(":")
    room_iden = f"{room_name}{room_id}"
    table_name = f"{room_iden}_mem"
    _room = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    if not _room:
        return "room_error"
    if _room[1] == True:
        return "joined late"
    _user = cur.execute(
        f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,)
    ).fetchone()
    if _user:
        return "user_error"
    cur.execute(
        f"INSERT INTO {table_name} (user_id,wishes) VALUES (?, '-')", (user_id,)
    )

    _room = cur.execute(
        "SELECT * FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
        (user_id, room_iden),
    ).fetchone()
    if not _room:
        cur.execute(
            "INSERT INTO user_rooms (tg_id, room_iden, is_member, is_admin) VALUES (?, ?, TRUE, FALSE)",
            (user_id, room_iden),
        )
    else:
        cur.execute(
            "UPDATE user_rooms SET is_member = TRUE WHERE tg_id = ? AND room_iden = ?",
            (user_id, room_iden),
        )

    db.commit()
    return True


async def get_members_list(room_iden):
    admin_raw = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    admin_id = admin_raw[2]
    isAdminMember = False

    member_id_list = cur.execute(f"SELECT * FROM {room_iden}_mem ").fetchall()
    admin = member = cur.execute(
        "SELECT * FROM users WHERE tg_id = ?", (admin_id,)
    ).fetchone()

    member_list = []
    for member_id in member_id_list:
        if member_id[0] != admin_id:
            member = cur.execute(
                "SELECT * FROM users WHERE tg_id = ?", (member_id[0],)
            ).fetchone()
            member_list.append(member)
        else:
            isAdminMember = True
    return member_list, admin, isAdminMember


async def leave_room(room_iden, user_id):
    cur.execute(f"DELETE FROM {room_iden}_mem WHERE user_id = ?", (user_id,))
    cur.execute(
        "UPDATE user_rooms SET is_member = FALSE WHERE tg_id = ? AND room_iden = ?",
        (user_id, room_iden),
    )
    db.commit()
    cur.execute(
        "DELETE FROM user_rooms WHERE tg_id = ? AND room_iden = ? AND is_member = FALSE AND is_admin = FALSE",
        (user_id, room_iden),
    )
    db.commit()


async def get_my_rooms(user_id, asAdmin):
    if asAdmin:
        rooms_raw = cur.execute(
            "SELECT room_iden FROM user_rooms WHERE tg_id = ? AND is_admin = TRUE",
            (user_id,),
        ).fetchall()
    else:
        rooms_raw = cur.execute(
            "SELECT room_iden FROM user_rooms WHERE tg_id = ? AND is_member = TRUE",
            (user_id,),
        ).fetchall()
    return [room[0] for room in rooms_raw]


async def delete_room(room_iden, admin_id):
    member_table_name = f"{room_iden}_mem"
    saint_table_name = f"{room_iden}_saint"

    users_id = cur.execute(f"SELECT user_id FROM {member_table_name}").fetchall()
    cur.execute(
        "DELETE FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
        (admin_id, room_iden),
    )
    for user_id in users_id:
        cur.execute(
            "DELETE FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
            (user_id[0], room_iden),
        )

    cur.execute(f"DROP TABLE IF EXISTS {member_table_name}")
    cur.execute(f"DROP TABLE IF EXISTS {saint_table_name}")
    cur.execute("DELETE FROM rooms WHERE room_iden = ?", (room_iden,))
    db.commit()


async def write_pairs(pairs, room_iden):
    table_name = f"{room_iden}_saint"
    for pair in pairs:
        cur.execute(
            f"INSERT INTO {table_name} (saint_user_id,reciver_user_id) VALUES (?, ?)",
            (pair, pairs[pair]),
        )
    db.commit()


async def start_event(room_iden):
    cur.execute("UPDATE rooms SET status = TRUE WHERE room_iden = ?", (room_iden,))
    db.commit()


async def who_gives(room_iden, user_id):
    table_name = f"{room_iden}_saint"
    pair = cur.execute(
        f"SELECT * FROM {table_name} WHERE saint_user_id = ?", (user_id,)
    ).fetchone()
    if not pair:
        return "JOINED LATE"
    return pair[1]


async def isStarted(room_iden):
    room_raw = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    return room_raw[1]


async def get_user(user_id):
    return cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,)).fetchone()


async def check_room_and_member(user_id, room_iden):
    _room = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    if not _room:
        return "ROOM NOT EXISTS"
    table_name = f"{room_iden}_mem"
    _user = cur.execute(
        f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,)
    ).fetchone()
    if not _user and _room[2] == user_id:
        return "IS ADMIN"
    if not _user:
        return "MEMBER NOT EXISTS"
    return True


async def get_room_admin(room_iden):
    admin_raw = cur.execute(
        "SELECT admin FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    if not admin_raw:
        return None
    return admin_raw[0]


async def count_user_room(user_id):
    count = cur.execute(
        "SELECT COUNT(*) FROM user_rooms WHERE tg_id = ?",
        (user_id,),
    ).fetchone()
    return count[0] if count else 0


async def get_wishes_and_photo(room_iden, user_id):
    _room = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)
    ).fetchone()
    if not _room:
        return "ROOM NOT EXISTS", None, None
    table_name = f"{room_iden}_mem"
    _user = cur.execute(
        f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,)
    ).fetchone()
    if not _user:
        return "MEMBER NOT EXISTS", None, None
    _, wishes, photo_id = _user
    return True, wishes, photo_id


async def edit_wishes(wishes, user_id, room_iden, photo_id=""):
    _room = cur.execute(
        "SELECT * FROM rooms WHERE room_iden = ?",
        (room_iden,),
    ).fetchone()
    if not _room:
        return "ROOM NOT EXISTS"

    table_name = f"{room_iden}_mem"
    _user = cur.execute(
        f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,)
    ).fetchone()
    if not _user:
        return "MEMBER NOT EXISTS"

    cur.execute(
        f"UPDATE {table_name} SET wishes = ?, photo_id = ? WHERE user_id = ?",
        (wishes, photo_id, user_id),
    )

    db.commit()
    return True


async def migrate_rooms_table():
    columns = [
        column[1] for column in cur.execute("PRAGMA table_info(rooms)").fetchall()
    ]
    migrations = [
        (
            "gift_price_range",
            f"ALTER TABLE rooms ADD COLUMN gift_price_range TEXT DEFAULT '{ROOM_DEFAULT_PRICE}'",
        ),
        (
            "event_time",
            f"ALTER TABLE rooms ADD COLUMN event_time TEXT DEFAULT '{ROOM_DEFAULT_EVENT_TIME}'",
        ),
        (
            "exchange_type",
            f"ALTER TABLE rooms ADD COLUMN exchange_type TEXT DEFAULT '{ROOM_DEFAULT_EXCHANGE_TYPE}'",
        ),
    ]

    for column, query in migrations:
        if column not in columns:
            cur.execute(query)

    db.commit()


async def get_room_settings(room_iden):
    _room = cur.execute(
        "SELECT gift_price_range, event_time, exchange_type FROM rooms WHERE room_iden = ?",
        (room_iden,),
    ).fetchone()
    if not _room:
        return "ROOM NOT EXISTS", None, None, None
    price, event_time, exchange_type = _room
    return True, price, event_time, exchange_type


async def update_room_settings(room_iden, price=None, event_time=None, exchange_type=None):
    _room = cur.execute(
        "SELECT 1 FROM rooms WHERE room_iden = ?",
        (room_iden,),
    ).fetchone()
    if not _room:
        return "ROOM NOT EXISTS"

    if price is not None:
        cur.execute(
            "UPDATE rooms SET gift_price_range = ? WHERE room_iden = ?",
            (price, room_iden),
        )
    if event_time is not None:
        cur.execute(
            "UPDATE rooms SET event_time = ? WHERE room_iden = ?",
            (event_time, room_iden),
        )
    if exchange_type is not None:
        cur.execute(
            "UPDATE rooms SET exchange_type = ? WHERE room_iden = ?",
            (exchange_type, room_iden),
        )

    db.commit()
    return True


if __name__ == "__main__":
    asyncio.run(start_db())
