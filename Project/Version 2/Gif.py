import pygame, sys, os.path
from pygame.locals import *
from PIL import Image


class Gif_Image(object):
	"""
		The class represents a gif image.
	"""
	
	def __init__(self, gif_name, location):
		
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
		if self.active:
		
			# Printing frame.
			DISPLAYSURF.blit(self.frames_list[self.current_frame_index], self.location)
			
			# Check if reached last frame.
			if self.current_frame_index > len(self.frames_list) - 2:
			
				# Resetting index to first frame.
				self.current_frame_index = 0
				
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
		for gif in self.gifs_list:
			
			if gif.active:
				
				gif.next_frame()