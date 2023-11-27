import asyncio

async def create_member_list(raw_list,admin,room_iden,isAdminMember):
    member_list=f"Участники группы {room_iden[:-4]}:{room_iden[-4:]}\n\n"
    member_list+=f"Админ {admin[1]} {admin[2]} @{admin[3]}\n"
    i=1
    if isAdminMember:
        member_list+=f"1. {admin[1]} {admin[2]} @{admin[3]}\n"
        i+=1
    for member in raw_list:
        member_list +=f"{i}. {member[1]} {member[2]} @{member[3]}\n"
        i+=1
    return member_list