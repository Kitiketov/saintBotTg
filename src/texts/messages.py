def menu() -> str:
    return "Меню"


def welcome_menu() -> str:
    return "🎅Мы рады что вы выбрали нас.\n Что вы хотите:"


def prompt_join_room() -> str:
    return "Напишите название комнаты c её id (имякомнаты:id):"


def room_not_exists(room_name: str | None = None) -> str:
    if room_name:
        return f"Комнаты {room_name} не существует"
    return "Такой комнаты не существует"


def user_already_in_room() -> str:
    return "Вы уже находитесь в этой комнате"


def game_already_started() -> str:
    return "Игра уже начилась"


def join_success(first_name: str, room_name: str) -> str:
    return f"{first_name} вы успешно присоединились к комнате: {room_name}"


def choose_option() -> str:
    return "Выберите нужный вам вариант"


def not_a_member(room_name: str) -> str:
    return f"Вы не участник комнаты  {room_name}"


def room_admin_title(room_name: str) -> str:
    return f"Управление комнатой {room_name} "


def room_title(room_name: str) -> str:
    return f"Комната {room_name}"


def event_not_started(room_name: str) -> str:
    return f"Событие в комнате {room_name} ещё не началось "


def admin_not_member_start(room_name: str) -> str:
    return (
        f"Вы пока не участник комнаты {room_name}.\n"
        "Добавить себя и участвовать в обмене или начать без вас?"
    )


def event_started_before_join(room_name: str) -> str:
    return (
        f"Событие в комнате {room_name} началось раньше вашего присоединения\n"
        "Вы не были распределены"
    )


def gift_target(user_info: str) -> str:
    return f"Вы дарите <tg-spoiler>{user_info}</tg-spoiler>"


def left_room() -> str:
    return "Вы покинули комнату"


def too_many_rooms() -> str:
    return "Превышено количество созданных вами комнат\n"


def prompt_create_room_name() -> str:
    return "Введите название комнаты:"


def invalid_room_name() -> str:
    return (
        "Имя не должно содержать _mem , _saint, символы кроме  _ , цифры в начале , пробелы и"
        " не длинее 30 символов\nПридумайте другое название:"
    )


def room_created(room_name: str, room_id: str) -> str:
    return (
        f"Комната:  {room_name}:{room_id} создана \n"
        "Чтобы другие могли в неё войти скажите им её название c id\n"
        "<b>Админ автоматически не является участником</b>"
    )


def prompt_wish() -> str:
    return "Напишите ваше пожелание"


def prompt_wish_with_current(current: str) -> str:
    return (
        "Ваше текущее желание:\n"
        f"<code>{current}</code>\n"
        "Отправьте новое (можно нажать на текст выше, чтобы скопировать)."
    )


def wish_not_member() -> str:
    return "Вы не участник комнаты"


def wish_updated(text: str) -> str:
    return f"Вы изменили пожелание:\n{text}"


def room_leave_confirmation(room_name: str) -> str:
    return f"Вы уверены что хотите удалить комнату {room_name} ?"


def room_deleted(room_name: str) -> str:
    return f"Комната {room_name} удаленна"


def member_already_removed(room_name: str) -> str:
    return f"Участник уже не в {room_name}"


def member_removed(room_name: str) -> str:
    return f"Участник удален из комнаты  {room_name} "


def event_already_started(room_name: str) -> str:
    return f"Событие уже начато  {room_name} "


def media_group_not_supported() -> str:
    return "Можно отправить только одно фото или текст без альбомов."


def event_not_enough_members(room_name: str) -> str:
    return f"Участников в  {room_name} недостаточно для начала. Должно быть более 1"


def event_started(room_name: str) -> str:
    return f"Событие началось в  {room_name} "


def event_started_notify(room_name: str) -> str:
    return f"Событие в комнате {room_name} началось\nПроверте кому вы дарите"

def remind_notify(room_name: str) -> str:
    return (
        f"🔔 Напоминание: событие в комнате {room_name} уже идёт.\n"
        "Зайдите в комнату и нажмите «🎁Кому я дарю», чтобы проверить получателя, "
        "и подготовьте подарок."
    )


def invitation_text(room_name: str) -> str:
    return (
        f"✉️Приглашение принять участвие в Тайном санта в комнате <code>{room_name}</code>\n"
        "<b>Если приглашение не сработало попробуйте присоединиться в ручном режиме</b>"
    )


def prompt_custom_invitation(room_name: str) -> str:
    return (
        f"Отправьте текст приглашения для комнаты <code>{room_name}</code>\n"
        "Можно добавить одно фото без альбома"
    )


def invitation_too_long() -> str:
    return "Слишком длинное приглашение. Укоротите текст и отправьте новое"


def invitation_empty() -> str:
    return "Приглашение не распознано. Отправьте текст или фото с подписью"


def room_not_exists_retry() -> str:
    return "Такой комнаты не существует\nПопробуйте ещё раз:"


def id_info(user_id: int, chat_id: int) -> str:
    return f"ID: user_id - {user_id}\n      chat_id - {chat_id}"

def about_santa():
    return (
        "🎅 Тайный Санта — игра, в которой каждый участник случайно становится дарителем для кого-то другого. "
        "Бот помогает провести обмен анонимно и без лишней организации."
        "\n\nКак проходит игра:\n"
        "1. Админ создаёт комнату и делится кодом или приглашением.\n"
        "2. Участники присоединяются, заполняют пожелания и смотрят настройки: бюджет, дата, тип обмена.\n"
        "3. Когда все готовы, админ нажимает «Старт» — бот случайно распределяет пары.\n"
        "4. Каждый получает сообщение, кому дарить, а его имя остаётся секретом для остальных."
        "\n\nПодготовьте подарок в указанном бюджете и времени, и оставайтесь Тайным Сантой 🎁"
    )
