#!/usr/bin/python3
import curses

class Menu:

	def __init__(self,scr):
		self.items = []
		self.actions = []
		self.args = []
		self.screen = scr
		self.noback = False
		self.closemenu = False
		self.title = None
	
	def add(self, item, action, *args):
		self.items.append(item)
		self.actions.append(action)
		self.args.append(args)
	
	def get(self):
		return self.items
	
	def set_title(self, ntitle):
		self.title = ntitle

	def set_noback(self, truefalse):
		self.noback = truefalse

	def action(self, i):
		return self.actions[i](*self.args[i])
	
	def size(self):
		return len(self.items)
	
	def close(self):
		self.closemenu = True
	
	def cldraw(self, x, y):
		self.screen.clear()
		self.draw(x,y)
	
	def draw(self, x, y):

		self.closemenu = False
		
		if self.title != None:
			x += 2

		curses.start_color()
		curses.init_pair(1,curses.COLOR_RED, curses.COLOR_WHITE)
		self.screen.keypad(1)
		pos = 0
		key = ord('z')
		h = curses.color_pair(1)
		n = curses.A_NORMAL
		color = n
		curses.curs_set(0)

		while self.closemenu == False:
			
			if key == ord('\n') or key == curses.KEY_RIGHT:
				self.action(pos)
			if key == curses.KEY_LEFT and self.noback == False:
				self.close()
			if chr(key) >= "0" and chr(key) <= str(self.size()):
				pos = int(chr(key)) - 1
				self.action(pos)
			if key == curses.KEY_DOWN and pos < self.size() - 1:
				pos += 1	
			if key == curses.KEY_UP and pos > 0:
				pos -= 1

			if self.closemenu == True:
				self.screen.clear()
			else:
				if self.title != None:
					self.screen.addstr(x-2, y, str(self.title), curses.A_NORMAL)
				self.screen.border(0)
				nx = x
				for item in self.get():
					if pos == nx - x:
						color = h
					else:
						color = n
					self.screen.addstr(nx, y, str(nx - x + 1) + " - " + item, color)
					nx += 1
				self.screen.refresh()
				key = self.screen.getch()

#class MenuItem:
#	def __init__(self, text, action, *args):
#		self.menu_item = (text, action, args)


if __name__ == '__main__':
	print("Please run the correct file. This is not the correct file.")
