#!/usr/bin/python3
import curses
import threading
import queue
import time

class Menu:

	# Static threading "magic"
	# key queue contains key presses
	key_thread_object = None
	keyq = queue.Queue()

	def __init__(self, scr, *title):
		self.items     = []     # Array - MenuItem array
		self.screen    = scr    # Curses screen object

		##self.keyq      = queue.Queue()

		# Default Values
		self.numeric   = True   # Bool - Use of the numpad
		self.noback    = False  # Bool - Use of the left arrow key to return  
		self.closemenu = False  # Bool - This kills the crab, er... menu
		self.tooltips  = True   # Bool - Display item tooltips under menu title
		self.width     = 1      # Int  - Minimum width of the menu
		self.refresh   = 5      # Int  - Refresh rate in seconds
										# Menu also updates upon selection
		self.thread_break = False

		#self.q = queue.Queue(maxsize=1)

		# Set the title if provided
		if len(title) > 0:
			self.title  = title[0]
		else:
			self.title  = None

	def update_thread(self):
		t_run = 0
		while not self.closemenu:
			#self.do_refresh()
			for i in self.items:
				i.do_update()
			time.sleep(self.refresh)

	def key_thread(self):
		stdkey = curses.initscr()
		while not self.thread_break and not self.closemenu:
			key = stdkey.getch()
			Menu.keyq.put(key)

	#def do_refresh(self):
	#	for i in self.items:
	#		i.do_update()

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
		self.thread_break = True
	
	def clr_draw(self, x, y):
		self.screen.clear()
		self.draw(x,y)

	def key_qer(self):
		
		# Threadsafe (ish) screen for getting key commands
		stdkey    = curses.initscr()

		while self.closemenu != False:
			key = stdkey.getch()
			Menu.keyq.put(key)

	def draw(self, x, y):
		
		# Start gathering button/tooltip text asynchronously.
		threading.Thread(target = self.update_thread).start()

		# Start keylistener asynchronously
		# IF it isn't already running
		# This is so that the draw-loop doesn't block on getch()
		if Menu.key_thread_object == None:
			Menu.key_thread_object = threading.Thread(target = self.key_thread).start()

		# Double check that the menu isn't going to autoclose
		self.closemenu = False
		
		# Make room for the title and tooltips
		# IF they exist.
		if self.title != None:
			x += 2
		elif self.tooltips == True:
			x += 1

		# Init stuff
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED,    curses.COLOR_WHITE)
		curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
		self.screen.keypad(1)
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
			
			# Draw the title if it exists
			if self.title != None:
				self.screen.addstr(x-2, y, str(" " + self.title).ljust(padding), title_color)

			# Draw the tooltip/section if it exists
			if self.tooltips == True:
				self.screen.move(x-1, 0)
				self.screen.clrtoeol()
				self.screen.addstr(x-1, y+1, str(self.items[pos].get_tooltip()) + " ", tooltip_color)

			# Draw screen border
			self.screen.border(0)
	
			# Draw each item the menu
			nx = x
			for item in self.items:
				if pos == nx - x:
					color = sel_color
				else:
					color = unsel_color
				if self.numeric != False:
					i_num = str(nx - x + 1) + " - "
				else:
					i_num = ""
				self.screen.addstr(nx, y, (" " + i_num + item.get_text()).ljust(padding), color)
				nx += 1
			
			self.screen.refresh()

			# Retrieve key sent from key thread
			if not Menu.keyq.empty():
				key = Menu.keyq.get()
			else:
				time.sleep(.025)
				key = ord('z')
			
			# Key handling 
			if key == curses.KEY_DOWN and pos < self.size() - 1:
				pos += 1	

			elif key == curses.KEY_UP and pos > 0:
				pos -= 1

			elif key == curses.KEY_LEFT and self.noback == False:
				self.close()
			
			elif key == ord('\n') or key == curses.KEY_RIGHT:
				self.items[pos].do_action()
			
			elif self.numeric == True and (chr(key) >= "0" and chr(key) <= str(self.size())):
				pos = int(chr(key)) - 1
				self.items[pos].do_action()
		
		# TODO: Clear the menu only, not whole curses screen.
		self.screen.clear()
		self.thread_break = True

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
		self.tooltip = text
	
	def set_action(self, action):
		self.action = action

	def do_update(self):
		#threading.Thread(target=self.update_text).start()
		#threading.Thread(target=self.update_tooltip).start()
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


