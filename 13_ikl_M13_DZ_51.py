from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# запуск своего телеграмбота
api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# инициализация обычной клавиатуры
kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=False)
"""
инициализация клавиатуры, где параметры:
row_width - количество столбцов кнопок, (int)
resize_keyboard - будет ли клавиатура растягиваться, (bool)
one_time_keyboard - разовая ли клавиатура, (bool)
"""
# Создание обычных кнопок
button_1 = KeyboardButton(text='Рассчитать норму калорий')
# button_2 = KeyboardButton(text='Информация')

# Запуск обычных кнопок
kb.add(button_1)
# kb.row(button_1, button_2) # кнопки в линию

# инициализация Inline-клавиатуры
kb_inline = InlineKeyboardMarkup()

# создание Inline-кнопок
button_1_inline = InlineKeyboardButton(text='Расчет нормы', callback_data='calories')
button_2_inline = InlineKeyboardButton(text='Формула расчета', callback_data='formulas')

# запуск Inline-кнопок
kb_inline.add(button_1_inline, button_2_inline)

# Вроде создал ... но не понадобилось в итоге
# # создаю Inline-menu
# start_menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text='calories'),
#             KeyboardButton(text='formulas')
#         ],
#     ], resize_keyboard=True)


@dp.message_handler(commands=['start'])
async def start(message):
    print('Кто-то вошел в бот') # это сообщения для меня (вывода на консоль)
    await message.answer(f'Привет!\nЯ бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать норму калорий')
async def main_menu(message):
    await message.answer('Выбери опцию', reply_markup=kb_inline)  # активизировал Inline-клаву


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    print('Поступил запрос на информацию Formulas') # это сообщения для меня (вывода на консоль)
    await call.message.answer(f"Упрощенный вариант формулы Миффлина-Сан Жеора:\n"
                              f"для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5\n"
                              f"для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161")
    await call.answer()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    print('Поступил запрос на расчет Calories') # это сообщения для меня (вывода на консоль)
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(first=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    await state.update_data(third=message.text)
    data = await state.get_data()
    # для мужчин: 10 х вес(кг) + 6,25 x рост(см) – 5 х возраст(г) + 5
    # для женщин: 10 x вес(кг) + 6,25 x рост(см) – 5 x возраст(г) – 161
    await message.answer(f'Ваша норма каллорий:\n'
                         f'для мужчин'
                         f'{10 * int(data["first"]) + 6.25 * int(data["second"]) - 5 * int(data["third"]) + 5};\n'
                         f'для женщин'
                         f'{10 * int(data["first"]) + 6.25 * int(data["second"]) - 5 * int(data["third"]) - 161}.')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
