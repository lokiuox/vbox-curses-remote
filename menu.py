#!/usr/bin/python3
import curses
import threading
import queue
import time

class Menu:

	# Static threading "magic"
	# key queue contains key presses
	keyq = queue.Queue()
	screen = None
	x = 0
	y = 0
	loading_scr = None

	@staticmethod
	def show_loading():
		threading.Thread(target=Menu.loading_scr.draw).start()
		

	@staticmethod
	def key_thread():
		while True:
			key = Menu.screen.getch()
			Menu.keyq.put(key)

	@staticmethod
	def global_init(screen, x = 0, y = 0):
		Menu.x = x
		Menu.y = y
		Menu.screen = screen
		t = threading.Thread(target=Menu.key_thread)
		t.setDaemon(True)
		t.start()
		Menu.loading_scr = Menu("Loading...")


	def __init__(self, title=None, prev=None):
		self.items     = []     # Array - MenuItem array

		# Default Values
		self.numeric   = True   # Bool - Use of the numpad
		self.noback    = False  # Bool - Use of the left arrow key to return  
		self.closemenu = False  # Bool - This kills the crab, er... menu
		self.tooltips  = False   # Bool - Display item tooltips under menu title
		self.width     = 1      # Int  - Minimum width of the menu
		self.refresh   = 3      # Int  - Refresh rate in seconds
										# Menu also updates upon selection
		self.previous=prev

		# Set the title if provided
		self.title = title

	def update_thread(self):
		while not self.closemenu:
			for i in self.items:
				i.do_update()
			time.sleep(self.refresh)

	def set_title(self, title):
		self.title = " " + title
	
	def add_item(self, menu_item):
		self.items.append(menu_item)
	
	def set_noback(self, truefalse):
		self.noback = truefalse
	
	def set_numeric(self, truefalse):
		self.numeric = truefalse

	def enable_tooltips(self, truefalse):
		self.tooltips = truefalse

	def set_refresh(self, rate):
		self.refresh = rate
	
	def set_width(self, width):
		self.width = width
	
	def size(self):
		return len(self.items)

	def close(self):
		self.closemenu = True

	def draw(self, x=None, y=None):

		if x is None:
			x = Menu.x
		if y is None:
			y = Menu.y

		# Start gathering button/tooltip text asynchronously.
		t = threading.Thread(target = self.update_thread)
		t.setDaemon(True)
		t.start()

		# Double check that the menu isn't going to autoclose
		self.closemenu = False
		
		# Make room for the title and tooltips
		# IF they exist.
		if self.title != None:
			x += 2
		elif self.tooltips == True:
			x += 1

		if self.title is not None and self.title != "Loading...":
			self.loading_scr.close()

		# Init stuff
		Menu.screen.clear()
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED,    curses.COLOR_WHITE)
		curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
		Menu.screen.keypad(1)
		pos = 0
		key = ord('z')
		sel_color     = curses.color_pair(2)
		unsel_color   = curses.A_REVERSE
		title_color   = curses.A_REVERSE
		tooltip_color = curses.A_NORMAL
		color = unsel_color
		curses.curs_set(0)

		# Figure out how wide to make the background
		padding = self.width
		for i in self.items:
			le = len(i.get_text()) + 2
			if self.numeric == True:
				le += 4
			if le > padding:
				padding = le

		tlen = len(str(self.title)) + 2
		if tlen > padding:
			padding = tlen

		# Menu loop
		while self.closemenu == False:

			# Draw screen border
			Menu.screen.border(0)

			# Draw the title if it exists
			if self.title != None:
				Menu.screen.addstr(x-2, y, str(" " + self.title).ljust(padding), title_color)

			if len(self.items) > 0:
				# Draw the tooltip/section if it exists
				if self.tooltips == True:
					Menu.screen.move(x-1, 0)
					Menu.screen.clrtoeol()
					Menu.screen.addstr(x-1, y+1, str(self.items[pos].get_tooltip()) + " ", tooltip_color)

			# Draw each item the menu
			for idx, item in enumerate(self.items):
				if pos == idx:
					color = sel_color
				else:
					color = unsel_color
				if self.numeric != False:
					i_num = str(idx + 1) + " - "
				else:
					i_num = ""
				Menu.screen.addstr(idx+x, y, (" " + i_num + item.get_text()).ljust(padding), color)
			
			Menu.screen.refresh()

			# Retrieve key sent from key thread
			if not Menu.keyq.empty() and len(self.items) > 0:
				key = Menu.keyq.get()

				# Key handling
				if key == curses.KEY_DOWN:
					pos += 1
					pos %= self.size()

				elif key == curses.KEY_UP:
					pos -= 1
					pos %= self.size()

				elif key == curses.KEY_LEFT and self.noback == False:
					self.close()
				
				elif key == ord('\n') or key == curses.KEY_RIGHT:
					self.items[pos].do_action()
				
				elif self.numeric == True and (key >= ord("0") and key <= ord(str(self.size()))):
					pos = int(chr(key)) - 1
					self.items[pos].do_action()

				elif key == 3: # CTRL+C
					raise KeyboardInterrupt

			else:
				time.sleep(.025)
		
		# TODO: Clear the menu only, not whole curses screen.
		Menu.screen.clear()

class MenuItem:

	def __init__(self, text, action, *tooltip):
		
		self.disp_text = None
		self.disp_tooltip = ""
		
		self.text = text
		self.action = action

		self.text_update_q = queue.Queue()
		self.tooltip_update_q = queue.Queue()

		if len(tooltip) > 0:
			self.tooltip = tooltip
		else:
			self.tooltip = ""
	
	def set_text(self, text):
		self.text = text

	def set_tooltip(self, tooltip):
		self.tooltip = tooltip
	
	def set_action(self, action):
		self.action = action

	def do_update(self):
		self.update_text()
		self.update_tooltip()

	def get_text(self):
		if self.disp_text == None:
			self.update_text()
		while not self.text_update_q.empty():
			self.disp_text = self.text_update_q.get_nowait()
		return self.disp_text

	def get_tooltip(self):
		while not self.tooltip_update_q.empty:
			self.disp_tooltip = self.tooltip_update_q.get_nowait()
		return self.disp_tooltip

	def update_text(self):
		# Function with args
		if type(self.text) is tuple:
			self.text_update_q.put(self.text[0](*self.text[1:]))
		# Function without args
		elif type(self.text) is not str:
			self.text_update_q.put(self.text())
		# String (hopefully)
		else:
			self.text_update_q.put(self.text)

	def update_tooltip(self):
		# Function with args
		if type(self.tooltip) is tuple:
			self.tooltip_update_q.put(self.tooltip[0](*self.tooltip[1:]))
		# Function without args
		elif type(self.tooltip) is not str:
			self.tooltip_update_q.put(self.tooltip())
		# String (hopefully)
		else:
			self.tooltip_update_q.put(self.tooltip)
		

	def get_action(self):
		return self.action

	def do_action(self):
		if type(self.action) is tuple:
			return self.action[0](*self.action[1:])
		return self.action()

if __name__ == '__main__':
	print("Please run 'vcr'.")


