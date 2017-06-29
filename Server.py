import socket
from random import randint, choice
import select 
import numpy
import math
import time
from math import *
import sys


class Client(object):
	"""
		The instances of this class are the clients that currently connected to the server.
	"""
	
	def __init__(self, name, id, socket):
		
		# The name that the client is going to be called during the game.
		self.name = name
		
		# The way the server can identify each client.
		self.id = id
		
		# The socket of the client.
		self.socket = socket
		
		# The opponent of the client.
		self.opponent = None
		
		# The game of the client.
		self.game = None
		
		# True if the player is now waiting for the next round.
		self.next_round = True
		
		# The beginning amount of money of a player.
		self.money = 450
		
		# The beginning amount of hp of a player.
		self.hp = 25
		
		# Contains all the factories of the client.
		self.factories = []	

	def new_tower_request(self, request):
		"""
			The function receives a tower request. Sends True if there's enough money to buy this tower.
		"""
		
		if request == "Machine Gun" and self.money >= 1350:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueMachine Gun"
			
		elif request == "Dark Cat" and self.money >= 300:
		
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueDark Cat"
			
		elif request == "Bomber" and self.money >= 1200:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueBomber"
		
		elif request == "Witch" and self.money >= 1200:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueWitch"
			
		elif request == "Factory1" and self.money >= 1000:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueFactory1"
		
		elif request == "Factory2" and self.money >= 6500:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueFactory2"
		
		elif request == "Factory3" and self.money >= 30000:
			
			messages_to_send[self.socket] = "Game:tower_confirmation:TrueFactory3"
			
	def allow_soldier(self, name, money):
		"""
			The function sends the client that the soldier request has approved and its opponent, the soldier itself if he has enough money. Else sends the client that the request has denied.
		"""
		
		if self.money >= money:
			
			messages_to_send[self.socket] = "Game:soldier_confirmation:True" + name
			self.money -= money
			messages_to_send[self.opponent.socket] = "Game:new_soldier:" + name
				
		else:
				
			messages_to_send[self.socket] = "Game:soldier_confirmation:False" + name
			
	def new_soldier_request(self, request):
		"""
			The function receives a soldier request. Returns True if there's enough money to buy this soldier. Else returns False.
		"""
		
		if request == "Private":
			
			self.allow_soldier("private", 15)
		
		elif request == "Private2":
			
			self.allow_soldier("private2", 30)
		
		elif request == "Private first class":
			
			self.allow_soldier("Private first class", 60)
		
		elif request == "Specialist":
			
			self.allow_soldier("Specialist", 150)
				
		elif request == "Corporal":
		
			self.allow_soldier("Corporal", 400)
				
		elif request == "Sergeant":
			
			self.allow_soldier("Sergeant", 1000)
			
		elif request == "PrivateSpaceShip":
		
			self.allow_soldier("PrivateSpaceShip", 7500)
		
		messages_to_send[self.socket] = "Game:money:" + str(self.money)

	def place_tower(self, request):
		"""
			The function receives a tower name and places it.
		"""
		
		if request == "Machine Gun":
			
			self.money -= 1350
		
		elif request == "Dark Cat":
		
			self.money -= 300
			
		elif request == "Bomber" or request == "Witch":
			
			self.money -= 1200
			
		elif request == "Factory1":
			
			self.money -= 1000
			
			self.factories.append(Factory(self, 150, 2.5))
			
		elif request == "Factory2":
			
			self.money -= 6500
			
			self.factories.append(Factory(self, 1400, 8))
			
		elif request == "Factory3":
			
			self.money -= 30000
			
			self.factories.append(Factory(self, 7500, 15))
			
		messages_to_send[self.socket] = "Game:money:" + str(self.money)
		
	def reward(self, reward):
		"""
			The function receives an amount of money and adds it to the player money.
		"""
		
		self.money += float(reward)
		
		messages_to_send[self.socket] = "Game:money:" + str(self.money)
		
	def dec_hp(self, soldier):
		"""
			The function receives a soldier name and decrees its damage from the player's hp.
		"""
		
		if soldier == "private" or soldier == "private2" or soldier == "private_first_class":
			
			self.hp -= 1
			
		elif soldier == "Specialist" or soldier == "Corporal" or soldier == "Sergeant":
			
			self.hp -= 2
			
		elif soldier == "PrivateSpaceShip":
		
			self.hp -= 5
		
		messages_to_send[self.socket] = "Game:hp:" + str(self.hp)
		
		if self.hp <= 0:
			
			self.opponent.i_win()
			
	def i_win(self):
		"""
			The function updates the both players about the winner.
		"""
		
		global disconnected_clients
		
		self.socket.send("new_message:Result:win")
		self.opponent.socket.send("new_message:Result:lose")
		
		# Disconnect both of the players.
		disconnected_clients.append(self.opponent)
		disconnected_clients.append(self)
		

class Game(object):
	"""
		The instance of the class is a game.
	"""
	
	def __init__(self, player1, player2):
	
		# The first client.
		self.player1 = player1
		
		# The second client.
		self.player2 = player2
		
		# Contains the game function.
		self.game_function = ""
		
		# The first x coordination of the function.
		self.first_x = ""
		
		# The last x coordination of the function.
		self.last_x = ""
		
		# True if all the required input was entered.
		self.game_started = False
		
		# The current round of the game.
		self.round = 0
		
		# The content of the last line round_soldiers file has. (correct only when the last line has read)
		self.last_file_round = 0
		
		# Both of the players has a maximum time of 60 seconds to decide on an input to the game.
		self.input_timer = [60, time.time()]
		
	def game_manager(self):
		"""
			The function tracks the status of the game and acts according to it.
		"""
		
		# The function acts just when the game have started.
		if self.game_started:
		
			# player1 and player2 are both ready for the next round. 
			if self.player1.next_round and self.player2.next_round:
				
				self.new_round_manager()
				
			if self.player1.factories:
				
				for factory in self.player1.factories:
					
					factory.manipulate()
			
			if self.player2.factories:
			
				for factory in self.player2.factories:
						
						factory.manipulate()
		
		else:
			
			if time.time() - self.input_timer[1] >= 1:
				
				self.input_timer = [self.input_timer[0] - 1, time.time()]
				
				messages_to_send[self.player1.socket] = "input_time:" + str(self.input_timer[0])
				
				messages_to_send[self.player2.socket] = "input_time:" + str(self.input_timer[0])
			
			if self.input_timer[0] <= 0:
				
				self.set_input()
				
	def set_input(self):
		"""
			The function sets the input of the game without considering with the both players.
		"""
		
		global messages_to_send
		
		self.game_function = choice(['sin(x)', 'cos(x)', 'sin(x)**2', 'cos(x)**2', 'cos(x)**3', 'x**2', 'x**3', 'tan(x)', 'sin(x)**2 - cos(x**2)**3'])
		
		self.first_x = str(choice(range(-10, -1)))
		
		self.last_x = str(choice(range(1, 10)))
		
		messages_to_send[self.player1.socket] = "accept:last_x_coordination:" + self.last_x + "new_message:accept:first_x_coordination:" + self.first_x + "new_message:accept:game_function:" + self.game_function + "new_message:input_status:_valid"
		messages_to_send[self.player2.socket] = "accept:last_x_coordination:" + self.last_x + "new_message:accept:first_x_coordination:" + self.first_x + "new_message:accept:game_function:" + self.game_function + "new_message:input_status:_valid"
		
		self.game_started = True
		
	def new_round_manager(self):
		"""
			The functions does all the new preparation for the next round. 
		"""
		
		self.player1.next_round = False
		
		self.player2.next_round = False
		
		self.round += 1
		
		# Calculate the soldiers for the next round.
		next_round_soldiers = self.calculate_round_soldiers()
		
		# Send both player1 and player2 the soldiers they have to face next round.
		messages_to_send[self.player1.socket] = "Game:new_round:" + str(game.round) + ":soldiers:" + next_round_soldiers
		
		messages_to_send[self.player2.socket] = "Game:new_round:" + str(game.round) + ":soldiers:" + next_round_soldiers
		
	def calculate_round_soldiers(self):
		"""
			The function generates soldiers for the next round.
		"""
		
		global pss_count
		
		# In case it's the end of the file
		try:
			
			with open("round_soldiers.txt") as file:
				
				data_in_lines = file.readlines()
				
				self.last_file_round = data_in_lines[self.round - 1]
				
				return (self.last_file_round)
				
		except:
			
			pss = ('Sergeant,' + 0)
			
			for i in range(1, pss_count):
			
				pss += (',' + 'Sergeant,' + i*3)
				
			return pss
		
	def input_completed(self):
		"""
			The function returns True if all the input attributes are setted, else returns False.  
		"""
		
		if self.game_function != "" and self.first_x != "" and self.last_x != "":
			
			return True
			
		return False
	
	def input_valid(self):
		"""
			The function returns True if the current game input is valid- if it can be rendered to path. Else returns False.
		"""
		
		if self.input_completed():
			
			if check_function(self.game_function, self.first_x, self.last_x):
				
				self.game_started = True
				
				return [True, ""]
		
		# Reset the input values.
		self.game_function = ""
		self.first_x = ""
		self.last_x = ""
		
		return [False, "Error"]
		
	def update_game_information(self, player, data):
		"""
			The function receives new information about the game and updates it. 
		"""
		
		if data == "round_ended":

			player.next_round = True
			
		if data[: 18] == "new_tower_request:":
		
			player.new_tower_request(data[18 :])
			
		elif data[: 20] == "new_soldier_request:":
			
			player.new_soldier_request(data[20: ])
			
		elif data[: 13] == "tower_placed:":
			
			player.place_tower(data[13 :])
			
		elif data[: 13] == "money_reward:":
			
			player.reward(data[13: ])
			
		elif data[: 7] == "dec_hp:":
			
			player.dec_hp(data[7: ])
			

class Factory(object):
	"""
		The instance of the class is a factory that the player can buy. The factory gives the player money each amount of time.
	"""
	
	def __init__(self, client, production, reloading):
		
		# The client who owns this factory.
		self.client = client
		
		# How much money the factory products.
		self.production = production
		
		# The time between every production (in seconds).
		self.reloading = reloading
		
		# When have started to reload (in seconds).
		self.reloading_from = time.time()
		
	def manipulate(self):
		"""
			The function reloads the factory by one more frame. If finished to reload- add the production to the player money.
		"""
		
		if time.time() - self.reloading_from >= self.reloading:
			
			self.client.money += self.production
			
			messages_to_send[self.client.socket] = "Game:money:" + str(self.client.money)
			
			self.reloading_from = time.time()

			
def check_function(function, first_x, last_x):
	"""
		The function checks if the received data is valid. If not returns False, else returns True. 
	"""
	
	try:
	
		# Check if the first coordinates is also the last one.
		if first_x == last_x:

			return False
			
	except:
		
		return False
	
	try:

		# Draw the path. If first_x/last_x aren't number, throws exception.
		for x in numpy.arange(float(first_x), float(last_x), (float(last_x) - float(first_x)) / 1050):
			
			# Calculate the y coordination of the current x coordination in the function and multiple it by the proportion to get the right pixel on the screen. 
			y = long(round(eval(function)))
		
	except Exception as e:

		return False
	
	return True
	

def match_y(y):
	"""
		Receives a y coordination and match it to the current screen (in pygame (0,0) is the top left pixel).
	"""
	
	if y > 0 or y == 0:
				
		return abs(y - 402)
			
	return abs(y) + 402

	
def set_game(player1, player2):
	"""
		The function receives two players and creates a game.
	"""
	
	global current_games
	global waiting_for_opponent
	global messages_to_send	

	player2.socket.send('new_message:0')
	messages_to_send[player2.socket] = 'name:' + player1.name
	messages_to_send[player1.socket] = 'name:' + player2.name

	player1.opponent = player2
	
	player2.opponent = player1
	
	# Create the game and append it to the current games list.
	new_game = Game(player2, player1)
	
	current_games.append(new_game)
	
	# Set the both players their new game.
	player1.game = new_game
	
	player2.game = new_game
	
	# Since now, no one is waiting for opponent.
	waiting_for_opponent = None


def update_game_property(player1, data):
	"""
		The function receives a game and data. It interprets the data and update the received game property according to it. 
	"""
	
	if len(data) > 7 and data[: 7] == "accept:":
		
		data = data[7 :]
		
		if len(data) > 14 and data[: 14] == "game_function:":
			
			player1.game.game_function = data[14 :]
			player1.opponent.socket.send("new_message:accept:" + data)
		
		elif len(data) > 21 and data[: 21] == "first_x_coordination:":

			player1.game.first_x = data[21 :]
			player1.opponent.socket.send("new_message:accept:" + data)
				
		elif len(data) > 20 and data[: 20] == "last_x_coordination:":
			
			player1.game.last_x = data[20 :]
			player1.opponent.socket.send("new_message:accept:" + data)
	
	else:
		
		if len(data) > 14 and data[: 14] == "game_function:":
			
			if player1.game.game_function == '':
			
				player1.opponent.socket.send("new_message:" + data)
				
		
		elif len(data) > 21 and data[: 21] == "first_x_coordination:":

			if player1.game.first_x == '':
			
				player1.opponent.socket.send("new_message:" + data)
				
		elif len(data) > 20 and data[: 20] == "last_x_coordination:":
			
			if player1.game.last_x == '':
			
				player1.opponent.socket.send("new_message:" + data)
	
	if player1.game.input_completed():
		
		input_status = player1.game.input_valid()

		if input_status[0]:
			
			player1.socket.send("new_message:input_status:_valid")
			player1.opponent.socket.send("new_message:input_status:_valid")
		
		else:
			
			player1.socket.send("new_message:input_status:_not_valid:" + input_status[1])
			player1.opponent.socket.send("new_message:input_status:_not_valid:" + input_status[1])
			

def send_messages(wlist):
	"""
		The function receives the current wlist and the messages to send dictionary as global. The function sends all the messages that their clients are currently in rlist.
	"""
	
	global messages_to_send
	
	for socket in messages_to_send:
		
		if socket in wlist:
			
			try:

				socket.send("new_message:" + messages_to_send[socket])
				
				messages_to_send[socket] = '$'
			
			except:
				
				pass
			
	# Delete the messages that already have sent.
	remove = [socket for socket in messages_to_send if messages_to_send[socket] == '$']
	
	for socket in remove: del messages_to_send[socket]
	

def generate_id(number_list):
	"""
		The function generates new id between 10**16 -1 and 10**20, the function makes sure that the is isn't in the received list.
	"""
	
	num = randint(10**16, 10**20)
	
	while num in number_list:
		
		num = randint(10**16, 10**20)
	
	return str(num)
	
	
def number_length(string):
	"""
		returns the number in the beginning of the string.
	"""
	
	number = ''
	for num in string:
		if num.isdigit():
				number += str(num)
		else:
			break
	return number
	
	
def get_client_by_id(id):
	"""
		The function receives an id and returns the client that it's his id. If no client found with thit id returns None.
	"""
	
	for client in connected_clients:
		
		if client.id == id:
			
			return client
	
	return None
	

def client_to_player(client, game):
	"""
		The function receives a client and its game. It returns the following address (player1 / player2) of the game according to the client.
	"""
	
	if client.id == game.player1.id:
		
		return game.player1
	
	else:
		
		return game.player2
	
	
def get_client_by_socket(client_socket):
	"""
		The function receives a socket and returns the client that its his socket. If no client found with this socket returns None.
	"""
	
	for client in connected_clients:
		
		if client.socket == client_socket:
			
			return client
	
	return None
	
	
"""
	PREPARATION FOR THE MAIN LOOP.
"""

# Create the server socket.
server_socket = socket.socket()

# In case there's already a running server.
try:
	# Bind the server socket.
	server_socket.bind(('0.0.0.0', 951))
except:
	"A server is already running."
	sys.exit()

# Set the listeners capacity to 5.
server_socket.listen(5)

# Contains all the connected clients.
connected_clients = []

# Contains all the open sockets.
open_clients_sockets = []

# Clients that are no longer connected to the server.
disconnected_clients = []

# Contains all the games the currently being playing.
current_games = []

# Contains all the occupied ids.
occupied_ids = []

# Contains messages that have to be sent in the next loop and the socket that the message has to be sent to.
messages_to_send = {}

# Contains the client that is currently waiting for an opponent.
waiting_for_opponent = None

# When the round are over start send private space ships.
pss_count = 1


"""
	MAIN LOOP.
"""

while True:

	rlist, wlist, xlist = select.select([server_socket] + open_clients_sockets, open_clients_sockets, [])

	send_messages(wlist)
	
	for current_socket in rlist:
		
		# If the current socket equals to the server socket it's trying to connect, accept it and append it to open_clients_sockets.
		if current_socket is server_socket:
			
			(new_socket, address) = server_socket.accept()
			
			# Receive the client's name.
			client_name = new_socket.recv(1024)
			
			# Create a random number between 10**16 - 10**20
			client_id = generate_id(occupied_ids)
			
			# Add it to the occupied ids.
			occupied_ids.append(client_id)
			
			# Create the client and append it to the connected clients list.
			new_client = Client(client_name, client_id, new_socket)
			connected_clients.append(new_client)
			
			# Append the client socket to open_clients_sockets
			open_clients_sockets.append(new_socket)
			
			# Send to the client its id so he can identify next time he sends data to the server, before the id 0 represents the client has an opponent and 1 that he has to wait.
			try:
				
				# If there is a client that currently waiting for an opponent, send the current client that an opponent was found and set the game.
				if waiting_for_opponent:

					new_socket.send('new_message:0' + client_id)
					
					set_game(new_client, waiting_for_opponent)

				else:

					new_socket.send('new_message:1' + client_id)
					
					waiting_for_opponent = new_client
					
			except:
				
				disconnected_clients.append(new_client)
				continue
			
		# See what the current client sent.
		else:
		
			try:
				
				received_data = current_socket.recv(1024)
				
			except:
				
				disconnected_clients.append(new_client)
				continue
			
			if received_data[: 12] == "new_message:":
			
				received_data = received_data[12 :].split("new_message:")
				
				for data in received_data:
					
					# This client left the server. 
					if data == "":
						
						disconnected_clients.append(get_client_by_socket(current_socket))
						continue
				
				# Extract the id of the client from the data he sent.
				client_id = number_length(data)
				
				# Find the client that it's his id.
				client = get_client_by_id(client_id)
				
				# If no client were found disconnect this socket
				if client == None:
					
					current_socket.shutdown(socket.SHUT_RDWR)
					current_socket.close()
				
				# Update the data- now without the id of the client in its beginning.
				data = data[len(client_id):]
				
				if data[:14] == "game_property:":
					
					update_game_property(client, data[14:])
					
				elif data[: 5] == "Game:":
					
					client.game.update_game_information(client_to_player(client, client.game), data[5 :])
			
			# Damaged data, disconnect this socket.
			else:
				
				try:
					disconnected_clients.append(get_client_by_socket(current_socket))
				except:
					open_clients_sockets.remove(current_socket)
				current_socket.shutdown(socket.SHUT_RDWR)
				current_socket.close()

	# Iterate over all the players that are currently waiting for data.
	for current_socket in wlist:

		current_client = get_client_by_socket(current_socket)
		
		# If there are two players that are looking for opponent, set their game.
		if not current_client.opponent and waiting_for_opponent and waiting_for_opponent is not current_client:
			
			set_game(current_socket, waiting_for_opponent)
	
	# Manage everything related to the game itself.
	for game in current_games:
		
		game.game_manager()
	
	# Iterate over all the clients that have been disconnected. 
	for client in disconnected_clients:
		
		# If the client that left was waiting for opponent set waiting for opponent to None.
		if waiting_for_opponent and client.socket is waiting_for_opponent.socket:

			waiting_for_opponent = None
		
		else:
			
			# In case its opponent has left the game right now.
			try:
				client.opponent.socket.send("new_message:Result:win")
				current_games.remove(client.game)
			except:
				
				pass
		
		# Disconnect the client's opponent. 
		try:
			open_clients_sockets.remove(client.opponent.socket)
			occupied_ids.remove(client.opponent.id)
			connected_clients.remove(client.opponent)
			client.opponent.socket.shutdown(socket.SHUT_RDWR)
			client.opponent.socket.close()
			
		except:
			pass
		
		# Disconnect the client.
		try:
			
			open_clients_sockets.remove(client.socket)
			occupied_ids.remove(client.id)
			connected_clients.remove(client)
			client.socket.shutdown(socket.SHUT_RDWR)
			client.socket.close()
			
		except:
			pass
			
	disconnected_clients = []