import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN, LOCAL_SERVER, ERL_ID, admin_ids
from  db.close_to_average.handler import add_answer, has_answered, get_answers, get_random_with_guess

if LOCAL_SERVER != None:
	telebot.apihelper.API_URL = LOCAL_SERVER + "/bot{0}/{1}"
	telebot.apihelper.FILE_URL = LOCAL_SERVER

bot = telebot.TeleBot(BOT_TOKEN)

#############################################################
##################### Deep linking ##########################
#############################################################

CLOSE_TO_AVERAGE_MESSAGE_TEXT = """

Selecciona un número de la lista a continuación 🧐; resultarán ganadores del juego aquellos que hayan marcado el valor más cercano a dos tercios (2/3) del promedio de los números marcados por todos los participantes 🧮.

Les pedimos por supuesto que no comenten su nada relacionado con su voto 🙅 y lo hagan solo si tienen dudas con las reglas 😉👍

Entre todos los ganadores, además de un emoji de diploma y gladiolo 📜🌺 seleccionaremos uno al azar y le realizaremos una recarga de 110 CUP a su teléfono 📱 para que se motiven un poco 😅

El ganador del premio en ¿metálico? ¿digital? 🤔🤷‍♂️ deberá ser suscriptor de nuestro canal @ElRadicalLibre. Así que ya sabes, comparte con tus amigos y diles que se suscriban 🤠

¡Elige bien, porque solo tendrás una oportunidad!
"""

CLOSE_TO_AVERAGE_POST_URL = 'https://t.me/ElRadicalLibre/2378'

def close_to_average(message):
	keyboard = InlineKeyboardMarkup()
	for row in range(5):
		keyboard.row(*[InlineKeyboardButton(str(num), callback_data=f'close_to_average_guess {num}') for num in range(4 * row + 1, 4 * row + 5)])
	bot.send_message(message.chat.id, CLOSE_TO_AVERAGE_MESSAGE_TEXT, reply_markup=keyboard)

start_events = {
	'close_to_average': close_to_average
}

#########################################################
##################### Commands ##########################
#########################################################

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	splitted = message.text.split(' ', 1)
	payload = 'not_a_payload'
	if len(splitted) > 1:
		payload = splitted[1]
	if payload in start_events:
		start_events[payload](message)
	else:
		bot.send_message(message.chat.id, f"Hola, soy el bot de juegos de <a href='https://t.me/elRadicalLibre'>El Radical Libre</a>", parse_mode="HTML")

@bot.message_handler(commands=['watch'])
def watch_results(message):
	if message.from_user.id in admin_ids:
		ans = get_answers()
		s = 0
		c = 0
		for guess, count in ans:
			c += count
			s += guess * count
		
		ave = s / c
		ave_2_3 = 2 * ave / 3

		best_guess = 0
		diff = 100
		for guess, _ in ans:
			if abs(guess - ave_2_3) < diff:
				diff = abs(guess - ave_2_3)
				best_guess = guess

		winner, = get_random_with_guess(best_guess)

		bot.send_message(message.chat.id, f'Average: {ave}\n2/3 average: {ave_2_3}\nBest guess: {best_guess}\nWinner: <a href="tg://user?id={winner}">{winner}</a>\nHistogram:\n{ans}', parse_mode="HTML")

########################################################
##################### Queries ##########################
########################################################

@bot.callback_query_handler(func=lambda q: True)
def handle_queries(callback: telebot.types.CallbackQuery):
	if callback.data.startswith('close_to_average_guess'):
		if bot.get_chat_member(ERL_ID, callback.from_user.id).status in ['left', 'kicked']:
			bot.answer_callback_query(callback.id, text="Necesitas ser miembro del canal para poder participar en el juego.",show_alert=True)
		else:
			if has_answered(callback.from_user.id):
				bot.answer_callback_query(callback.id, text="Ya respondiste antes a este juego.")
			else:
				guess = int(callback.data.split(' ', 1)[1])
				add_answer(callback.from_user.id, guess)
				bot.answer_callback_query(callback.id, text="Registrada tu decisión. ¡Suerte!")

				keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Tu respuesta: {guess}", url=CLOSE_TO_AVERAGE_POST_URL)]])
				bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=keyboard)


if __name__ == '__main__':
	bot.polling()