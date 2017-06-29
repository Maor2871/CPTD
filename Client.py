import pygame
import sys
import socket
from pygame.locals import *
from math import *
import math
import numpy
import os.path
import select
from PIL import Image
from random import shuffle, randint, choice


class Button(object):
	"""
		This class represents a button. the button is an image which have the abilities of a button- it can alerts when it get pressed and
		call a function when it does. If die is True then the button is disposable.
	"""

	def __init__(self, coordinates, image, function, die, DISPLAYSURF):
		
		self.coordinates = coordinates
		
		self.image_name = image
		
		# Contains the loaded image.
		self.image = pygame.image.load(image)

		self.function = function
		
		self.die = die
		
		self.DISPLAYSURF = DISPLAYSURF
		
		self.active = True
		
	def set_button(self):
		"""
			the function displays the button according to its coordinates and image.
		"""
	
		self.DISPLAYSURF.blit(self.image, self.coordinates)
		
	def press(self):
		"""
			Call the function of the button.
		"""		

		self.function()
		
	def is_pressed(self, click_coor):
		"""
			The function receives coordinates and check if those coordinates are in the button area. If they are returns True, else returns False.
		"""
		
		if self.active:
		
			# Create a list with all the possible x coordinates.
			x_length = self.image.get_rect().topright[0] - self.image.get_rect().topleft[0]
			x_range = range(self.coordinates[0], self.coordinates[0] + x_length)
			
			#Create a list with all the possible y coordinates.
			y_length = self.image.get_rect().bottomleft[1] - self.image.get_rect().topleft[1]
			y_range = range(self.coordinates[1], self.coordinates[1] + y_length)

			if click_coor[0] in x_range and click_coor[1] in y_range:
				return True

		return False
		

class Input_Box(Button):
	"""
		The instances of the class are input boxes.
	"""
	
	def __init__(self, coordination, image, max_input_length, text_color, font, font_size, line_capacity, lines, request):
	
		super(Input_Box, self).__init__(coordination, image, self.track_on, False, DISPLAYSURF)
		
		# The maximum length of the input.
		self.max_input_length = max_input_length
		
		# The color of the text.
		self.text_color = text_color
		
		# The font of the input text.
		self.font = pygame.font.SysFont(font , font_size)
		
		# The size of the output.
		self.font_size = font_size

		# The requested input.
		self.request = request
		
		# How many characters in one line.
		self.line_capacity = line_capacity
		
		# How many lines does the text box contains.
		self.lines = lines
		
		# The current input.
		self.text = ''
		
		# If the text was entered- True.
		self.enter = False
		
	def print_box(self):
		"""
			The function prints the input box according to its current data, if it's empty prints the request.
		"""
		
		lines = self.lines
		
		coordination = list(self.coordinates)
		
		while lines > 1:
			
			# Draw the box.
			DISPLAYSURF.blit(self.image, coordination)
			
			coordination[1] += self.image.get_rect().height
		
		DISPLAYSURF.blit(self.image, coordination)
		
		# If There is no input- print the request.
		if self.text == '':
			
			output = self.request
		
		else:
			
			output = self.text
		
		coordination = list(self.coordinates)
		
		coordination[0] += 8
		coordination[1] += 3
			
		# If the output is longer than one line.
		while len(output) > self.line_capacity:
			
			text = self.font.render(output[0 : self.line_capacity], 1, self.text_color)
			
			DISPLAYSURF.blit(text, coordination)
			
			output = output[self.line_capacity :]
			
			coordination[1] += self.image.get_rect().height
		
		text = self.font.render(output, True, self.text_color)

		# Print the last line.
		DISPLAYSURF.blit(text, coordination)
		
	def add_char(self, char):
		"""
			The function adds a char to the text of the box, if backspace entered deletes the last character if exist.
		"""
		
		if self.active:
		
			# Check if there is space for another character
			if len(self.text) < self.max_input_length:
				
				#Check if shift is pressed.
				if pygame.key.get_mods() & KMOD_SHIFT:
					
					if char == '9':
						
						self.text += '('
					
					elif char == '0':
						
						self.text += ')'
						
					elif char == '=':
						
						self.text += '+'
					
					elif char == '8':
						
						self.text += '*'
				
				# Its a simple character.
				elif len(char) == 1:

					self.text += char
				
				# char is not a letter/number/symbol.
				else:
					
					if char == "space":
						self.text += ' '
					elif char == "return":
						self.enter = True
					
			if char == "backspace":
						
				if len(self.text) > 0:
		
					self.text = self.text[:-1]
			
			if char == "return":
				
				self.enter = True
			
	def track_on(self):
		"""
			The function sets current_text_box to this text box and updates enter to False.
		"""
		
		global current_text_box
		
		current_text_box = self
		
		self.image_name = "Selected"

		self.image = pygame.image.load("Selected.png")
		
		# The player wants to enter text.
		self.enter = False
		
	def release_track(self):
		"""
			The function changes the image of the text box.
		"""
		
		self.image_name = "Text Box1"

		self.image = pygame.image.load("Text Box1.png")
		
		
class Elaborate_Input_box(Input_Box):
	"""
		The class extends from Input_Box and allows few more features.
	"""
	
	def __init__(self, coordination, image, max_input_length, text_color, font, font_size, line_capacity, lines, request, interrupt_image, accept_button_image, second_text_color):
		
		super(Elaborate_Input_box, self).__init__(coordination, image, max_input_length, text_color, font, font_size, line_capacity, lines, request)
		
		# If true the text in the box was interrupted and unchangeable any more.
		self.interrupt = False
		
		# The image of the interrupt sign.
		self.interrupt_image = pygame.image.load(interrupt_image)
		
		# The second text box text.
		self.second_text = ""
		
		# A button, if the user press on it the second text box text disappears, replaced with the first text box text and interrupt becomes True.
		self.accept_button = Button((coordination[0] + self.image.get_rect().width, coordination[1] + self.image.get_rect().height), accept_button_image, self.accept_second_text, True, DISPLAYSURF)  
		
		# The color of the text on the second text box.
		self.second_text_color = second_text_color
		
		# If true the input was entered and has to be sent to the server.
		self.send = False
		
		# If true, the text box data is interrupted, ready to be sent to the server.
		self.accept = False
		
	def print_elaborate(self):
		"""
			The function prints the second text box.
		"""
		
		if self.active:
		
			global buttons_to_push
			
			lines = self.lines
			
			coordination = list(self.coordinates)
			
			coordination = [coordination[0], coordination[1] + self.image.get_rect().height * self.lines]
			
			while lines > 1:
				
				# Draw the box.
				DISPLAYSURF.blit(self.image, coordination)
				
				coordination[1] += self.image.get_rect().height
			
			DISPLAYSURF.blit(self.image, coordination)
			
			coordination = list(self.coordinates)
			
			coordination = [coordination[0]  + 8, coordination[1] + self.image.get_rect().height * self.lines + 3]
			
			output = self.second_text
			
			# If the output is longer than one line.
			while len(output) > self.line_capacity:
				
				text = self.font.render(output[0 : self.line_capacity], 1, self.second_text_color)
				
				DISPLAYSURF.blit(text, coordination)
				
				output = output[self.line_capacity :]
				
				coordination[1] += self.image.get_rect().height
			
			text = self.font.render(output, True, self.second_text_color)

			# Print the last line.
			DISPLAYSURF.blit(text, coordination)
			
			if self.second_text != '' and self.accept_button not in current_buttons and not self.interrupt:
				
				buttons_to_push.append(self.accept_button)
				
				push_buttons()
			
			if self.interrupt:
				
				coordination = list(self.coordinates)

				DISPLAYSURF.blit(self.interrupt_image, (coordination[0] + self.image.get_rect().width - self.interrupt_image.get_rect().width, coordination[1]))
			
			# If the user pressed enter set send to True and enter to False.
			elif self.enter and not self.send:
				
				self.send = True
				
				self.enter = False
			
			if self.second_text != '':
				
				self.accept_button.set_button()
	
	def accept_second_text(self):
		"""
			The function cuts the second text box text and places it in the first one, then sets the interrupt.
		"""

		self.text = self.second_text
		
		self.set_interrupt()
		
		self.accept = True
		
	def set_interrupt(self):
		"""
			The function sets the text box to be interrupted.
		"""
		
		self.second_text = ""
		
		self.interrupt = True
		
		self.enter = False
		
		if not input_instructions_page:
			
			DISPLAYSURF.blit(pygame.image.load("Create Game.png"), (0, 0))
			
			DISPLAYSURF.blit(pygame.image.load("Input Instructions button.png"), (0, 714))
		
			set_name(opponent_name)
		
	def elaborate_add_char(self, char):
		"""
			The function adds char only if not interrupted.
		"""
		
		if self.active:
		
			if not self.interrupt:
				
				self.add_char(char)
		
		
class Input_Wire(object):
	"""
		The instance of the class is some Elaborate_Input_boxs.
	"""
	
	def __init__(self, text_boxes, error_font = "Ravie"):
		
		# A list of all the text_boxes.
		self.text_boxes = text_boxes
		
		# If true all the text boxes are interrupted.
		self.completed = False
		
		self.error_font = error_font
		
		# If the input is not valid prints the error message.
		self.error_message = ""
		
		# If true, the functions that maintains the current wire input won't be active.
		self.active = True
	
	def set_Input_Wire(self):
		"""
			The function pushes all the text boxes to push_buttons and prints it.
		"""
		
		global buttons_to_push
		
		buttons_to_push += self.text_boxes.values()
		
		push_buttons()
		
		self.print_wire()
		
	def set_activation(self, bool):
		"""
			The function receives a boolean and sets the active attribute of all the text boxes to the boolean value.
		"""
		
		global current_buttons
		
		self.active = bool
		
		for button in current_buttons:
			
			if isinstance(Elaborate_Input_box, Button):
				
				button.active == bool

	def print_wire(self):
		"""
			The function prints the input wire.
		"""
		
		if self.active:
		
			for text_box in self.text_boxes.values():
				
				text_box.print_box()
				text_box.print_elaborate()

			# If error message exists, prints it.
			if self.error_message != "":
				
				text = pygame.font.SysFont(self.error_font, 30).render(self.error_message, True, (255, 0, 0))
				
				DISPLAYSURF.blit(text, (800, 800))
			
	def is_completed(self):
		"""
			The function checks if all the elaborated text boxes interrupted, if true returns True and destroys the wire. Else returns False.
		"""
		
		for text_box in self.text_boxes.values():
		
			if not text_box.interrupt:
			
				self.completed = False
				
				return False
				
		return True
		
	def send_data(self, socket, id):
		"""
			The function iterates over all the boxes and send to the server the data of a box if its send attribute is True. 
		"""
		
		# Send the new data the player has entered.
		for text_box in self.text_boxes:
			
			# Send the new interrupted data.
			if self.text_boxes[text_box].accept:
				
				try:
				
					socket.send("new_message:" + id + "game_property:" + "accept:" + text_box.replace(' ', '_') + ':' + self.text_boxes[text_box].text)
					self.text_boxes[text_box].accept = False
					
				except:
					pass
			
			# Send the new entered data.
			elif self.text_boxes[text_box].send:

				try:
					
					socket.send("new_message:" + id + "game_property:" + text_box.replace(' ', '_') + ':' + self.text_boxes[text_box].text)
					
					self.text_boxes[text_box].send = False
					
				except:
					pass
	
	def new_chance(self, error_data):
		"""
			The function cancels the interrupts and prints the error message.
		"""
		
		# Updates the error message.
		self.error_message = error_data

		# Set all the interrupted text boxes to False and clear their data.  
		for text_box in self.text_boxes:
			
			self.text_boxes[text_box].interrupt = False
			
			self.text_boxes[text_box].text = ""
			
			self.text_boxes[text_box].second_text = ""
			

class Gif_Image(object):
	"""
		The class represents a gif image.
	"""
	
	def __init__(self, gif_name, location, loops = 0):
		
		# The name of the gif file.
		self.name = gif_name
		
		# The directory attribute contains path to the folder that contains all frames.
		self.directory = Gif_Image.new_folder(gif_name)
		
		# Contains all the frames of the gif.
		self.frames_list = self.ProcessImage()
		
		# The index for the current frame in frames_list.
		self.current_frame_index = 0
		
		# The location of the gif on the screen.
		self.location = location
		
		# If true the gif is active.
		self.active = True
		
		# How many loops the gif is going to do. If 0- forever.
		self.loops = loops
		
		# The current loop of the gif.
		self.current_loop = 0
		
		# If True, the gif has finished.
		self.dead = False
		
	@staticmethod
	def new_folder(gif_name):
		"""
			The function creates new folder in the default path that will contain all the frames of the gif.
		"""
		
		# The path of the new folder.
		directory = os.path.dirname(os.path.realpath(__file__)) + '/' + gif_name.replace('.gif', '')
		
		# Make sure that the directory does not exist yet.
		if not os.path.exists(directory):
		
			# Creating new directory.
			os.makedirs(directory)
		
		# Returning path to directory.
		return directory
		
	def ProcessImage(self):
		"""
			The process receives a gif file and saves the gifs frames to a directory.
		"""
		
		# Creating frames list.
		frames_list = []
		
		try:
		
			# Open image using Image module, in order to be able to use Image functions on this image.
			gif_image = Image.open(self.name)
		
		# If image is not loadable.
		except IOError:
			
			# For debugging.
			print "Cant load", self.name
			
			# Exit.
			sys.exit(1)
			
		# Frame number index.
		i = 0
		
		# Saving images pallet.
		mypalette = gif_image.getpalette()

		try:
		
			while True:
			
				# Attaching gifs pallet to each gif frame.
				gif_image.putpalette(mypalette)
				
				# Creating new Image file to each frame.
				new_frame = Image.new("RGBA", gif_image.size)
				
				# Pasting the frame to the new image.
				new_frame.paste(gif_image)
				
				if not os.path.isfile(self.directory + '/' + self.name.replace(".gif", '') + str(i) + '.png'):
					
					# Saving the frame.
					new_frame.save(self.directory + '/' + self.name.replace(".gif", '') + str(i) + '.png')
					
				# Appending frame to frames list.
				frames_list.append(pygame.image.load(self.directory + '/' + self.name.replace(".gif", '') + str(i) + '.png'))
				
				# Increasing frame index.
				i += 1
				
				# Proceeding to the next frame.
				gif_image.seek(gif_image.tell() + 1)
		
		# Exceptions occur when frames end.
		except EOFError:
		
			# Finishing loop and returning the list containing frames name.
			pass 
		
		return frames_list
	
	def next_frame(self):
		"""
			The function displays the next gif frame.
		"""
		
		# Move to the next frame only if the gif is active.
		if self.active and not self.dead:
		
			# Printing frame.
			DISPLAYSURF.blit(self.frames_list[self.current_frame_index], self.location)
			
			# Check if reached last frame.
			if self.current_frame_index > len(self.frames_list) - 2:
			
				# Resetting index to first frame.
				self.current_frame_index = 0
				
				self.current_loop += 1
				
				if self.current_loop == self.loops:
					
					self.dead = True
				
			else:
				
				# Increasing index.
				self.current_frame_index += 1
	
	def switch_gif_mode(self):
		"""
			The function changes the current gif activation status.
		"""
		
		self.active = not self.active
		

class Gifs_list(object):
	"""
		The class creates a gif data-base.
	"""
	
	def __init__(self, current_background, gifs = []):
		
		# A list of all the current gifs.
		self.gifs_list = gifs
		
		# The current background of the screen.
		self.background = current_background
		
		
	def next_frames(self):
		"""
			The function displays each gif its next frame.
		"""
		
		try:
			
			DISPLAYSURF.blit(pygame.image.load(self.background), (0, 0))
		
		# There is no background image.
		except:
			pass
		
		# Iterate over all the gifs and call to next_frame.
		for gif in range(len(self.gifs_list)):
			
			if self.gifs_list[gif].active:
				
				self.gifs_list[gif].next_frame()
		
		# Iterate over all the gifs and removes the dead.
		self.gifs_list = [gif for gif in self.gifs_list if not gif.dead]


class Bullet(object):
	"""
		The class represents a basic bullet, without any special abilities.
	"""
	
	def __init__(self, image, destination, coordination, speed, damage, die, parent):
		
		# The image of the Bullet.
		self.image = pygame.image.load(image)
		
		# The gif of the bullet.
		self.gif_image = Gif_Image(image, coordination)
		
		# The target location of the bullet.
		self.destination = destination
		
		# The current coordination of the bullet.
		self.coordination = coordination
		
		# The damage of the bullet.
		self.damage = damage
		
		# If true, the bullet hits and die.. no more than one hit.
		self.die = die
		
		# The tower that shot this bullet.
		self.parent = parent
		
		# How many pixels left on the horizontal axis in order to reach the destination.
		self.x_to_go = destination[0] - coordination[0]
		
		# How many pixels left on the vertical axis in order to reach the destination.
		self.y_to_go = destination[1] - coordination[1]
		
		# How many pixels to move on the horizontal axis every frame.
		self.x_speed = speed
		
		# How many pixels to move on the vertical axis every frame (the bullet might has no path- the tower is very close to the path).
		try:
			self.y_speed = abs((self.y_to_go / self.x_to_go) * speed)
		except:
			self.y_speed = 0

	def next_step(self):
		"""
			The function takes the bullet one step forward in its path. If it's out of the screen returns False, else returns True.
		"""
		
		if self.x_to_go < 0:
			
			self.coordination[0] -= self.x_speed
			
		else:
			
			self.coordination[0] += self.x_speed
			
		if self.y_to_go < 0:
			
			self.coordination[1] -= self.y_speed
			
		else:
			
			self.coordination[1] += self.y_speed
		
		# The bullet is out of the screen.
		if self.coordination[0] + self.image.get_rect().width < 0 or self.coordination[0] + self.image.get_rect().width > 1050 or self.coordination[1] < 0 or self.coordination[1] > 864:
			
			return False
		
		else:
			
			return True
	
	def Check_for_hit(self):
		"""
			The function iterates over the soldiers list and checks if the bullet is currently on a soldier. If it does, reduce the soldiers life according to the bullet damage.
		"""
		
		global current_bullets
		
		for soldier in game.current_soldiers:
			
			# If true, it's a hit!
			if self.coordination[0] > soldier.coordination[0] and self.coordination[0] < soldier.coordination[0] + soldier.image.get_rect().width and self.coordination[1] > soldier.coordination[1] and self.coordination[1] < soldier.coordination[1] + soldier.image.get_rect().height: 
		
				self.hit(soldier)
				
				# If the bullet is disposable, remove it from the active bullets list.
				if self.die:
					
					# The bullet might hit more than one soldier once.
					try:
						game.current_bullets.remove(self)
					
					except:
						continue
						
	def hit(self, soldier):
		"""
			The function receives a soldier and hits him.
		"""
		
		soldier.health -= self.damage
		
		soldier.look_for_pulse()
	

class Bomb(Bullet):
	"""
		The instance of the class is a bullet with range, when it hits someone it explodes.
	"""
	
	def __init__(self, image, destination, coordination, speed, damage, die, parent, range, explosion_gif):
		
		super(Bomb, self).__init__(image, destination, coordination, speed, damage, die, parent)
		
		# The range of the bomb.
		self.range = range
		
		# The gif of the explosion.
		self.explosion_gif = explosion_gif
	
	def hit(self, soldier):
		"""
			The function overrides the hit function of bullet. The function looks for more soldiers in the bomb range and hits them too.
		"""
		
		global my_gifs
		
		my_gifs.gifs_list.append(Gif_Image(self.explosion_gif, self.coordination, 1))
		
		soldier.health -= self.damage
		
		soldier.look_for_pulse()
		
		for soldier in Tower.soldiers_in_range(soldier.coordination, self.range):
			
			soldier.health -= self.damage + int(round(self.damage / 1.5))
		
			soldier.look_for_pulse()
			

class Ghost(Bullet):
	"""
		The instance of the class is a bullet that also takes the soldier few steps backwards.
	"""
	
	def __init__(self, image, destination, coordination, speed, damage, die, parent, backwards):
		
		super(Ghost, self).__init__(image, destination, coordination, speed, damage, die, parent)
		
		# How many steps the bullets takes the hit soldier backwards.
		self.backwards = backwards
		
	def hit(self, soldier):
		"""
			The function overrides the hit function of bullet. The function takes the hit soldier few steps backward according to the attribute of the current instance.
		"""
		
		global frightened_soldiers
		
		soldier.health -= self.damage
		
		soldier.look_for_pulse()
		
		frightened_soldiers[soldier] = self.backwards
	
	
class TowerIcon(Button):
	"""
		The class extends from Button and adds it few more attributes and methods that fit the tower icon.
	"""
	
	def __init__(self, coordinates, image, DISPLAYSURF, tower_representation, data, data_coordinates, description, function, price, die = False):
		
		super(TowerIcon, self).__init__(coordinates, image, function, die, DISPLAYSURF)
		
		# What tower this tower_icon represents.
		self.tower_representation = tower_representation
		
		# A string that contains all the data about the Tower: its price, its attack power and range.
		self.data = data
		
		# Where the data is going to be displayed.
		self.data_coordinates = data_coordinates
		
		# A description about the tower.
		self.description = description
		
		# The price of the tower- how much does it cost in order to place it on the screen.
		self.price = price
		
	def press(self):
		"""
			Asks from the server for a confirmation that the player has enough money in order to buy this tower.
		"""
		
		global messages_for_the_server
		
		messages_for_the_server.append("Game:new_tower_request:" + self.tower_representation)
		
	def accepted(self):
		"""
			Tries to place the tower.
		"""
		
		tower_icon_press(self.image, self.image_name)
		
		mouse_tower = self
		
	def mouse_over(self):
		"""
			The function displays the data of the Icon according to the data coordinate.
		"""
	
		# Draw the text box.
		rect = pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), (self.data_coordinates[0], self.data_coordinates[1], 370, 100), 5)
		# Fill the text box
		rect = pygame.draw.rect(self.DISPLAYSURF, (0, 255, 255), (self.data_coordinates[0] + 3, self.data_coordinates[1] + 3, 364, 94), 0)
		
		# Write the data.
		self.DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 14).render(self.data, True, (255, 0, 0)), (self.data_coordinates[0] + 10, self.data_coordinates[1] + 5))
		
		# Write the description.
		for line in range(len(self.description)):
		
			self.DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 10).render(self.description[line], True, (0, 100, 100)), (self.data_coordinates[0] + 10, self.data_coordinates[1] + 5 + (line+1) * 20))

	def is_over(self):
		"""
			The function returns True if the mouse is currently over the icon, else returns False.
		"""
		
		mouse_pos = pygame.mouse.get_pos()
		
		# The icon mightn't have setted yet, so its image attribute isn't loaded and has no get_rect method.
		try:

			return self.coordinates[0] - 1 < mouse_pos[0] and self.image.get_rect().topright[0] + self.coordinates[0] + 1 > mouse_pos[0] and self.image.get_rect().topleft[1] + self.coordinates[1] - 1 < mouse_pos[1] and self.image.get_rect().bottomleft[1] + self.coordinates[1] + 1 > mouse_pos[1]   
			
		except:
			return False
			
			
class SoldierIcon(TowerIcon):
	"""
		The class extends from TowerIcon and overiding few methods to fit the soldier icon.
	"""
	
	def __init__(self, coordinates, image, DISPLAYSURF, tower_representation, data, data_coordinates, description, function, price, die = False):
	
		super(SoldierIcon, self).__init__(coordinates, image, DISPLAYSURF, tower_representation, data, data_coordinates, description, function, price, die = False)
		
		self.image = pygame.transform.scale(self.image, (65, 65))
		
	def press(self):
		"""
			Asks from the server for a confirmation that the player has enough money in order to buy this Soldier.
		"""
		
		global messages_for_the_server
		
		messages_for_the_server.append("Game:new_soldier_request:" + self.tower_representation)
		
	def accepted(self):
		"""
			Nothing has to be done. Just overiding.
		"""
		
		pass
		

class Tower(object):
	"""
		The class represents a basic tower.
	"""
	
	def __init__(self, coordination, image, attack_power, range, reloading, bullet, bullet_type, strategy, bullet_speed, icon):
		
		# The coordination of the tower on the map.
		self.coordination = coordination
		
		# The tower image.
		self.image = pygame.image.load(image)
		
		# The damage of the bullet.
		self.attack_power = attack_power
		
		# The radius of the tower- how far can it shoot.
		self.range = range
		
		# How much time does it take to the tower to reload its ammo (frame per second).
		self.reloading = reloading
		
		# How many frames does the tower has to wait till the next bullet have reloaded.
		self.reloading_status = 0
		
		# The bullet image (string) the tower is using.
		self.bullet = bullet
		
		# The type of the bullet and its attributes (if not regular).
		self.bullet_type = bullet_type
		
		# A list of the active bullets of the tower. 
		self.current_bullets = []
		
		# The rotation angel of the tower.
		self.rotation = 0
		
		# If true the image is pointing to the right, else to the left.
		self.right_perspective = False
		
		# Contains the current strategy of the tower.
		self.strategy = strategy
		
		# Contains the soldier that currently on target.
		self.target = None
		
		# The speed of the bullet in pixels per frame.
		self.bullet_speed = bullet_speed
		
		# The icon that the tower is being bought by, this is a tower button. Static variable.
		icon = icon
		
		# Set the tower.
		game.set_tower.append(self)
		
	def set_target(self):
		"""
			The function checks what's the current target of the tower according to its strategy and updates it.
		"""
		in_range = Tower.soldiers_in_range(self.coordination, self.range)
		
		if self.strategy == "farthest":
			
			if len(in_range) > 0:
				
				# Contains the x pixel of the farthest soldier
				farthest = in_range[0].current_x_pixel
				index = 0
				
				if len(in_range) > 1:
				
					for i in range(1, len(in_range)):
				
						if in_range[i].current_x_pixel > farthest:
							
							farthest = in_range[i].current_x_pixel
							
							index = i
							
				# Set the target to the farthest soldier.
				self.target = in_range[index]
			
			# There are no soldiers in the range of the tower.
			else:
				
				self.target = None
	
	@staticmethod
	def soldiers_in_range(coordination, range):
		"""
			The function iterates over all the active soldiers and returns a list of all the soldiers that are in the tower range.
		"""
		
		in_range = []
		
		for soldier in game.current_soldiers:
			
			distance = math.sqrt((coordination[0] - soldier.current_x_pixel)**2 + (coordination[1] - soldier.current_y_position)**2)
			
			if distance < range:
				
				in_range.append(soldier)
		
		return in_range
		
	def aim(self):
		"""
			The function rotates the tower to the current target.
		"""	
		
		# The target might be dead already.
		try:
		
			#The center of the target coordination.
			target_coordination = [self.target.coordination[0] + self.target.image.get_rect().width / 2, self.target.coordination[1] + self.image.get_rect().height / 2]
			
			# Horizontal distance.
			x = self.coordination[0] - target_coordination[0]
			
			# Check if the target is on the upper side of the tower.
			if target_coordination[1] < self.coordination[1]:
				
				# Vertical distance.
				y = self.coordination[1] - target_coordination[1]
				
				self.rotation = math.degrees(- math.acos(x / math.sqrt(x**2 + y**2)))
				
			# The target is on the lower side of the tower or on the center.
			else:
			
				# Vertical distance.
				y = target_coordination[1] - self.coordination[1]
				
				self.rotation = math.degrees(math.acos(x / math.sqrt(x**2 + y**2)))
				
			# Check if the target is on the left side of the tower.
			if target_coordination[0] < self.coordination[0]:
				
				self.right_perspective = False
				
			# The target is on the right side of the tower or on the center.
			else:
				
				self.right_perspective = True
				self.rotation *= -1
				
		except:
			pass
			
	def fire(self):
		"""
			If there's a target, shoot it.
		"""
		
		# The target might be dead already.
		try:
		
			# If the tower finished to reload new ammo, fire!
			if self.reloading_status < 1:
			
				if self.target != None:
					
					r = self.image.get_rect().height / 2
					
					a = pygame.image.load(self.bullet).get_rect().height

					if not self.right_perspective:
					
						if self.rotation > 0:
							
							# Match the tower rotation to the current situation rotation requirements.
							rotation = math.radians(self.rotation)

							bullet_coordination = [round(self.coordination[0] + r - r * math.cos(rotation) - a), round(self.coordination[1] + r + r * math.sin(rotation))]
							
						else:
							
							rotation = - math.radians(self.rotation)
							bullet_coordination = [round(self.coordination[0] + r - r * math.cos(rotation) - a), round(self.coordination[1] + r - r * math.sin(rotation) - a)]
					
					else:
					
						if self.rotation > 90:
							
							rotation = math.radians(180 - self.rotation)

							bullet_coordination = [round(self.coordination[0] + r - r * math.cos(math.radians(self.rotation))), round(self.coordination[1] + r - r * math.sin(math.radians(self.rotation)) -a)]
							
						else:
							
							rotation = math.radians(180 + self.rotation)
							bullet_coordination = [round(self.coordination[0] + r + r * math.cos(rotation)), round(self.coordination[1] + r + r * math.sin(rotation))]
					
					#The center of the target coordination.
					target_coordination = [self.target.coordination[0] + self.target.image.get_rect().width / 2, self.target.coordination[1] + self.image.get_rect().height / 2]
					
					if self.bullet_type[0] == "regular":
						
						game.current_bullets.append(Bullet(self.bullet, [target_coordination[0], target_coordination[1]], bullet_coordination, self.bullet_speed, self.attack_power, True, self))
					
					elif self.bullet_type[0] == "bomber":
						
						game.current_bullets.append(Bomb(self.bullet, [target_coordination[0], target_coordination[1]], bullet_coordination, self.bullet_speed, self.attack_power, True, self, self.bullet_type[1], self.bullet_type[2]))
						
					elif self.bullet_type[0] == "witch":
					
						game.current_bullets.append(Ghost(self.bullet, [target_coordination[0], target_coordination[1]], bullet_coordination, self.bullet_speed, self.attack_power, True, self, self.bullet_type[1]))
					
					# Start reloading new ammo.
					self.reloading_status = self.reloading
					
			# Keep reloading.		
			else:
				
				self.reloading_status -= 1
		
		except:
			pass
	
	def print_tower(self):
		"""
			The function prints the tower according to its rotation and right_perspective value.
		"""
		
		if not self.right_perspective:
			
			DISPLAYSURF.blit(rotate_image(self.image, self.rotation), self.coordination)
		
		else:
			
			DISPLAYSURF.blit(pygame.transform.flip(rotate_image(self.image, self.rotation), False, True), self.coordination)
			
			
class Soldier(object):
	"""
		The instance of the class is a soldier.
	"""
	
	def __init__(self, image, rank, game_function, proportion, current_x_pixel, current_x_position, x_0_coordinate, destination, speed, step_length, health, attack, dying_sound, eat_sound, reward):
		
		self.name = image[: -4]
		
		self.image = pygame.image.load(image)
		
		self.image_to_rotate = pygame.image.load(image)
		
		self.rank = rank
		
		self.game_function = game_function
		
		self.proportion = proportion
		
		self.destination = destination
		
		# The beginning x coordinate of the game function.
		self.x_0_coordinate = x_0_coordinate
		
		# current_x_position is necessary to find the current_y_position, this is the current_x_position in the function itself but not on the screen. 
		self.current_y_position, self.current_x_position = find_y_position(current_x_position, destination, step_length, game_function, proportion)
		
		# The current x coordinate of the soldier on the screen.
		self.current_x_pixel = current_x_pixel
		
		# The center of the soldier (going to be updated in the first move of the soldier).
		self.coordination = []

		DISPLAYSURF.blit(self.image, (self.current_x_pixel, self.current_y_position))
		
		# every unit is FPS pixels for second.
		self.speed = speed
		
		# The distance between every x coordinate in the function.
		self.step_length = step_length
		
		# The health of the soldier.
		self.health = health
		
		# The attack power of the soldier.
		self.attack = attack
		
		# The sound of the soldier when it's dying.
		self.dying_sound = pygame.mixer.Sound(dying_sound)
		
		# The amount of money the player receives when he kills this soldier.
		self.reward = reward
		
		# The sound the soldiers does when he finishes the path.
		self.eat_sound = pygame.mixer.Sound(eat_sound)

	def next_step(self):
		"""
			Moves the soldier to his next position.
		"""
		
		global frightened_soldiers
		
		if self not in frightened_soldiers:

			# Step forward the soldier in purpose to the screen.
			self.current_x_pixel += self.speed
			
			# Step forward the soldier in purpose to the function. 
			self.current_x_position = self.x_0_coordinate + int(round(self.current_x_pixel)) * self.step_length

			self.current_y_position, self.current_x_position = find_y_position(self.current_x_position, self.destination, self.step_length, self.game_function, self.proportion)
			
			# If true, the soldier arrived to his destination.
			if self.current_y_position == 9999:
				
				self.winner()
		
		else:
			
			# Step backward the soldier in purpose to the screen.
			if self.current_x_pixel > 5:
				
				self.current_x_pixel -= 15
			
			else:
				
				self.current_x_pixel = 0
				
			frightened_soldiers[self] -= 1
			
			if frightened_soldiers[self] <= 0:
				
				del frightened_soldiers[self]
			
			# Step forward the soldier in purpose to the function. 
			self.current_x_position = self.x_0_coordinate + int(round(self.current_x_pixel)) * self.step_length

			self.current_y_position, self.current_x_position = find_y_position(self.current_x_position, self.destination, self.step_length, self.game_function, self.proportion)

		# Print the soldier in his new position.
		image_half_length = (int(round(0.5*(self.image.get_rect().topright[0] - self.image.get_rect().topleft[0]))), int(round(0.5*(self.image.get_rect().bottomleft[1] - self.image.get_rect().topleft[1]))))
		self.coordination = [self.current_x_pixel - 0.5*image_half_length[0], self.current_y_position - 0.5*image_half_length[1]]
		DISPLAYSURF.blit(rotate_image(self.image, get_angel(self.game_function, self.current_x_position, self.step_length, self.proportion)), (self.coordination[0], self.coordination[1]))

		
	def winner(self):
		"""
			The soldier finished the path- reduce the goal health and erase the soldier. 
		"""
		global game
		
		# Remove the current soldier from the list that contains all the soldiers on the screen.
		game.current_soldiers.remove(self)

		# Play the soldiers eating sound.
		self.eat_sound.play()
		
		# Alert the server that this soldier finished the path.
		messages_for_the_server.append("Game:dec_hp:" + self.rank)
	
	def look_for_pulse(self):
		"""
			The function checks if the soldiers health is above 0. If not, removes him from the current_soldiers_list and sends the server the reward.
		"""
		
		global messages_for_the_server
		global current_SpaceShip_x_pixel
		
		if self.health <= 0:
		
			if self.name == "PrivateSpaceShip":
				
				current_SpaceShip_x_pixel = self.current_x_pixel
				
				soldiers = ["Corporal", "Sergeant"]
				
				for i in range(5):
				
					game.soldiers_to_send.append([choice(soldiers), 0, self.current_x_position, self.current_y_position])
			
			game.current_soldiers.remove(self)
			
			game.dying_soldiers[self] = 0
			
			messages_for_the_server.append("Game:money_reward:" + str(self.reward))
			
			

class Game(object):
	"""
		The instance of this class is responsible on everything that connects to the game.
	"""
	
	def __init__(self, game_function, x_0_coordinate, x_f_coordinate, soldiers_to_send, hp):
		
		# The path of the enemy is being built via the game function and its area.
		self.game_function = game_function
		self.x_0_coordinate = x_0_coordinate
		self.x_f_coordinate = x_f_coordinate
		self.step = (x_f_coordinate - x_0_coordinate) / 1050
		self.y_max = Game.highest_y_coor(game_function, x_0_coordinate, x_f_coordinate, self.step)
		
		# Get the proportion between the highest y coordinate in abstract and the number of the y pixels between the half of the vertical screen to its vertical edge.  
		try:
			self.proportion = 402 / self.y_max
		except:
			self.proportion = 0
		
		# A list that contains lists of soldiers names (string) and their time-to-send: when to send the current soldier.
		self.soldiers_to_send = soldiers_to_send
		
		# Contains all the soldiers that are currently on the screen.
		self.current_soldiers = []
		
		# Contains all the towers that are currently on the screen.
		self.current_towers = []
		
		# Contains all the active bullets.
		self.current_bullets = []
		
		# Contains all the currently dying soldiers.
		self.dying_soldiers = {}
		
		# Contains the towers that have to get printed.
		self.set_tower = []
		
		# If true, updating the scene.
		self.update_scene = False
		
		# The hp of the player.
		self.hp = hp
		
		# Load the image of each pixel on the path.
		self.way = pygame.image.load("way.png")
		
		# If True, the server was alerted that the round has finished.
		self.round_ended = False
		
		# The current round
		self.round = 0
		
		# A list of all the new events that have occurred and the player has to know about.
		self.new_events = []
		
		# How much time left to display the new round title.
		self.new_round_title_time = 0
		
		# The image of the round title and its coordinates.
		self.round_title = [pygame.image.load("round.png"), [400, 350]]
		
		# The current amount of money of the player.
		self.money = 450
	
	@staticmethod
	def highest_y_coor(game_function, x_0_coordinate, x_f_coordinate, step):
		"""
			The function receives a function and returns its abstract highest y coordinate.
		"""
		
		x = start_from = x_0_coordinate
		
		# Eval is evil, catch the exception if exist.
		try:
			max = abs(eval(game_function))
		except:
			while True:
				x += step
				try:
					max = abs(eval(game_function))
					break
				except KeyboardInterrupt:
						raise
				except:
					if x < x_f_coordinate:
						continue
		
		start_from = x
					
		for x in numpy.arange(start_from, x_f_coordinate, step):
		
			try:
				y_coor = abs(eval(game_function))
			except:
				while True:
					x += step
					try:
						y_coor = abs(eval(game_function))
						break
					# Usually there is an keyboard interrupt which not raises an exception.
					except KeyboardInterrupt:
						raise
					except:
						if x < x_f_coordinate:
							continue
			
			if y_coor > max:
				max = y_coor
		
		return max
		
	def build_path(self):
		"""
			Draws the game function's graph, as the path, to the screen.
		"""
		
		global current_scene
		
		# count is going to represent the current x coordination of the function as the current x coordination on the screen, in pixels. 
		count = 0
		
		# Draw the path.
		for x in numpy.arange(self.x_0_coordinate, self.x_f_coordinate, self.step):
			
			# Calculate the y coordination of the current x coordination in the function and multiple it by the proportion to get the right pixel on the screen. 
			y = match_y(int(round(eval(self.game_function) * self.proportion)))

			# Move to the next pixel on the screen.
			count += 1
			
			DISPLAYSURF.blit(self.way, (count, y))
			
		# Update the current scene, the path has been added.
		update_scene()
		
	def set_new_towers(self):
		"""
			The function prints all the new towers. Then appends the new towers to the current towers list.
		"""

		for tower in self.set_tower:
		
			DISPLAYSURF.blit(tower.image, tower.coordination)
			
			if tower:
			
				self.current_towers.append(tower)
		
		if len(self.set_tower) > 0:	
			
			self.set_tower = []
			
	def tower_manager(self):
		"""
			This function is responsible on everything that connects to the towers behaviour- rotating and shooting.  
		"""
		
		# Iterate over all the active towers.
		for tower in self.current_towers:
			
			tower.set_target()
			
			if tower.target:
				
				tower.aim()
				
				tower.fire()
			
			tower.print_tower()
		
	def send_soldiers(self):
		"""
			The function updates the dictionary- decreases every soldier time-to-send by 1 and send those who their time-to-send is 0.
		"""
		
		global current_SpaceShip_x_pixel
		
		for current_soldier in range(len(self.soldiers_to_send)):

			self.soldiers_to_send[current_soldier][1] -= 1
			
			if self.soldiers_to_send[current_soldier][1] < 1:
				
				if self.soldiers_to_send[current_soldier][2] == 0 and self.soldiers_to_send[current_soldier][3] == 0:
				
					x_coord = self.x_0_coordinate
					x_pixel = 0
					
				else:
				
					x_coord = self.soldiers_to_send[current_soldier][2]
					x_pixel = current_SpaceShip_x_pixel
				
				self.current_soldiers.append(new_soldier(self.soldiers_to_send[current_soldier][0], self.game_function, self.proportion, x_coord, self.x_f_coordinate, x_pixel))
			
		# Remove the soldiers that already have sent.		
		self.soldiers_to_send = [soldier for soldier in self.soldiers_to_send if soldier[1] > 0]
		
	def look_for_hits(self):
		"""
			The function iterates over all the active bullets in the game and check if there is a hit.
		"""
		
		for bullet in game.current_bullets:
			
			# If there is a hit, reduce the soldier life and check if he's still alive, if not- kill him.
			bullet.Check_for_hit()

	def move_soldiers(self):
		"""
			The function moves all the soldiers on the path to their next position.
		"""
		
		# Iterate over all the soldiers that are on the path.
		for soldier in self.current_soldiers:
			
			soldier.next_step()
			
	def check_tower_data(self):
		"""
			The function checks if the mouse is over a tower icon, if it does prints the current tower data.
		"""
		
		global current_buttons
		
		# Iterate over all the buttons in the game.
		for button in current_buttons:
			
			# Check if its a tower icon and if the mouse is over it.
			if isinstance(button, TowerIcon) and button.is_over() or isinstance(button, SoldierIcon) and button.is_over():
				
				button.mouse_over()
				
				# The mouse can't be in two different places the same time.
				break
	
	def move_bullets(self):
		"""
			The function moves each active bullet one step forward.
		"""
		
		for bullet in self.current_bullets:
		
			# Move the bullet one step forward.
			if not bullet.next_step():
				
				# If the bullet is out of the screen, his shouldn't be active any more.
				self.current_bullets.remove(bullet)
			
			else:
				
				# Print the bullet in its new location.
				bullet.gif_image.location = bullet.coordination
				
				bullet.gif_image.next_frame()
	
	def current_dying_soldiers(self):
		"""
			The function is responsible on everything happens after the soldier is dead. 
		"""
		
		for soldier in self.dying_soldiers:
			
			# If true the soldier died this moment.
			if self.dying_soldiers[soldier] == 0:

				soldier.dying_sound.play()

				self.dying_soldiers[soldier] += 1
			
			if self.dying_soldiers[soldier] < 5:
				
				soldier.image = pygame.transform.rotozoom(soldier.image, 30, 0.5)
				
				DISPLAYSURF.blit(soldier.image, soldier.coordination)
				
				self.dying_soldiers[soldier] += 1
			
			if self.dying_soldiers[soldier] > 4:
				
				self.dying_soldiers[soldier] = '*'
		
		# Remove the R.I.P soldiers from the dying dictionary.

		remove = [soldier for soldier in self.dying_soldiers if self.dying_soldiers[soldier] == '*']
		
		for soldier in remove: del self.dying_soldiers[soldier]
		
	def update_status(self):
		"""
			The function updates the server about the new necessary things that have occurred.
		"""
		
		global messages_for_the_server
		
		if not self.soldiers_to_send and not self.current_soldiers and not self.round_ended:
			
			messages_for_the_server.append("Game:round_ended")
			
			self.round_ended = True
			
	def display_data(self):
		"""
			The function prints basic data as the current amount of money.
		"""
		
		# Print the current amount of money of the player.
		DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 14).render("Money: " + str(game.money), True, (255, 0, 0)), (1150, 700))
		
		# Print the current amount of hp of the player.
		DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 14).render("HP: " + str(game.hp), True, (255, 0, 0)), (1325, 700))
		
	def events(self):
		"""
			The function prints the client the title of the current round.
		"""
		
		# Iterate over the new events that have occurred.
		for event in self.new_events:
		
			if event == "new_round":
				
				self.new_round_title_time = 60
				
				self.new_events.remove(event)
				
		# Call all the events that are still active.
		
		self.new_round_alert()
		
	def new_round_alert(self):
		"""
			The function alerts the player that a new round is now beginning.
		"""
		
		if self.new_round_title_time > 0:
			
			self.new_round_title_time -= 1
			
			DISPLAYSURF.blit(self.round_title[0], (self.round_title[1][0], self.round_title[1][1]))
			
			DISPLAYSURF.blit(pygame.font.SysFont("Palatino Linotype Regular" , 150).render(str(self.round), True, (0, 0, 0)), (self.round_title[1][0] + self.round_title[0].get_rect().width + 30, self.round_title[1][1] + 30))
	
	def tower_confirmation(self, tower):
		"""
			The function receives a tower and buy it.
		"""
		
		for button in current_buttons:
			
			if isinstance(button, TowerIcon) and button.tower_representation == tower:
				
				button.accepted()
				
				break
				
	def soldier_confirmation(self, soldier):
		"""
			The function receives a soldier and buy it.
		"""
		
		for button in current_buttons:
			
			if isinstance(button, SoldierIcon) and button.tower_representation == soldier:
				
				button.accepted()
				
				break
	
	@staticmethod	
	def result(result):
		"""
			The game was ended. Alert the player if he won or lost the game.
		"""
		
		global current_buttons
		global game_started
		global connected
		global buttons_to_push
		global my_gifs
		
		game_started = False
		connected = False
		game_ended = True
		
		if result == "win":
			
			DISPLAYSURF.blit(pygame.image.load("victory.png"), (0, 0))
			
		else:
			
			DISPLAYSURF.blit(pygame.image.load("defeat.png"), (0, 0))
			
		buttons_to_push.append(Button((750, 700), "Main menu button.png", restart, True, DISPLAYSURF))
			
		push_buttons()
		

def tower_icon_press(image, image_string):
	"""
		The function replace the mouse cursor with the tower image.
	"""
	
	global tower_cursor
	global image_tower_cursor
	global image_tower_cursor_string

	pygame.mouse.set_visible(False)
	
	tower_cursor = True	

	DISPLAYSURF.blit(image, pygame.mouse.get_pos())
	
	image_tower_cursor_string = image_string
	
	image_tower_cursor = image
	

def server_crashed():
	"""
		The function set restart_game and prints that the game has crashed.
	"""
	
	global restart_game
	
	global game_crashed
	
	game_crashed = True
	
	try:
		
		# Tell the server you're out.
		my_socket.send("!@#$")
		
	except:
		
		pass
	
	restart_game = True
	

def get_angel(game_function, current_x_cordination, step_length, proportion):
	"""
		The function receives an image, the game function, current x position and returns its angel with the x axis.
	"""

	try:
	
		x = current_x_cordination - step_length
		y_1 = eval(game_function) * proportion
		x = current_x_cordination + step_length
		y_2 = eval(game_function) * proportion

		return 90 - (math.degrees(math.atan((y_2 - y_1) / - 2 )))
	
	except:
		
		return 0
		

def rotate_image(image, angle):
	"""
		The function Rotates an image while keeping its center and size.
	"""
    
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotozoom(image, angle, 1)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	
	return rot_image

	
def find_y_position(current_x_position, destination, step_length, game_function, proportion):
	"""
		A function might have a limit- when x value hasn't a y value. find the next x coordinate which has a y value. 
	"""
	
	count = 0
	x = current_x_position
	max_steps = (destination - current_x_position) / step_length

	while count < max_steps:
		
		try:
			
			return match_y(int(round(eval(game_function) * proportion))), current_x_position
			
		except:
		
			count += 1
			current_x_position += step_length
			x = current_x_position
	
	# The soldier have reached the goal.		
	return 9999, 0


def match_y(y):
	"""
		Receives a y coordination and match it to the current screen (in pygame (0,0) is the top left pixel).
	"""
	
	if y > 0 or y == 0:
				
		return abs(y - 402)
			
	return abs(y) + 402
	

def set_name(name):
	"""
		The function receives the name of the opponent and prints it to the screen.
	"""
	
	global opponent_name
	
	opponent_name = name
	
	DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 30).render("Your opponent: " + name, True, (0, 0, 0)), (45, 175))
	

def set_input_time(time):
	"""
		The function prints the received time.
	"""
	
	global game_input_time_bool
	
	if game_input_time_bool:
	
		DISPLAYSURF.blit(pygame.image.load("input_timer.png"), (946, 169))
		
		DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 38).render("Time left: " + time, True, (0, 0, 0)), (1050, 175))
	
	
def pygame_y(y):
	"""
		The opposite of match_y, returns the original y coordination as relates to the pygame screen. 
	"""
	
	if y > 0 or y == 0:
	
		return 402 - y

	return abs(y) + 402
	
	
def new_soldier(soldier_name, game_function, proportion, start_x_coordinate, x_f_coordinate, x_pixel):
	"""
		The function receives a soldier name and creates him. Then returns him.
	"""

	if soldier_name == "private":
		
		return Soldier("private.png", "private", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 2, game.step, 200, 1, "mouse die.wav", "mouse eat.wav", 10)
	
	elif soldier_name == "private2":
		
		return Soldier("private2.png", "private2", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 2, game.step, 400, 1, "mouse die.wav", "mouse eat.wav", 25)
		
	elif soldier_name == "Private first class":
	
		return Soldier("private_first_class.png", "private_first_class", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 7, game.step, 250, 1, "mouse die.wav", "mouse eat.wav", 40)

	elif soldier_name == "Specialist":
	
		return Soldier("Specialist.png", "Specialist", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 2, game.step, 2000, 2, "mouse die.wav", "mouse eat.wav", 100)
	
	elif soldier_name == "Corporal":
		
		return Soldier("Corporal.png", "Corporal", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 2, game.step, 10000, 2, "mouse die.wav", "mouse eat.wav", 150)
		
	elif soldier_name == "Sergeant":
		
		return Soldier("Sergeant.png", "Sergeant", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 2, game.step, 50000, 2, "mouse die.wav", "mouse eat.wav", 200)
		
	elif soldier_name == "PrivateSpaceShip":
		
		return Soldier("PrivateSpaceShip.png", "PrivateSpaceShip", game_function, proportion, x_pixel, start_x_coordinate, game.x_0_coordinate, x_f_coordinate, 1, game.step, 110000, 5, "mouse die.wav", "mouse eat.wav", 600)

		
def try_place_tower(mouse_coord):
	"""
		The function receives mouse coordination and returns False if the tower is above other tower, out of the bounds of the game or on the path. Else returns True.
	"""

	global image_tower_cursor
	global game
	global game_function

	# The radius of the way.
	way_radius = game.way.get_rect().width / 2
	
	# Calculate what are the first pixel of the path and the last one that should be scanned. 
	# posite_value(game.x_0_coordinate - first_pixel) - if the first pixel is out of the path range start from the first coordinate of the path.
	
	# The tower image is out of bounds.
	if mouse_coord[0] + image_tower_cursor.get_rect().width > 1050 + way_radius:
	
		return False
	
	# Don't check further then the end of the path.
	elif mouse_coord[0] + image_tower_cursor.get_rect().width > 1050 + way_radius:
	
		last_pixel = mouse_coord[0] + image_tower_cursor.get_rect().width + way_radius 
		last_pixel -= posite_value(last_pixel - 1050)
	
	else:
		
		# Check if there's already a tower in the current coordinates.
		if len(game.current_towers) > 0:
			
			for tower in game.current_towers:
				
				if mouse_coord[0] > tower.coordination[0] - 1 and mouse_coord[0] < tower.coordination[0] + tower.image.get_rect().width + 1:
					
					# Check the upper left pixel.
					if  mouse_coord[1] > tower.coordination[1] - 1 and mouse_coord[1] < tower.coordination[1] + tower.image.get_rect().height + 1:
						return False
					
					# Check the bottom left pixel.					
					if mouse_coord[1] + image_tower_cursor.get_rect().height > tower.coordination[1] -1 and mouse_coord[1] + image_tower_cursor.get_rect().height < tower.coordination[1] + tower.image.get_rect().height + 1:
						return False
						
				if mouse_coord[0] + image_tower_cursor.get_rect().width > tower.coordination[0] - 1 and mouse_coord[0] + image_tower_cursor.get_rect().width < tower.coordination[0] + tower.image.get_rect().width + 1:	
				
					# Check the upper right pixel.
					if  mouse_coord[1] > tower.coordination[1] - 1 and mouse_coord[1] < tower.coordination[1] + tower.image.get_rect().height + 1:
						return False
					
					# Check the bottom right pixel.					
					if mouse_coord[1] + image_tower_cursor.get_rect().height > tower.coordination[1] -1 and mouse_coord[1] + image_tower_cursor.get_rect().height < tower.coordination[1] + tower.image.get_rect().height + 1:
						return False
		
		last_pixel = mouse_coord[0] + image_tower_cursor.get_rect().width + way_radius 

		first_pixel = mouse_coord[0] - way_radius + posite_value(way_radius - mouse_coord[0])
		
		# Iterate over the relevant x pixels coordinates of the path. Check if there's a pixel of the image tower currently above a piece of the path.
		for x_pixel in range(first_pixel + 1, last_pixel):
			
			# x and x_funcoord are going to contain the x coordination in relative to the function.
			x = x_funcoord = x_pixel * game.step + game.x_0_coordinate
			
			# Contains the flags of every piece of the frame (up, down, left, right), if the flag is True checks it.
			flags = {'up' : True, 'down' : True, 'left' : True, 'right' : True}
			
			# The left / right horizontal distance is same for every left and right pixel on the edges of the frame- calculate them once.
			left_horizontal_distance = abs(mouse_coord[0] - x_pixel - way_radius)
			
			right_horizontal_distance = abs(mouse_coord[0] + image_tower_cursor.get_rect().width - x_pixel - way_radius)
			
			D_y = pygame_y(eval(game.game_function) * game.proportion) + way_radius
			
			A_y = mouse_coord[1]
			
			# The vertical distance between the current function point and the current tower image point.
			vertical_distance = abs(D_y - A_y)

			# This for loop iterates over all the frame when image_frame_step is going to be all the natural values between 0 and the length of a side of the tower image (that is a square).
			for image_frame_step in range(image_tower_cursor.get_rect().width):
				
				# Check the upper side of the frame.
				
				A_x = mouse_coord[0] + image_frame_step

				B_x = x_pixel + way_radius
				
				# The horizontal distance between the current function point and the current tower image point.
				horizontal_distance = abs(A_x - B_x)
					
				hypotenuse = math.sqrt(vertical_distance**2 + horizontal_distance**2)

				# If True the tower is on the way, return False.
				if hypotenuse < way_radius:
					
					return False
						
				# Check the left side of the frame. Uses the D_y pixel of the upper piece of the frame.
				
				vertical_distance = abs(mouse_coord[1] + image_frame_step - D_y)

				hypotenuse = math.sqrt(vertical_distance**2 + left_horizontal_distance**2)
						
				if hypotenuse < way_radius:
					
					return False
					
				# Check the right side of the frame. Uses the vertical distance of the left piece of frame.
				hypotenuse = math.sqrt(vertical_distance**2 + right_horizontal_distance**2)
				
				# If True the tower is on the way, return False.
				if hypotenuse < way_radius:
					
					return False

				# Check the lower side of the frame. Uses D_y, A_x, B_x.
					
				# The horizontal distance of the upper frame and the lower frame is same for each pixel.
				horizontal_distance = abs(A_x - B_x)

				vertical_distance = abs(mouse_coord[1] + image_tower_cursor.get_rect().height - D_y)
					
				hypotenuse = math.sqrt(vertical_distance**2 + horizontal_distance**2)
						
				# If True the tower is on the way, return False.
				if hypotenuse < way_radius:
					
					return False
	
		return True
		

def create_tower(tower_image, tower, mouse_coord):
	"""
		The function receives the image of the tower, its icon instance and the current mouse coordinate.
	"""
	
	global messages_for_the_server
	
	if tower_image == "Dark Cat.png":
	
		Tower(mouse_coord, tower_image, 250, 250, 15, "wool.gif", ["regular"], "farthest", 10, tower)
		
		messages_for_the_server.append("Game:tower_placed:Dark Cat")
		reset_cursor()
		
	elif tower_image == "MachineGun.png":
	
		Tower(mouse_coord, tower_image, 125, 350, 3, "wool.gif", ["regular"], "farthest", 30, tower)
		
		messages_for_the_server.append("Game:tower_placed:Machine Gun")
		reset_cursor()
		
	elif tower_image == "Bomber.png":
		
		Tower(mouse_coord, tower_image, 250, 250, 20, "bomb.gif", ["bomber", 100, "explosion.gif"], "farthest", 10, tower)
		
		messages_for_the_server.append("Game:tower_placed:Bomber")
		reset_cursor()
		
	elif tower_image == "Witch.png":
		
		Tower(mouse_coord, tower_image, 150, 300, 20, "ghost.gif", ["witch", 5], "farthest", 6, tower)
		
		messages_for_the_server.append("Game:tower_placed:Witch")
		reset_cursor()
		
	elif tower_image == "Factory1.png":
		
		Tower(mouse_coord, "Factory1.png", 0, 0, 0, '', [], '', 0, tower)
		messages_for_the_server.append("Game:tower_placed:Factory1")
		reset_cursor()
		
	elif tower_image == "Factory2.png":
		
		Tower(mouse_coord, "Factory2.png", 0, 0, 0, '', [], '', 0, tower)
		messages_for_the_server.append("Game:tower_placed:Factory2")
		reset_cursor()
		
	elif tower_image == "Factory3.png":
		
		Tower(mouse_coord, "Factory1.png", 0, 0, 0, '', [], '', 0, tower)
		messages_for_the_server.append("Game:tower_placed:Factory3")
		reset_cursor()
		
		
def posite_value(value):
	"""
		The function returns the value if its positive, else returns 0.
	"""
	if value > 0:
		
		return value
	
	else:
		
		return 0
		
		
def background_music():
	"""
		The function sets the background music from on to off and from off to on.
	"""
	
	global mute
	global bg_music_index
	
	if play_music.image_name == "Mute.png":
		
		play_music.image_name = "speaker_on.png"
		
		play_music.image = pygame.image.load("speaker_on.png")
		
		mute = True
		
		pygame.mixer.music.pause()
		
	else:
	
		play_music.image_name = "Mute.png"
		
		play_music.image = pygame.image.load("Mute.png")
		
		mute = False
		
		pygame.mixer.music.play()
		

def new_game_button():
	"""
		The function calls the create game page.
	"""

	global current_buttons
	global play_music

	# Reset current_buttons
	current_buttons = []
	
	buttons_to_push.append(play_music)
	
	push_buttons()

	create_game()
	

def insructions_button():
	"""
		The function sets instructions_button to True.
	"""
	
	global print_instructions
	global new_game_button
	
	remove_buttons.append(new_game_button)
	
	pop_buttons()
	
	print_instructions = True
	

def input_instructions():
	"""
		The function sets the Input Instructions page.
	"""
	
	global game_input
	global buttons_to_push
	global game_input_time_bool
	global input_instructions_page
	
	# Don't print the left time while in input_instructions page.
	game_input_time_bool = False
	
	input_instructions_page = True
	
	game_input.set_activation(False)
	
	DISPLAYSURF.blit(pygame.image.load("Input Instructions.png"), (0, 0))
	
	buttons_to_push.append(Button((0, 764), "Back.png", back_to_input, True, DISPLAYSURF))
	
	push_buttons()


def back_to_input():
	"""
		The function returns the player from the input instructions page to the create game page.
	"""
	
	global game_input
	global opponent_name
	global buttons_to_push
	global game_input_time_bool
	global input_instructions_page
	
	# Return to print how much time left.
	game_input_time_bool = True
	
	input_instructions_page = False
	
	game_input.set_activation(True)
	
	DISPLAYSURF.blit(pygame.image.load("Create Game.png"), (0, 0))
	
	set_name(opponent_name)
	
	buttons_to_push.append(Button((0, 714), "Input Instructions button.png", input_instructions, True, DISPLAYSURF))
	
	push_buttons()
	

def push_buttons():
	"""
		The function receives a list of buttons with the global buttons_to_push, sets them all and adds them to current_buttons. 
	"""
	
	global buttons_to_push
	
	for button in buttons_to_push:
		
		button.set_button()
	
		current_buttons.append(button)
	
	buttons_to_push = []
	

def pop_buttons():
	"""
		The function receives a list of buttons via remove_buttons global list and removes the from current_buttons.
	"""
	
	global current_buttons
	global remove_buttons

	for button in remove_buttons:
		
		# In case the button isn't in current_buttons.
		try:
			current_buttons.remove(button)
		except:
			pass
		
	remove_buttons = []


def create_game():
	"""
		The function sets the create game page. 
	"""

	global game_created
	global current_text_box
	global buttons_to_push
	
	# Print the create game screen image.
	DISPLAYSURF.blit(pygame.image.load("Create Game.png"), (0, 0))
		
	# Allow the client to enter his name.
	current_text_box = name_input
	
	buttons_to_push.append(current_text_box)
	
	# Add the name text box to the buttons list.
	push_buttons()

	game_created = True

	
def set_game(game_function, x_0_coordinate, x_f_coordinate):
	"""
		The function sets the game.
	"""
	global game_started
	global game
	global game_map
	global current_scene
	global buttons_to_push
	
	map = pygame.image.load(game_map)
	
	DISPLAYSURF.blit(map, (0, 0))
	
	# The current_scene is the map, nothing new has been modified yet.
	current_scene = map
	
	game = Game(game_function, x_0_coordinate, x_f_coordinate, [], 25)
	
	# Draw the game path on the map.
	game.build_path()
	
	tower_icons = [TowerIcon((1200, 350), "MachineGun.png", DISPLAYSURF, "Machine Gun", "attack: 125  range: 350  price: 1350", (1160, 720), ["Machine Gun: straight and precise fire,", "very fast reloading.", "no special abilities."], tower_icon_press, 1350),
				   TowerIcon((1300, 250), "Dark Cat.png", DISPLAYSURF, "Dark Cat", "attack: 250  range: 250  price: 300", (1160, 720), ["Dark Cat: straight fire, average reloading.", "", "no special abilities."], tower_icon_press, 300),
				   TowerIcon((1200, 250), "Bomber.png", DISPLAYSURF, "Bomber", "attack: 250  range: 250  price: 1200", (1160, 720), ["Bomber: straight fire, average reloading.", "", "Shoots a suicide bomber."], tower_icon_press, 1200),
				   TowerIcon((1300, 350), "Witch.png", DISPLAYSURF, "Witch", "attack: 150  range: 300  price: 1200", (1160, 720), ["Witch: straight fire, average reloading.", "Shoots ghosts that frighten the soldiers", "and moves them backwards."], tower_icon_press, 1200),
				   TowerIcon((1200, 450), "Factory1.png", DISPLAYSURF, "Factory1", "attack: 0  range: 0  price: 1000", (1160, 720), ["Factory1: products money.", "", "150 per 2.5 seconds"], tower_icon_press, 1000),
				   TowerIcon((1300, 450), "Factory2.png", DISPLAYSURF, "Factory2", "attack: 0  range: 0  price: 6500", (1160, 720), ["Factory2: products money.", "", "1400 per 8 seconds"], tower_icon_press, 6500),
				   TowerIcon((1200, 550), "Factory3.png", DISPLAYSURF, "Factory3", "attack: 0  range: 0  price: 30000", (1160, 720), ["Factory1: products money.", "", "7500 per 15 seconds"], tower_icon_press, 30000)]
	
	soldier_icons = [SoldierIcon((1380, 250), "private.png", DISPLAYSURF, "Private", "speed: 2  health: 200  price: 15", (1160, 720), ["Private: low speed, very low health", "1 life cost", "no special abilities."], None, 15),
					 SoldierIcon((1450, 250), "private2.png", DISPLAYSURF, "Private2", "speed: 2  health: 400  price: 30", (1160, 720), ["Private2: low speed, low health", "1 life cost", "no special abilities."], None, 30),
					 SoldierIcon((1380, 350), "private_first_class.png", DISPLAYSURF, "Private first class", "speed: 7  health: 250  price: 60", (1160, 720), ["Private first class: very high speed, very low health", "1 life cost", "no special abilities."], None, 60),
					 SoldierIcon((1450, 350), "Specialist.png", DISPLAYSURF, "Specialist", "speed: 2  health: 2000  price: 150", (1160, 720), ["Specialist: average speed, average health", "2 life cost", "no special abilities."], None, 150),
					 SoldierIcon((1380, 450), "Corporal.png", DISPLAYSURF, "Corporal", "speed: 2  health: 10000  price: 400", (1160, 720), ["Corporal: average speed, average health", "2 life cost", "no special abilities."], None, 400),
					 SoldierIcon((1450, 450), "Sergeant.png", DISPLAYSURF, "Sergeant", "speed: 2  health: 50000  price: 1000", (1160, 720), ["Sergeant: average speed, average health", "2 life cost", "no special abilities."], None, 1000),
					 SoldierIcon((1380, 550), "PrivateSpaceShip.png", DISPLAYSURF, "PrivateSpaceShip", "speed: 1  health: 110000  price: 7500", (1160, 720), ["PrivateSpaceShip: low speed, high health", "5 life cost", "Contains random soldiers."], None, 1)]
	
	buttons_to_push += tower_icons + soldier_icons
	
	push_buttons()
	
	update_scene()
	
	game_started = True

	
def update_opponent_data(data):
	"""
		The function receives data from the server and updates this data in the right box of the game input text boxes.
	"""
	
	global game_input

	if len(data) > 7 and data[: 7] == "accept:":
		
		data = data[7 :]
		
		if len(data) > 14 and data[:14] == "game_function:":
		
			game_input.text_boxes["game function"].text = data[14:]
			game_input.text_boxes["game function"].set_interrupt()
			
		elif len(data) > 21 and data[:21] == "first_x_coordination:":
		
			game_input.text_boxes["first x coordination"].text = data[21:]
			game_input.text_boxes["first x coordination"].set_interrupt()
		
		elif len(data) > 20 and data[:20] == "last_x_coordination:":
		
			game_input.text_boxes["last x coordination"].text = data[20:]
			game_input.text_boxes["last x coordination"].set_interrupt()
			
	elif data == "done":
		
		game_input.completed = True
	
	else:

		if len(data) > 14 and data[:14] == "game_function:":
		
			game_input.text_boxes["game function"].second_text = data[14:]
		
		elif len(data) > 21 and data[:21] == "first_x_coordination:":
		
			game_input.text_boxes["first x coordination"].second_text = data[21:]
			
		elif len(data) > 20 and data[:20] == "last_x_coordination:":
		
			game_input.text_boxes["last x coordination"].second_text = data[20:]


def true_or_false(num):
	"""
		The function returns true if the received number is 0, else returns False.
	"""
	
	if num == '0':
		return True
	
	else:
		return False
		

def multiple_messages(messages):
	"""
		The function receives a list of messages.
	"""
	
	if len(messages) > 1:
		
		for i in range(1, len(messages) - 1):
			
			messages[i] = messages[i][:-1]
	
	return messages
	

def reset_cursor():
	"""
		The function resets the cursor.
	"""
	
	global mouse_tower
	global tower_cursor
	global image_tower_cursor
	global image_tower_cursor_string
	
	pygame.mouse.set_visible(True)
	mouse_tower = None
	tower_cursor = False
	image_tower_cursor = ""
	image_tower_cursor_string = ""
	
	
def update_scene():
	"""
		The function updates the variable current_scene to the current screen image.
	"""
	
	global current_scene
	
	try:
		
		pygame.image.save(DISPLAYSURF, "current_scene.png")
	
		current_scene = pygame.image.load("current_scene.png")
	
	except:
		
		pygame.image.save(DISPLAYSURF, "current_scene_copy.png")
	
		current_scene = pygame.image.load("current_scene_copy.png")
		

def restart():
	"""
		The function restarts the current game.
	"""
	
	global restart_game
	
	restart_game = True
	

def Main_menu():
	"""
		The function generates the main menu.
	"""
	
	global new_game_button
	global insructions_button
	global buttons_to_push
	global game_crashed
	
	Main_menu = pygame.image.load('Cheese Party.png')
	
	DISPLAYSURF.blit(Main_menu, (0, 0))
	
	buttons_to_push.append(new_game_button)
	buttons_to_push.append(instructions_button)
	
	push_buttons()
	
	if game_crashed:
		
		DISPLAYSURF.blit(pygame.font.SysFont('Ravie', 20).render("Game too crowded", True, (0, 0, 0)), (250, 700))
		game_crashed = False
	

"""
	PREPARATION FOR THE MAIN LOOP.
"""

pygame.init()

DISPLAYSURF = pygame.display.set_mode((1536, 864), pygame.FULLSCREEN)

pygame.display.set_caption('Cheese Party TD')

fpsClock = pygame.time.Clock()

restart_game = True

new_game_button = Button(( 618, 200), "new game.png", new_game_button, True, DISPLAYSURF)

instructions_button = Button(( 618, 350), "instructions button.png", insructions_button, True, DISPLAYSURF)

# Get event that alerts if song is ended.
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

# A list that contains background music.
bg_music = ["theme1.ogg"]

shuffle(bg_music)

# An index on the current music in the list.
bg_music_index = 0

pygame.mixer.music.load(bg_music[bg_music_index])

pygame.mixer.music.play()

mute = False


"""
	MAIN LOOP
"""

while True:
	
	# Reset all the variables in order to start a new game from the main menu.	
	if restart_game:

		# The socket of the player.
		my_socket = socket.socket()
		
		# A list of all the gifs in the game.
		my_gifs = Gifs_list(None)
		
		# The gif that being displayed when the server is looking for an opponent.
		searching_gif = Gif_Image('searching.gif', (450, 350))
		searching_gif2 = Gif_Image('searching2.gif', (700, 500))
		
		# True if searching_gifs is now being displayed.
		looking_for_opponent_gif = False
		
		restart_game = False
		
		FPS = 30
		
		current_buttons = []
		
		buttons_to_push = []
		
		remove_buttons = []

		game_created = False
		
		# If True, prints a message.
		game_crashed = False

		game_started = False
		
		# Going to contain the chosen game map.
		game_map = 'Map1.png'

		# Going to contain the current game scene.
		current_scene = None

		# True if the player clicked a tower in the towers menu and the cursor have changed to the tower image.
		tower_cursor = False

		# Contains the image of the tower that pressed in the tower menu.
		image_tower_cursor = ""

		image_tower_cursor_string = ""

		# Contains the button tower instance of the mouse.
		mouse_tower = None
		
		# Sound on/off button
		play_music = Button((0, 0), "Mute.png", background_music, False, DISPLAYSURF)
		buttons_to_push.append(play_music)
		push_buttons()
		
		# Contains the name of the player.
		my_name = [None, False]

		# The name input box.
		name_input = Input_Box((350, 300), "Text Box1.png", 11, (255, 255, 255), 'Pristina', 40, 22, 1, "Please Enter your name")

		# The current text box that the player is typing into.
		current_text_box = None

		# Going to contain the id the player is going to identify to the server with.
		my_id = None
		
		# When True the player wants the first time to connect the server.
		ready_to_connect = False
		
		# If true, the player is connected to the server.
		connected = False
		
		# If True the player has an opponent.
		has_opponent = False
		
		# The name of the opponent.
		opponent_name = ''
		
		# If true, game input won't be printed.
		game_input_off = False
		
		# True when the data about the game was decided.
		data_completed = False
		
		# The game instance.
		game = None
		
		# A backup of the last frame cursor position.
		cursor_pos_copy = (0, 0)
		
		# Contains new messages that have to be sent to the server.
		messages_for_the_server = []
		
		# If true the game was ended.
		game_finished = False
		
		# If True prints the instructions page.
		print_instructions = False
		
		# Just if True, updates the game input time.
		game_input_time_bool = True
		
		# Contains the x_pixel of the last destroyed space ship.
		current_SpaceShip_x_pixel = 0
		
		# True if currently in the input instruction page.
		input_instructions_page = False
		
		# Contains the soldiers that are currently moving backwards. Their values is how many frames left that they have to move backwards.
		frightened_soldiers = {}
		
		Main_menu()
	
	# Take care of all the new events.
	for event in pygame.event.get():
		
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		
		# Left click 
		if pygame.mouse.get_pressed()[0]:
			
			# Deselect the current current_text_box if exist.
			if current_text_box:
				
				current_text_box.enter = False
				
				current_text_box.release_track()
				
				current_text_box = None
			
			cursor_pos = pygame.mouse.get_pos()
		
			# Iterates over all the buttons till finds a pressed button. 
			for button in current_buttons:
				
				if button.is_pressed(cursor_pos):

					button.press()
					
					if button.die:
						
						# button.press() sometimes deletes the button itself.
						try:
							current_buttons.remove(button)
						except:
							pass
					
					break
		
			# Check if a tower has to get placed and if it can be placed that point.
			if tower_cursor and try_place_tower(cursor_pos):
				
				create_tower(image_tower_cursor_string, mouse_tower, cursor_pos)

		
		# Check if there's a keyboard data.
		if event.type == pygame.KEYDOWN:

			# Check if there is an active text box.
			if current_text_box:

				# Check if its a capital letter.
				if pygame.key.get_mods() & KMOD_CAPS and len(pygame.key.name(event.key)) == 1:
					
					if isinstance(current_text_box, Elaborate_Input_box):
						
						current_text_box.elaborate_add_char(pygame.key.name(event.key).upper())
					else:
						
						current_text_box.add_char(pygame.key.name(event.key).upper())
				
				else:
				
					if isinstance(current_text_box, Elaborate_Input_box):
						
						current_text_box.elaborate_add_char(pygame.key.name(event.key))
					
					else:
						
						current_text_box.add_char(pygame.key.name(event.key))
						
		if event.type == SONG_END:
		
			if bg_music_index < len(bg_music) - 1:
			
				bg_music_index += 1
			
			else:
				
				bg_music_index = 0

			pygame.mixer.music.load(bg_music[bg_music_index])

			pygame.mixer.music.play()

	# If the game was created- set it.
	if game_created:
		
		# The first thing the player has to do when he starts a new game is to enter his name.
		if not my_name[1]:

			name_input.print_box()

			# If the name was entered set it to True.
			if name_input.enter and len(name_input.text) > 0:
				
				my_name[1] = True
				
				ready_to_connect = True
				
		# After entering his name properly the player connects to the server and finding an opponent.
		elif ready_to_connect:
			
			DISPLAYSURF.blit(pygame.image.load("Create Game.png"), (0, 0))
			
			ready_to_connect = False
			
			# Try to connect the server.
			try:

				# Connect to the server.
				my_socket.connect(('192.168.1.12', 951))
				
				# Send to the server the name of the client.
				my_socket.send(name_input.text)
				
				# Receive from the server the player id.
				data = my_socket.recv(1024)[12 :]
				
				# If the server has an opponent to the player his first character of the data contains 0. else it contains 1 (or any other character).
				has_opponent = true_or_false(data[0])
				
				# If the server couldn't found an opponent, alert the player.
				if not has_opponent:
				
					if not looking_for_opponent_gif:
						
						my_gifs.gifs_list.append(searching_gif)
						my_gifs.gifs_list.append(searching_gif2)
						my_gifs.background = "Create Game LFO.png"
						looking_for_opponent_gif = True	
				
				my_id = data[1:]
				
				# Alert that the player is now connected to the server.
				connected = True
				
				if has_opponent:
					
					game_input = Input_Wire({"game function" : Elaborate_Input_box((350, 250), "Text Box1.png", 40, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter a function", "interrupt.png", "accept button.png", (255, 255, 255)),
											 "first x coordination" : Elaborate_Input_box((350, 360), "Text Box1.png", 12, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter the first x coordinate", "interrupt.png", "accept button.png", (255, 255, 255)),
											 "last x coordination" : Elaborate_Input_box((350, 470), "Text Box1.png", 12, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter the last x coordinate", "interrupt.png", "accept button.png", (255, 255, 255))})
				
					game_input.set_Input_Wire()
					
					buttons_to_push.append(Button((0, 714), "Input Instructions button.png", input_instructions, True, DISPLAYSURF))
					
					push_buttons()
				
			# If the server is down- restart the game.
			except:
				
				restart_game = True
		
		elif not data_completed and has_opponent and not game_input_off:
			
			game_input.print_wire()
		
	# If the player is connected to the server get rlist, wlist and xlist.
	if connected:
		
		rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
		
		# If true there's a new data from the server.
		if my_socket in rlist:
			
			# In case The server is down.
			try:
				
				received = my_socket.recv(1024)

				received_data = received[12 :].split('new_message:')
				
				for data in received_data:
				
					# Disconnected from the server.
					if data == '':
						
						restart_game = True
						
						try:
							
							Game.result("lose")
							
						# No game has created yet.
						except:
							break					
					
					# The server hasn't found an opponent yet, check if there's a progression.
					if not has_opponent:
						
						# An opponent has found!
						if data[0] == '0':
							
							has_opponent = True
							
							# Set the game input text boxes.
							game_input = Input_Wire({"game function" : Elaborate_Input_box((350, 250), "Text Box1.png", 40, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter a function", "interrupt.png", "accept button.png", (255, 255, 255)),
													 "first x coordination" : Elaborate_Input_box((350, 360), "Text Box1.png", 12, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter the first x coordinate", "interrupt.png", "accept button.png", (255, 255, 255)),
													 "last x coordination" : Elaborate_Input_box((350, 470), "Text Box1.png", 12, (255, 255, 255), 'Pristina', 20, 50, 1, "Please Enter the last x coordinate", "interrupt.png", "accept button.png", (255, 255, 255))})
						
							# Erase the waiting for opponent statement.
							DISPLAYSURF.blit(pygame.image.load("Create Game.png"), (0, 0))
							
							looking_for_opponent_gif = False
							
							my_gifs.gifs_list.remove(searching_gif)
							my_gifs.gifs_list.remove(searching_gif2)
							
							my_gifs.background = None
							
							game_input.set_Input_Wire()
							
							buttons_to_push.append(Button((0, 714), "Input Instructions button.png", input_instructions, True, DISPLAYSURF))
							
							push_buttons()
							
					elif data[: 5] == "name:":
						
						set_name(data[5 :])
						
					elif data[: 11] == "input_time:":
						
						set_input_time(data[11: ])
						
					elif data[: 7] == "Result:":
						
						Game.result(data[7: ])

						if not data_completed:
							
							game_input_off = True
						
					elif not data_completed:
						
						if "input_status:" in data:
							
							# This is the last property update, might also contain if the input is valid or not. 
							update_opponent_data(data[: data.index("input_status:")])
						
						else:
							
							# Updates the game input text boxes with the client new data.
							update_opponent_data(data)
						
						if "input_status:" in data:
							
							if data[data.index("input_status:") + 13 :] == "_valid":
								
								data_completed = True
								
								set_game(game_input.text_boxes["game function"].text, float(game_input.text_boxes["first x coordination"].text), float(game_input.text_boxes["last x coordination"].text))
								
							
							elif data[data.index("input_status:") + 13 : data.index("input_status:") + 24] == "_not_valid:":

								game_input.new_chance(data[24 :])
					
					if data[: 5] == "Game:":
						
						data = data[5 :]
						
						if data[: 10] == "new_round:":
							
							data = data[10 :]
							
							game.round = data[: data.index(':')]
							
							game.new_events.append("new_round")
							
							data = data[data.index(':') + 1 :]
							
							if data[: 9] == "soldiers:":
								
								data = data[9 :]
								
								data = [[data.split(',')[index], int(data.split(',')[index + 1])] for index in range(0, len(data.split(',')), 2)]
								
								for type, wait in data:
									
									game.soldiers_to_send.append([type, wait, 0, 0])
									
								game.round_ended = False
						
						if data[: 19] == "tower_confirmation:":
						
							data = data[19 :]
							
							if data[: 4] == "True":
								
								game.tower_confirmation(data[4 :])
								
						elif data[: 21] == "soldier_confirmation:":
						
							data = data[21 :]
							
							if data[: 4] == "True":
								
								game.soldier_confirmation(data[4 :])
							
						elif data[: 6] == "money:":
							
							game.money = data[6 :]
						
						elif data[: 3] == "hp:":
							
							game.hp = data[3: ]
							
						elif data[: 12] == "new_soldier:":

							game.soldiers_to_send.append([data[12: ], 0, 0, 0])
							
			except:
				server_crashed()
			
		# If there's new data that has to be sent to the server, send it.
		if my_socket in wlist:
			
			# In case the server is down.
			try:
			
				# If the player is in the create game page and have to choose data with his opponent send the server what's the player entered new.
				if has_opponent and not data_completed:
					
					# Sends the server the new data that the player entered.
					game_input.send_data(my_socket, my_id)
				
				for message in messages_for_the_server:
					
					my_socket.send("new_message:" + my_id + message)
					
					messages_for_the_server.remove(message)
			
			except:
				restart_game = True
			
	# When the game have started do everything necessary during it.
	if game_started:
		
		# Print the current_scene image
		DISPLAYSURF.blit(current_scene, (0, 0))
		
		# Update the scene to contain the new towers.
		game.set_new_towers()
		
		# Prepare the soldiers that are waiting to be sent in one more step.
		game.send_soldiers()
		
		# Update all the towers in relative to the new events on the screen.
		game.tower_manager()
		
		# Take all the soldiers on the path their next step.
		game.move_soldiers()
		
		# Take all the bullets on the screen to their next step.
		game.move_bullets()
		
		# If the mouse is over a tower icon print its data.
		game.check_tower_data()
		
		# Display the currently dying soldiers.
		game.current_dying_soldiers()
		
		# Manage the hits of the bullets and their effect.
		game.look_for_hits()
		
		# Update the server for every necessary stuff about the game status.
		game.update_status()
		
		# Print some basic data of the player.
		game.display_data()
		
		# Alerts the player for every new events that have occurred.
		game.events()
		
		# If the cursor is a tower image update the image location to the cursor location.
		if tower_cursor:

			if list(cursor_pos_copy)[0] != 0 and list(pygame.mouse.get_pos())[0] > 1510 and abs(list(cursor_pos_copy)[0] - list(pygame.mouse.get_pos())[0]) > 100:

				DISPLAYSURF.blit(image_tower_cursor, cursor_pos_copy)
				
				pygame.mouse.set_pos(cursor_pos_copy)
				
			else:

				cursor_pos_copy = pygame.mouse.get_pos()

				DISPLAYSURF.blit(image_tower_cursor, pygame.mouse.get_pos())
			
	if game_finished:
		
		restart_game = True
	
	if print_instructions:
		
		DISPLAYSURF.blit(pygame.image.load("instructions.png"), (0, 0))
		
		buttons_to_push.append(Button((0, 764), "main menu button.png", Main_menu, True, DISPLAYSURF))

		push_buttons()
		
		print_instructions = False
	
	if not game_finished:
		
		# Display all the next frames of the current gifs.
		my_gifs.next_frames()
	
	play_music.set_button()
	
	#Wait till it's time for the next frame. 
	fpsClock.tick(FPS)
	
	# Update all the new changes that have done.
	pygame.display.update()