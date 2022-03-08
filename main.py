from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from persistance.db_connection import DbConnection
from persistance.entity.answer_entity import AnswerEntity
from persistance.repo.answer_repo import AnswerRepo
from persistance.entity.user_entity import UserEntity
from persistance.repo.user_repo import UserRepo
from persistance.entity.question_entity import QuestionEntity
from persistance.repo.question_repo import QuestionRepo

bot: Bot = Bot("5194452695:AAE-iTnAvsaX_E82ltnc3NaDNlE752vftPc")
dp: Dispatcher = Dispatcher(bot)

db_connection = DbConnection("db")
answer_repo = AnswerRepo(db_connection)
user_repo = UserRepo(db_connection)
question_repo = QuestionRepo(db_connection)


@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer(
        f"Привіт!\n"
        f"Цей бот для збору заявок на надання допомоги з трансфером через кордон та пошуком житла. Будь-ласка, дайте відповідь на наступні декілька запитань аби наші волонтери змогли надати вам якісну допомогу.\n"
        f"Для заповнення форми пропишіть /form"
                         )


@dp.message_handler(commands=["form"])
async def start_handler(message: Message):
    current_question = 0

    user = UserEntity(message.from_user.id, message.from_user.username, current_question)
    user_repo.save_or_update(user)

    if message.from_user.username is None:
        await message.answer(f"Не можу знайти ваш телеграм тег\n"
                             f"Залиште свій номер для зв'язку")
    else:
        current_question += 1

        user = UserEntity(message.from_user.id, message.from_user.username, current_question)
        user_repo.save_or_update(user)

        questions = question_repo.find_all_questions()
        question: QuestionEntity = questions[0]

        await message.answer(question.text)


@dp.message_handler(commands=["send"])
async def start_handler(message: Message):

    user: UserEntity = user_repo.find_user_by_id(message.from_user.id)

    if user is None or user.current_question is None:
        await message.answer("Для того щоб заповнити заявку пропишіть /form")
        return

    user.ready = 1
    user_repo.save_or_update(user)

    await message.answer(f"Заявка збережена")


@dp.message_handler(commands=["process"])
async def process_handler(message: Message):
    if message.from_user.username not in ["telehina", "neonflame"]:
        await message.answer("Тебе не має у списку адмінів")
        return

    users = user_repo.find_all_ready_and_not_processed()
    if len(users) == 0:
        await message.answer("Всі заявки оброблені")
        return

    user: UserEntity = users[0]
    answers = answer_repo.find_all_answers_by_user_id(user.id)
    questions = question_repo.find_all_questions()

    if user.username != 'None':
        text = "@{0}\n".format(user.username)
    else:
        text = "{0}\n".format(user.contact_info)

    for i in range(0, len(questions)):
        text += "- " + questions[i].text + "\n"
        text += answers[i].text + "\n"

    await message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="✅",
                    callback_data=str(user.id)
                )]
            ]
        )
    )


@dp.callback_query_handler()
async def process(callback: CallbackQuery):
    if callback.from_user.username not in ["telehina", "neonflame"]:
        await callback.message.answer("Тебе не має у списку адмінів")
        return

    processed_user_id = int(callback.data)
    processed_user = user_repo.find_user_by_id(processed_user_id)
    processed_user.processed = 1
    user_repo.save_or_update(processed_user)

    await callback.answer("Оброблено")
    await callback.message.delete()

    await process_handler(callback.message)


@dp.message_handler()
async def message_handler(message: Message):
    user: UserEntity = user_repo.find_user_by_id(message.from_user.id)

    if user.current_question == 0:
        user.contact_info = message.text
        user.current_question += 1
        user_repo.save_or_update(user)
        await message.answer(f"Контакт для зв`язку записаний " + user.contact_info + "\n"
                             f"Оновити контактну інформацію можна командою /form")
        question = question_repo.find_by_id(user.current_question)
        await message.answer(question.text)
        return

    if user is None or user.current_question is None:
        await message.answer("Для того, щоб заповнити заявку пропишіть /form")
        return

    if user.current_question > question_repo.count():
        await message.answer("/send")
        return

    answer = AnswerEntity(
        user_id=message.from_user.id,
        question_id=user.current_question,
        text=message.text
    )
    answer_repo.save_or_update(answer)

    if user.current_question >= question_repo.count():
        user.current_question += 1
        user_repo.save_or_update(user)

        await message.answer("Для того щоб відправити заявку пропишіть /send")
        return

    user.current_question += 1
    user_repo.save_or_update(user)

    question = question_repo.find_by_id(user.current_question)
    await message.answer(question.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
