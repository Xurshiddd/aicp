import telebot
from telebot import types
import os
from config import BOT_TOKEN
from db import passport_exists, save_user, get_user_by_passport
from generator import generate_docx_and_pdf

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
temp_data = {}

# Step states
steps = [
    'phone', 'fio', 'pasport_seria_id', 'jshshir', 'tugulgan_sana', 'jinsi', 'manzili', 'talim_muassasasi', 'rasm'
]

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(btn)

    bot.send_message(chat_id, "Assalomu alaykum! Iltimos, telefon raqamingizni yuboring.", reply_markup=markup)
    user_states[chat_id] = 'phone'
    temp_data[chat_id] = {'chat_id': chat_id}

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    chat_id = message.chat.id
    if user_states.get(chat_id) != 'phone':
        return

    temp_data[chat_id]['phone'] = message.contact.phone_number
    user_states[chat_id] = 'fio'
    bot.send_message(chat_id, "F.I.SH ni kiriting:")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if not state or state == 'rasm':
        return

    temp_data[chat_id][state] = message.text.strip()

    next_index = steps.index(state) + 1
    if next_index < len(steps):
        next_state = steps[next_index]
        user_states[chat_id] = next_state

        questions = {
            'jshshir': "JSHSHIR:",
            'pasport_seria_id':"Passport Seria Id",
            'tugulgan_sana': "Tug'ilgan sanani kiriting misol(2000-10-25):",
            'jinsi': "Jinsingiz (erkak/ayol):",
            'manzili': "Yashash manzilingiz (passportdagi):",
            'talim_muassasasi': "tugatgan ta'lim muassasasi nomi:",
            'rasm': "Rasmingizni (3x4) yuboring:",
        }

        bot.send_message(chat_id, questions.get(next_state, f"{next_state} ni kiriting:"))
    else:
        bot.send_message(chat_id, "Iltimos, rasm yuboring.")

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state != 'rasm':
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    photo_path = os.path.join('upload', f"{chat_id}.jpg")
    with open(photo_path, 'wb') as f:
        f.write(downloaded_file)

    temp_data[chat_id]['rasm_path'] = os.path.abspath(photo_path)

    # Ma'lumotlarni bazaga yozish
    save_user(temp_data[chat_id])
    pasport = temp_data[chat_id]['pasport_seria_id']

    bot.send_message(chat_id, "Ma'lumotlaringiz saqlandi.")
    send_download_button(chat_id, pasport)

    user_states.pop(chat_id, None)
    temp_data.pop(chat_id, None)


def send_download_button(chat_id, pasport):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📄 Abiturient varaqasini yuklash", callback_data=f"download:{pasport}")
    markup.add(btn)
    bot.send_message(chat_id, "Quyidagi tugma orqali hujjatni yuklab olishingiz mumkin:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('download:'))
def download_doc(call):
    pasport = call.data.split(':')[1]
    user = get_user_by_passport(pasport)

    if user:
        file_path = generate_docx_and_pdf(user)
        bot.send_document(call.message.chat.id, open(file_path, 'rb'))
    else:
        bot.send_message(call.message.chat.id, "Ma'lumot topilmadi.")


print("Bot ishga tushdi")
bot.infinity_polling()
