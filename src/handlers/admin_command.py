import shutil
import tempfile
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from src.config import settings, logger
from src.db import db

router = Router(name=__name__)


def _is_admin(msg: Message):
    return msg.from_user and msg.from_user.id == settings.admin_id


@router.message(Command("backup"))
async def backup(msg: Message):
    if not _is_admin(msg):
        return

    db_file = Path(db.DB_PATH)
    log_file = Path("py_log.log").resolve()

    async def _send_file(file_path: Path, caption: str):
        if not file_path.exists():
            await msg.answer(f"{caption}: файл не найден.")
            return
        tmp_dir = Path(tempfile.mkdtemp())
        tmp_file = tmp_dir / file_path.name
        try:
            shutil.copy(file_path, tmp_file)
            await msg.answer_document(FSInputFile(tmp_file), caption=caption)
        except Exception as e:
            logger.error(f"Backup error for {file_path}: {e}")
            await msg.answer(f"Не удалось отправить {caption}.")
        finally:
            try:
                tmp_file.unlink()
                tmp_dir.rmdir()
            except Exception:
                pass

    await _send_file(db_file, "database.db")
    await _send_file(log_file, "py_log.log")


@router.message(Command("status"))
async def status(msg: Message):
    if not _is_admin(msg):
        return

    users_total, participants, rooms_total, started_rooms = await db.get_stats()
    await msg.answer(
        "Статус:\n"
        f"Пользователей в базе: {users_total}\n"
        f"Участников с комнатами: {participants}\n"
        f"Комнат всего: {rooms_total}\n"
        f"Комнат с запущенным ивентом: {started_rooms}"
    )
