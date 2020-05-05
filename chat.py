from pyrogram			import InlineKeyboardMarkup, InlineKeyboardButton
from words.words		import reacts, triggers
from words.ru.service   import ru_service
from words.en.service   import en_service
from small_func			import p
from random		 		import choice
from time			    import sleep
import traceback 
import re

p = p()

class Chat:
	def __init__(self, app, msg):
		self.title  = msg.chat.title
		self.id		= msg.chat.id
		self.config = { 'state'	: True,
						'mood'	: 'nyan',
						'lang'	: 'ru',}
		self.users   = {'on'  	: set(),
						'off'	: set()}
	
	def init_chat(self, app, msg):
		try:str(self.hnkw_id)
		except:	self.hnkw_id = app.get_me().id
		
		def qqq(uid):
			if self.check_usr(uid) == False: 
				self.users['off'].add(uid)

		qqq(msg.from_user.id)
		if msg['reply_to_message']:
			qqq(msg.reply_to_message.from_user.id)

	def replaier(self, app, msg):
		txt   = str(msg.text)
		txt_l = txt.lower()

		if ((self.config['state'] and msg.from_user.id in self.users['on']) or
			(msg['reply_to_message'] and msg['reply_to_message']['from_user']['id'] == self.hnkw_id) or
			'@hanekawa_nyanbot' in txt_l):
			reactions	= reacts[self.config['lang']][self.config['mood']]

			for trigger, option in triggers.items():
				if re.search(r'\b'+trigger+r'\b', txt_l):
					try:
						reaction = choice(reactions[option])
						reaction.reply(app, msg)
					except Exception as e:
						error	= f'{e}\n{traceback.format_exc()}'
						text	= f'Trigger: {trigger}\nOption: {option}'
						self.send_error(app, msg, error, text)
						
	def rp_funcs(self, app, msg):
		service = self.select_service()
		def nyan_roleplay(oth_username):
			
			roleplays = ('pat', 'hug', 'koos', 'lick', 'jamk', 'kiss')

			for t in roleplays:
				if re.search(t , msg.command[0]):
					txt = f'**✵{username}** {service[t]} **{oth_username}**'
					p.roleplay_send(app, msg, txt)
		
		username = msg.from_user.first_name

		if re.search(r'me', msg.command[0]):
			txt = (msg.text).replace('/me', f'**✵{username}**')
			p.roleplay_send(app, msg, txt)

		elif msg.reply_to_message is not None:
			reply_username  = msg.reply_to_message.from_user.first_name
			nyan_roleplay(reply_username)
		else:
			ids = []
			for i in self.users.values():
				ids.extend(i)
			user_id = choice(ids)
			user = app.get_chat_member(msg.chat.id, user_id).user
			oth_username = f'@{user.username}' if user.username else user.first_name
			nyan_roleplay(oth_username)
	
	def configurate_message(self, app, msg):
		"""
		Отправляет первичную клавиатуру для настройки бота.
		"""
		service = self.select_service()
		uid = msg.from_user.id
		if p.check_admin(app, str(msg.chat.id), uid) or uid == 600432868:
			buttons = [['lang', 'mood'], ['chat_stats', 'state'], ['vw_user', 'ch_user']]  
		else: 
			buttons = [['chat_stats'], ['vw_user'], ['ch_user']]

		kb = self.draw_kb(buttons)
		app.send_message(msg.chat.id, service['options'], reply_markup=InlineKeyboardMarkup(kb))
		p.msg_del(app, msg)

	def configurate_callback(self, app, query):
		"""
		Изменяет настройки бота в определенном чате, администрацией или создателем бота.
		"""
		service = self.select_service()
		msg = query.message
		uid = query.from_user.id
		states = {	'mood' : ['nyan', 'lewd', 'angr', 'scar'],
					'lang' : ['ru', 'en'],
					'state': ['con', 'coff']}
		usr_conf = ['uon', 'uoff']
		kb, txt = None, None
		if   query.data == 'chat_stats':	txt 					 = self.chat_stats()
		elif query.data in usr_conf:		txt 					 = self.ch_user(query, query.data.replace('u',''))
		elif query.data == 'vw_user':		txt 					 = service['admin_user_state'].format(str(query.from_user.first_name), service[self.check_usr(uid)])
		elif query.data in states['mood']: 	txt, self.config['mood'] = service['mood_change'] % service[query.data], query.data
		elif query.data in states['lang']:	txt, self.config['lang'] = service['lang_change'] % service[query.data], query.data
		elif query.data == 'con':			txt, self.config['state']= service['chat_on'], True
		elif query.data == 'coff':			txt, self.config['state']= service['chat_off'], False
		elif query.data == 'ch_user':		txt, kb					 = service['ch_user?'], self.draw_kb([['uon', 'uoff']])
		elif p.check_admin(app, str(msg.chat.id), uid) or uid == 600432868:
			for x, y in states.items():
				if query.data == x:			txt, kb 				 = service["set?"] % service[x].lower(), self.draw_kb([y])
		
		if	  kb is not None: 
			msg.edit_text(txt, reply_markup=InlineKeyboardMarkup(kb))
		elif txt is not None: 
			p.msg_del(app, query.message)	
			p.admin_send(app, msg, txt)

	def chat_stats(self):
		service = self.select_service()
		answer = f'{service["chat_stats"]}:\n\n'
		
		symbols = {	True : '✅',	'ru' : '🇷🇺',
					False: '❌', 'en' : '🇺🇸',}

		for setting, state1 in self.config.items():
			if   state1 in symbols.keys():	z = symbols[state1] 
			elif state1 in service.keys():	z = service[state1]
			else:							z = state1
			answer += f'{service[setting]}: {z}\n'
		return answer
		
	def check_usr(self, id):
		"""Определяет в какой из БД присутствует пользователь.
		"""
		for name, someset in self.users.items():
			if id in someset: return name
		return False
	
	def ch_user(self, query, command):
		"""Перемещает пользователя в указанную БД.
		"""
		service = self.select_service()
		commands = ('on', 'off')
		if command in commands:
			usr = query.from_user

			state = self.check_usr(usr.id)
			if state == command:	
				return service['same_user_cond'].format(str(usr.first_name), str(command))  
			else:
				def ch_state(from_cond, to_cond):
					if (re.search(r'^'+from_cond,   state) and 
						re.search(r'^'+  to_cond, command)):		
						self.users[from_cond].remove(usr.id)	
						self.users[  to_cond].add(usr.id)

				ch_state('on', 'off')
				ch_state('off', 'on')

				return service['admin_user_state'].format(str(usr.first_name), service[command])  

	def draw_kb(self, rows):
		service = self.select_service()
		keyboard = []
		for somelist in rows:
			row = []
			for button in somelist:
				row.append(InlineKeyboardButton(service[button], callback_data=button))
			keyboard.append(row)
		return keyboard
	
	def select_service(self):
		if   self.config['lang'] == 'ru': return ru_service
		elif self.config['lang'] == 'en': return en_service
	
	@staticmethod
	def send_error(app, msg, error, txt=''):
		c = msg.chat
		u = msg.from_user
		ln = u['last_name'] if u['last_name'] else ''
		un = u['username']  if u['username']  else ''
		app.send_message(-1001328058005,
f"""**@hanekawa_nyanbot**
Chat: **{c.title}**
Chat ID: **{c.id}**
Message ID: **{msg.message_id}**
User: **{u.first_name} {ln} (@{un})**
User ID: **{u.id}**\n
{txt}\n
Error: {error}\n
""")