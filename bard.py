from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import requests

app = Client("my_bot", api_id=19099900, api_hash="2b445de78e5baf012a0793e60bd4fbf5", bot_token="6390766852:AAHAXsP3NHPX2NbnRaFDZA9ZH1h6FyNH1K4")
API_URL = "https://opentdb.com/api.php?amount=10&category=31&type=multiple"

def get_quiz_questions():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    return None

current_question = 0
questions = get_quiz_questions()

@app.on_message(filters.command("start"))
def start_command(client, message):
    send_welcome_message(client, message.chat.id)

@app.on_message(filters.command("quiz"))
def quiz_command(client, message):
    global current_question
    current_question = 0
    send_question(client, message.chat.id)

@app.on_message(filters.text)
def handle_text(client, message):
    if not message.text.startswith("/"):
        handle_answer(client, message)

@app.on_callback_query()
def callback_handler(client, callback_query):
    global current_question  # Add this line
    user_id = callback_query.from_user.id
    selected_option = int(callback_query.data)

    if current_question < len(questions):
        correct_option = questions[current_question]['correct_option']
        if selected_option == correct_option:
            client.answer_callback_query(callback_query.id, text="Correct! 🎉")
            client.send_message(user_id, "Congratulations! You've earned a reward!")
        else:
            client.answer_callback_query(callback_query.id, text="Wrong answer. 😕")
        
        current_question += 1
        send_question(client, user_id)


def send_welcome_message(client, chat_id):
    welcome_message = "Welcome to the Anime Quiz Bot! Use /quiz to start the quiz."
    client.send_message(chat_id, welcome_message)

def send_question(client, chat_id):
    if current_question < len(questions):
        question = questions[current_question]['question']
        options = questions[current_question]['incorrect_answers']
        correct_option = questions[current_question]['correct_answer']

        options.append(correct_option)
        options = sorted(options)  # Shuffle options here if you want random order

        option_buttons = []
        for idx, option in enumerate(options):
            option_buttons.append([InlineKeyboardButton(f"{idx + 1}. {option}", callback_data=str(idx))])

        reply_markup = InlineKeyboardMarkup(option_buttons)

        client.send_message(chat_id, f"Question {current_question + 1}:\n{question}", reply_markup=reply_markup)
    else:
        client.send_message(chat_id, "Quiz completed!")

if __name__ == "__main__":
    app.run()
