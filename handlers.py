from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import base64
import keyboards
import text
from states import Gen, CallbackFactory, RemoveCallbackFactory
import db
import utils


router = Router()
@router.message(Command("menu"))
@router.message(Command("start"))
async def start_handler(msg: Message):
    await db.add_user(msg.from_user)
    if "join_to_room-" in msg.text and "end_invitation" in msg.text:
        raw_iden = msg.text.split("join_to_room-")[1].replace("end_invitation","")
        room_iden = base64.urlsafe_b64decode(raw_iden+"===").decode()
        name = f"{room_iden[:-4]}:{room_iden[-4:]}"
        room_status = await db.connect2room(name,msg.from_user.id)
        if room_status == "room_error":
            await msg.answer("Такой комнаты не существует",reply_markup=await  keyboards.cancel_keyboard("None",False))
            return
        elif room_status == "user_error":
            await msg.answer("Вы уже находитесь в этой комнате",reply_markup=await keyboards.cancel_keyboard("None",False))
            return
        kb = await keyboards.room_member_keyboard(f"{''.join(name.split(':'))}")
        await msg.answer(f"{msg.from_user.first_name} вы успешно присоединились к комнате: {name}",reply_markup=kb)
        return
    await msg.answer("🎅Мы рады что вы выбрали нас.\n Что вы хотите:",reply_markup=keyboards.choice_kb)

@router.callback_query(CallbackFactory.filter(F.action == "create_room"))
async def  start_create_room(call: CallbackQuery, callback_data: CallbackFactory, state : FSMContext):
    await db.update_user(call.from_user)
    room_count = await db.count_user_room(call.from_user.id)
    if room_count>5:
        await call.message.answer("Превышено количество созданных вами комнат\n",reply_markup= await keyboards.cancel_keyboard("None",False))
        return
    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_create)
    await call.message.answer("Введите название комнаты:",reply_markup= await keyboards.cancel_keyboard("None",False))

@router.callback_query(CallbackFactory.filter(F.action == "join_room"))
async def start_join_room(call: CallbackQuery, callback_data: CallbackFactory, state : FSMContext):
    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_join)
    await call.message.answer("Напишите название комнаты c её id (имякомнаты:id):",reply_markup=await  keyboards.cancel_keyboard("None",False))

@router.message(Gen.room_name_to_join)
async def join_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text
    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return
    room_status = await db.connect2room(name,msg.from_user.id)
    if room_status == "room_error":
        await msg.answer("Такой комнаты не существует\nПопробуйте ещё раз:",reply_markup=await  keyboards.cancel_keyboard("None",False))
        return
    elif room_status == "user_error":
        await msg.answer("Вы уже находитесь в этой комнате\n",reply_markup=await keyboards.cancel_keyboard("None",False))
        await state.clear()
        return
    await state.clear()
    kb = await keyboards.room_member_keyboard(f"{''.join(name.split(':'))}")
    await msg.answer(f"{msg.from_user.first_name} вы успешно присоединились к комнате: {name}",reply_markup=kb)

@router.message(Gen.room_name_to_create)
async def create_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text
    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return
    id = await db.create_room(name,msg.from_user.id)
    if not id:
        await msg.answer("Имя не должно содержать _mem , _saint, символы кроме  _ , цифры в начале , пробелы и не длинее 30 символов\nПридумайте другое название:",reply_markup=await keyboards.cancel_keyboard("None",False))
        return
    await state.clear()
    kb = await keyboards.room_admin_keyboard(f"{name}{id}")
    await msg.answer(f"Комната:  {name}:{id} создана \nЧтобы другие могли в неё войти скажите им её название c id\n<b>Админ автоматически не является участником</b>",reply_markup=kb)

@router.message(F.text =="◀️Вернуться в меню")
@router.callback_query(CallbackFactory.filter(F.action == "back_to_menu"))
async def menu(call: CallbackQuery, callback_data: CallbackFactory):
    await db.update_user(call.from_user)
    await call.message.edit_text("Меню", reply_markup=keyboards.choice_kb)

@router.callback_query(CallbackFactory.filter(F.action == "members_list"))
async def get_member_list(call: CallbackQuery, callback_data: CallbackFactory):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "MEMBER NOT EXISTS" or (callback_data.asAdmin==False and isMemberOrAdmin =="IS ADMIN"):
        await call.message.edit_text(f"Вы не участник комнаты  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    
    member_list, admin,isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        member_list.append(admin)
    ans = await text.create_member_list(member_list, admin,callback_data.room_iden)
    await call.message.answer(ans,reply_markup = await keyboards.cancel_keyboard(callback_data.room_iden,callback_data.asAdmin))

@router.callback_query(CallbackFactory.filter(F.action == "cancel"))
async def cancel(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    if callback_data.room_iden == "None":
        await state.clear()
    await call.message.delete()

@router.callback_query(CallbackFactory.filter(F.action == "leave_room"))
async def cancel(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    await db.leave_room(callback_data.room_iden,call.from_user.id)
    await call.message.edit_text("Вы покинули комнату", reply_markup=keyboards.choice_kb)

@router.callback_query(CallbackFactory.filter(F.action == "list_of_rooms"))
async def get_list_of_rooms(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    await call.message.edit_text("Выберите нужный вам вариант",reply_markup=keyboards.my_rooms_kb)

@router.callback_query(CallbackFactory.filter(F.action == "my_rooms"))
async def get_my_admin_rooms(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    rooms = await db.get_my_rooms(call.from_user.id, callback_data.asAdmin)
    kb = await keyboards.rooms_kb(rooms, callback_data.asAdmin)
    await call.message.edit_text("Выберите нужный вам вариант",reply_markup=kb)

@router.callback_query(CallbackFactory.filter(F.action == "show_room"))
async def show_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    if callback_data.asAdmin:
        await call.message.edit_text(f"Управление комнатой {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ",reply_markup =await keyboards.room_admin_keyboard(callback_data.room_iden))
    else:
        if isMemberOrAdmin == "MEMBER NOT EXISTS" or (callback_data.asAdmin==False and isMemberOrAdmin =="IS ADMIN"):
            await call.message.edit_text(f"Вы не участник комнаты  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
            return
        await call.message.edit_text(f"Комната {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}",reply_markup=await keyboards.room_member_keyboard(callback_data.room_iden))

@router.callback_query(CallbackFactory.filter(F.action == "delete_room"))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    kb = await keyboards.confirm_keyboard(callback_data.room_iden,callback_data.asAdmin)
    await call.message.answer(f"Вы уверены что хотите удалить комнату {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ?",reply_markup=kb)

@router.callback_query(CallbackFactory.filter(F.action == "confirm_delete"))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    await db.delete_room(callback_data.room_iden,call.from_user.id)
    await call.message.edit_text(f"Комната {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} удаленна",reply_markup=keyboards.choice_kb)

@router.callback_query(CallbackFactory.filter(F.action == "remove_member"))
async def remove_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    members,*_ = await db.get_members_list(callback_data.room_iden)
    kb = await keyboards.member_keyboard(members,callback_data.room_iden)
    await call.message.answer("Выберите нужный вам вариант",reply_markup=kb)

@router.callback_query(RemoveCallbackFactory.filter(F.action =="remove_member"))
async def removing_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(callback_data.user_id,callback_data.room_iden)
    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(f"Участник уже не в {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует ",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    
    await db.leave_room(callback_data.room_iden,callback_data.user_id)
    await call.message.edit_text(f"Участник удален из комнаты  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ",reply_markup = await keyboards.ok_keyboard(callback_data.room_iden,asAdmin=True))

@router.callback_query(CallbackFactory.filter(F.action =="start_event"))
async def start_event(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    
    status = await db.isStarted(callback_data.room_iden)
    if status:
        await call.message.edit_text(f"Событие уже начато  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ",reply_markup = await keyboards.room_admin_keyboard(callback_data.room_iden))
        return

    members,admin,isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        members.append(admin)
    members = [member[0] for member in members]
    if len(members)<2:
            await call.message.edit_text(f"Участников в  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} недостаточно для начала. Должно быть более 1",reply_markup = await keyboards.room_admin_keyboard(callback_data.room_iden))
            return
    
    await db.start_event(callback_data.room_iden)
    pairs = utils.randomize_members(members)
    await db.write_pairs(pairs,callback_data.room_iden)
    await call.message.edit_text(f"Событие началось в  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ",reply_markup =await keyboards.room_admin_keyboard(callback_data.room_iden))
    for user_id in members:
        await call.bot.send_message(chat_id=user_id, text=f"Событие в комнате {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} началось\nПроверте кому вы дарите",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))

@router.callback_query(CallbackFactory.filter(F.action == "who_gives"))
async def who_gives(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    status = await db.isStarted(callback_data.room_iden)
    if not status:
         await call.message.edit_text(f"Событие в комнате {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} ещё не началось ",reply_markup=await keyboards.room_member_keyboard(callback_data.room_iden))
         return
    member_id = await db.who_gives(callback_data.room_iden,call.from_user.id)
    member = await db.get_user(member_id)
    if member:
        user_info = await text.create_user_info(member)
        await call.message.answer(f"Вы дарите {user_info}",reply_markup = await keyboards.wishes_keyboard2(callback_data.room_iden,asAdmin=False))
       

@router.message(Command("ID"))
async def get_id(msg: Message):
    await msg.answer(f"ID: user_id - {msg.from_user.id}\n      chat_id - {msg.chat.id}")

@router.callback_query(CallbackFactory.filter(F.action == "create_invitation"))
async def create_invitation(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(f"Вы не участник комнаты  {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    kb = await keyboards.join_to_room(callback_data.room_iden)
    await call.message.answer(f"✉️Приглашение принять участвие в Тайном санта в комнате {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}\n<i>Если приглашение не сработало попробуйте присоединиться в ручном режиме</i>",reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == "my_wishes"))
async def my_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)

    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return

    wishes = await db.my_wishes(callback_data.room_iden,call.from_user.id)
    wishes_info = await text.create_wishes_info(wishes)

    await call.message.answer(wishes_info,reply_markup = await keyboards.wishes_keyboard(callback_data.room_iden,asAdmin=False))
   
@router.callback_query(CallbackFactory.filter(F.action == "edit_wishes"))
async def my_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)

    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    await state.set_data({'room_iden':callback_data.room_iden})
    await state.set_state(Gen.set_wishes)
    await call.message.answer("Напишите ваше пожелание",reply_markup=await  keyboards.cancel_keyboard("None",asAdmin=False))


@router.message(Gen.set_wishes)
async def edit_wishes_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    wishes = msg.text
    data = await state.get_data()
    room_iden = data.get("room_iden")
    await state.clear()

    if msg.text == "🚫Отмена":
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return
    edit_wishes =  wishes.replace('\\','/').replace('\'','`').replace('\"','`')
    room_status = await db.edit_wishes(edit_wishes,msg.from_user.id,room_iden)
    if room_status == "ROOM NOT EXISTS":
        await msg.answer("Такой комнаты не существует",reply_markup=await  keyboards.ok_keyboard("None",False))
        return
    
    if room_status == "MEMBER NOT EXISTS":
        await msg.message.edit_text(f"Вы не участник комнаты",reply_markup=await  keyboards.ok_keyboard("None",False))
        return
    
    await state.clear()
    await msg.answer(f"Вы изменили пожелание:\n{edit_wishes}",reply_markup = await keyboards.wishes_keyboard(room_iden,asAdmin=False))

@router.callback_query(CallbackFactory.filter(F.action == "see_wishes"))
async def my_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)

    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id,callback_data.room_iden)
    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]} не существует",reply_markup=await keyboards.ok_keyboard("None",asAdmin=False))
        return
    member_id = await db.who_gives(callback_data.room_iden,call.from_user.id)
    wishes = await db.my_wishes(callback_data.room_iden,member_id)
    wishes_info = await text.take_wishes_info(wishes)

    await call.message.answer(wishes_info,reply_markup = await keyboards.ok_keyboard("None",False))