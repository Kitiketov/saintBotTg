import asyncio
import sqlite3
from typing import Dict, List

import pytest

from src.db import db
from src.utilities import utils


class DummyUser:
    def __init__(self, user_id: int, first_name: str = "Test", last_name: str = "User", username: str = "tester"):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


@pytest.fixture
def setup_db(monkeypatch):
    """Provide an in-memory DB per test and ensure tables are created."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    monkeypatch.setattr(db, "db", conn)
    monkeypatch.setattr(db, "cur", cur)

    def run(coro):
        return asyncio.run(coro)

    run(db.start_db())
    yield run
    conn.close()


@pytest.fixture
def stub_random(monkeypatch):
    """Deterministic room ids for repeatable assertions."""
    counter = {"val": 1000}

    def _fake_randint(start: int, end: int) -> int:
        counter["val"] += 1
        return counter["val"]

    monkeypatch.setattr(db.random, "randint", _fake_randint)
    yield


def _room_name(name: str, room_id: str) -> str:
    return f"{name}{room_id}"


def test_create_room_creates_records(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    run(db.add_user(admin))

    room_id = run(db.create_room("alpha", admin.id))

    row = db.cur.execute("SELECT room_iden, admin FROM rooms").fetchone()
    assert row == (_room_name("alpha", room_id), admin.id)

    admin_room = db.cur.execute(
        "SELECT is_admin, is_member FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
        (admin.id, _room_name("alpha", room_id)),
    ).fetchone()
    assert admin_room == (1, 0)


def test_get_my_rooms_returns_admin_and_member_lists(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    member = DummyUser(2)
    run(db.add_user(admin))
    run(db.add_user(member))

    room_a_id = run(db.create_room("alpha", admin.id))
    room_b_id = run(db.create_room("beta", admin.id))

    join_status = run(db.connect2room(f"alpha:{room_a_id}", member.id))
    assert join_status is True

    admin_rooms = run(db.get_my_rooms(admin.id, asAdmin=True))
    member_rooms = run(db.get_my_rooms(member.id, asAdmin=False))

    assert set(admin_rooms) == {_room_name("alpha", room_a_id), _room_name("beta", room_b_id)}
    assert member_rooms == [_room_name("alpha", room_a_id)]


def test_check_room_and_member_roles(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    member = DummyUser(2)
    run(db.add_user(admin))
    run(db.add_user(member))

    room_id = run(db.create_room("alpha", admin.id))
    room_iden = _room_name("alpha", room_id)

    # Admin is not a member until explicitly joining.
    assert run(db.check_room_and_member(admin.id, room_iden)) == "IS ADMIN"

    run(db.connect2room(f"alpha:{room_id}", member.id))
    assert run(db.check_room_and_member(member.id, room_iden)) is True


def test_get_members_list_includes_admin_flag(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    member = DummyUser(2)
    run(db.add_user(admin))
    run(db.add_user(member))

    room_id = run(db.create_room("alpha", admin.id))
    room_iden = _room_name("alpha", room_id)

    # Admin and member both join the room.
    run(db.connect2room(f"alpha:{room_id}", admin.id))
    run(db.connect2room(f"alpha:{room_id}", member.id))

    member_list, admin_info, is_admin_member = run(db.get_members_list(room_iden))

    assert {m[0] for m in member_list} == {member.id}
    assert admin_info[0] == admin.id
    assert is_admin_member is True


def test_connect_to_unknown_room_returns_error(setup_db):
    run = setup_db
    status = run(db.connect2room("missing:0001", user_id=10))
    assert status == "room_error"


def test_delete_room_removes_all_traces(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    member = DummyUser(2)
    run(db.add_user(admin))
    run(db.add_user(member))

    room_id = run(db.create_room("alpha", admin.id))
    room_iden = _room_name("alpha", room_id)
    run(db.connect2room(f"alpha:{room_id}", member.id))

    run(db.delete_room(room_iden, admin.id))

    assert db.cur.execute("SELECT * FROM rooms WHERE room_iden = ?", (room_iden,)).fetchone() is None
    assert db.cur.execute("SELECT * FROM user_rooms WHERE room_iden = ?", (room_iden,)).fetchone() is None

    tables = db.cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
        (f"{room_iden}_%",),
    ).fetchall()
    assert tables == []


def test_leave_room_removes_member_record(setup_db, stub_random):
    run = setup_db
    admin = DummyUser(1)
    member = DummyUser(2)
    run(db.add_user(admin))
    run(db.add_user(member))

    room_id = run(db.create_room("alpha", admin.id))
    room_iden = _room_name("alpha", room_id)
    run(db.connect2room(f"alpha:{room_id}", member.id))

    run(db.leave_room(room_iden, member.id))

    assert db.cur.execute(f"SELECT * FROM {room_iden}_mem WHERE user_id = ?", (member.id,)).fetchone() is None
    assert db.cur.execute(
        "SELECT * FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
        (member.id, room_iden),
    ).fetchone() is None
    # Admin entry must remain untouched.
    assert db.cur.execute(
        "SELECT * FROM user_rooms WHERE tg_id = ? AND room_iden = ?",
        (admin.id, room_iden),
    ).fetchone() is not None


def test_randomize_members_assigns_unique_pairs():
    random_members: List[int] = [1, 2, 3, 4, 5]
    pairs: Dict[int, int] = utils.randomize_members(random_members)

    assert set(pairs.keys()) == set(random_members)
    assert len(set(pairs.values())) == len(random_members)
    assert all(giver != receiver for giver, receiver in pairs.items())
