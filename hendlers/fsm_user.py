from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import client_kb
from config import bot, ADMIN
from database import bot_db


# states
class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    surname = State()
    age = State()
    tag = State()
    gender = State()

    is_student = State()
    is_teacher = State()
    is_admin = State()


# start fsm
async def fsm_start(message: types.Message):
    if message.from_user.id == ADMIN:
        await FSMAdmin.photo.set()
        await bot.send_message(message.chat.id,
                               "Привет босс, отправь фото человека...",
                               reply_markup=client_kb.cancel_markup)
    else:
        await message.answer("Ты не админ!")


# load photo
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMAdmin.next()
    await bot.send_message(message.chat.id,
                           "Хорошo\nКак его зовут?")


# load name
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await bot.send_message(message.chat.id,
                           "Какая у него фамилия?")


# load surname
async def load_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await FSMAdmin.next()
    await bot.send_message(message.chat.id,
                           "Сколько ему лет?")


# load age
async def load_age(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['age'] = int(message.text)
        await FSMAdmin.next()
        await bot.send_message(message.chat.id,
                               "Отправь ключевое слово по которому его можно узнать (Кличку, внешность)\n"
                               "Например: Бека незнайка или Айдана бэкенд")
    except:
        await bot.send_message(message.chat.id, "Только числами!")


async def load_tag(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tag'] = message.text
    await FSMAdmin.next()
    await bot.send_message(message.chat.id,
                           "Какого он(а) пола?")


async def load_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await FSMAdmin.next()
    await bot.send_message(message.chat.id,
                           "Он учился (учится) в GeekTech?")


async def load_is_student(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        result = True
    elif message.text.lower() == "нет":
        result = False
    else:
        await message.answer("Пиши только да или нет!")

    if type(result) == bool:
        async with state.proxy() as data:
            data['is_student'] = result
        await FSMAdmin.next()
        await bot.send_message(message.chat.id,
                               "Он преподает в GeekTech?")


async def load_is_teacher(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        result = True
    elif message.text.lower() == "нет":
        result = False
    else:
        await message.answer("Пиши только да или нет!")

    if type(result) == bool:
        async with state.proxy() as data:
            data['is_teacher'] = result
        await FSMAdmin.next()
        await bot.send_message(message.chat.id,
                               "Он из администрации (отдела продаж)?")


async def load_is_admin(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        result = True
    elif message.text.lower() == "нет":
        result = False
    else:
        await message.answer("Пиши только да или нет!")

    if type(result) == bool:
        async with state.proxy() as data:
            data['is_admin'] = result
        await bot_db.sql_command_insert(state)
        await state.finish()
        await bot.send_message(message.chat.id,
                               "Сохранено!")


# form exit
async def cancel_form(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Отмена заполнения")


# **************************** LESSON 3 ***************************************

async def delete_data(message: types.Message):
    if message.from_user.id == ADMIN:
        results = await bot_db.sql_command_all(message)
        for result in results:
            await bot.send_photo(
                message.from_user.id, result[0],
                caption=f"Name: {result[1]} {result[4]}\n"
                        f"Surname: {result[2]}\n"
                        f"Age: {result[3]}\n",
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                    f"delete {result[1]}",
                    callback_data=f'delete {result[4]}'
                )))
    else:
        await message.answer("Permission denied!")


async def complete_delete(call: types.CallbackQuery):
    await bot_db.sql_command_delete(call.data.replace('delete ', ''))
    await call.answer(text="Deleted", show_alert=True)
    await bot.delete_message(call.message.chat.id, call.message.message_id)


def register_handler_fsmAdminGetUser(dp: Dispatcher):
    dp.register_message_handler(cancel_form, state="*", commands="cancel")
    dp.register_message_handler(cancel_form, Text(equals='cancel', ignore_case=True), state="*")

    dp.register_message_handler(fsm_start, commands=["reg"])
    dp.register_message_handler(load_photo, content_types=["photo"], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_surname, state=FSMAdmin.surname)
    dp.register_message_handler(load_age, state=FSMAdmin.age)
    dp.register_message_handler(load_tag, state=FSMAdmin.tag)
    dp.register_message_handler(load_gender, state=FSMAdmin.gender)
    dp.register_message_handler(load_is_student, state=FSMAdmin.is_student)
    dp.register_message_handler(load_is_teacher, state=FSMAdmin.is_teacher)
    dp.register_message_handler(load_is_admin, state=FSMAdmin.is_admin)

    dp.register_message_handler(delete_data, commands=['delete'])
    dp.register_callback_query_handler(complete_delete, lambda call: call.data and call.data.startswith("delete "))
