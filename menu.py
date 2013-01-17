#!/usr/bin/python3
import curses

class Menu:

	def __init__(self, scr, *title):
		self.items     = []     # Array - MenuItem array
		self.screen    = scr    # Curses screen object

		# Default Values
		self.numeric   = True   # Bool - Use of the numpad
		self.noback    = False  # Bool - Use of the left arrow key to return  
		self.closemenu = False  # Bool - This kills the crab, er... menu
		self.tooltips  = True   # Bool - Display item tooltips under menu title
		self.refresh   = 5      # Int  - Refresh rate in seconds

		# Set the title if provided
		if len(title) > 0:
			self.title  = title[0]
		else:
			self.title  = None
	
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
	
	def size(self):
		return len(self.items)

	def close(self):
		self.closemenu = True
	
	def clr_draw(self, x, y):
		self.screen.clear()
		self.draw(x,y)
	
	def draw(self, x, y):

		self.closemenu = False
		
		if self.title != None:
			x += 2
		elif self.tooltips == True:
			x += 1

		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED,    curses.COLOR_WHITE)
		curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
		self.screen.keypad(1)
		pos = 0
		key = ord('z')
		sel_color =     curses.color_pair(2)
		unsel_color =   curses.A_REVERSE
		title_color =   curses.A_REVERSE
		tooltip_color = curses.A_NORMAL
		color = unsel_color
		curses.curs_set(0)

		padding = 0
		for i in self.items:
			le = len(i.get_text()) + 2
			if self.numeric == True:
				le += 4
			if le > padding:
				padding = le

		tlen = len(str(self.title)) + 1
		if tlen > padding:
			padding = tlen

		while self.closemenu == False:
			
			if key == ord('\n') or key == curses.KEY_RIGHT:
				self.items[pos].do_action()
			if key == curses.KEY_LEFT and self.noback == False:
				self.close()
			if self.numeric == True and (chr(key) >= "0" and chr(key) <= str(self.size())):
				pos = int(chr(key)) - 1
				self.items[pos].do_action()
			if key == curses.KEY_DOWN and pos < self.size() - 1:
				pos += 1	
			if key == curses.KEY_UP and pos > 0:
				pos -= 1

			if self.closemenu == True:
				self.screen.clear()
			else:
				if self.title != None:
					self.screen.addstr(x-2, y, str(self.title).ljust(padding), title_color)
				if self.tooltips == True:
					self.screen.move(x-1, 0)
					self.screen.clrtoeol()
					self.screen.addstr(x-1, y+1, str(self.items[pos].get_tooltip()) + " ", tooltip_color)
				self.screen.border(0)
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
				key = self.screen.getch()

class MenuItem:

	def __init__(self, text, action, *tooltip):
		
		self.text = text
		self.action = action
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
	
	def get_text(self):
		if type(self.text) is tuple:
			return self.text[0](*self.text[1:])
		if type(self.text) is not str:
			return self.text()
		return self.text

	def get_tooltip(self):
		if type(self.tooltip) is tuple:
			return self.tooltip[0](*self.tooltip[1:])
		if type(self.tooltip) is not str:
			return self.tooltip()
		return self.tooltip
	
	def get_action(self):
		return self.action

	def do_action(self):
		if type(self.action) is tuple:
			return self.action[0](*self.action[1:])
		return self.action()

if __name__ == '__main__':
	print("Please run the correct file. This is not the correct file.")
