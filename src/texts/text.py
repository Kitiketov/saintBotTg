import asyncio


async def create_user_info(user):
    print(user)
    text = f"{user[1]} "
    if user[2] is not None:
        text += f"{user[2]} "
    if user[3] is not None:
        text += f"@{user[3]}\n"
    else:
        text += f"<a href='tg://user?id={user[0]}'>{user[1]}</a>\n"
    return text


async def create_member_list(raw_list, admin, room_iden):
    member_list = f"Участники группы {room_iden[:-4]}:{room_iden[-4:]}\n\n"
    member_list += "Админ " + await create_user_info(admin)
    i = 1
    for member in raw_list:
        member_list += f"{i}. " + await create_user_info(member)
        i += 1
    return member_list


async def create_wishes_info(wishes):
    if wishes == "-":
        return "У вас пока нет пожеланий, но вы можете их написать"
    return f"Ваше желание:\n{wishes}\nВы можете отредактировать его"


async def take_wishes_info(wishes):
    if wishes == "-":
        return "У получателя пока нет пожеланий"
    return f"Желание получателя:\n{wishes}"
