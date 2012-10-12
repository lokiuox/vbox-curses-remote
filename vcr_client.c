#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ncurses.h>
#include <menu.h>
#include <libssh/libssh.h>
#include "vcr_ssh.h"

int make_menu(char* items);
int init_remote_session(char* host);
int list_vms(char* buff);

ssh_session session;

int main() {

	//char vm_to_manage[128];
	char buff[1024] = "";

	initscr();	/* Start curses mode 		  */

	init_remote_session("vm@tc-eden");
	//vm_to_manage = list_vms(buff);
	list_vms(buff);

	close_session(&session);

	//getch();			/* Wait for user input */
	endwin();			/* End curses mode		  */
	return 0;
}

int init_remote_session(char* host) {

	start_session(&session, host);

	if (verify_knownhost(&session) < 0)
		return -1;

	authenticate_pubkey(&session);

	return 0;

}

int list_vms(char* buff) {

//	char* result[128];

	// Does session exsist?
	if (session == NULL) {
		return -1;
	}
	
	// Ask the remote vbox_manage to list the vms
	remote_vboxmanage(buff, &session, "list vms");

	// Create the menu
	make_menu(buff);

	// Clear the screen and draw the vms
	clear();
	printw("%s", buff);
	noecho();

	refresh();
	echo();

	return 0;
}

int make_menu(char* items) {

	MENU* the_menu = NULL;
	ITEM** item_list;
	int i = 0, n_choices = 1, c;
	char* str = items;
	clear();
	
	// Count the number of newlines because this is equal to the number of menu entries.
	while (*str++) {
		if (*str == '\n')
			n_choices++;
	}
	// Reset str.
	str = items;

	item_list = (ITEM **)calloc(n_choices + 0, sizeof(ITEM *));

	// A bunch of ways to do the same thing
	
	/*
   int i = 0;
   int str_size = strlen(str);
   char dst[str_size];
   bzero(dst, str_size);
   strncat(dst, str, sizeof(char));
   
   while (*str++) {
      if (*str == '\n' || *str == '\0') {
         item_list[i++] = new_item(dst, dst);
         dst[0] = '\0';
      } else {
         strncat(dst, str, sizeof(char));
      }
   }
	*/

	/*
   int i = 0, n = 1;
   int str_size = strlen(str);
   char dst[str_size];
   bzero(dst, str_size);
   
   while (*str++) {
      if (*str == '\n' || *str == '\0') {
         strncpy(dst, str-n, sizeof(char)*n);
         item_list[i++] = new_item(dst, dst);
         n = 0;
      } else {
			n++;
      }
   }
	*/

	char option_list[strlen(items)];
	strcpy(option_list, items);

	char* option = strtok(option_list, "\n");
	while (option != NULL) {
		item_list[i++] = new_item(option, option);
		option = strtok(NULL, "\n");
	}

	the_menu = new_menu((ITEM **)item_list);

	set_menu_opts(the_menu, O_ONEVALUE);

	//mvprintw(LINES - 2, 0, "(F1 to Exit)");
	post_menu(the_menu);
	refresh();

	cbreak();
	noecho();
	keypad(stdscr, TRUE);

	while((c = getch()) != KEY_F(1)) {
		switch(c) {
			case KEY_DOWN:
				menu_driver(the_menu, REQ_DOWN_ITEM);
				break;
			case KEY_UP:
				menu_driver(the_menu, REQ_UP_ITEM);
				break;
			case 10: /* Enter, using KEY_ENTER fails in a highly mysterious way. */
	
				/* This frees most of them, probably. */
				while (i >= 0) {
					free_item(item_list[i--]);
				}
				free_menu(the_menu);
				clear();
				//mvprintw(LINES - 4, 0, "Selected %d.", item_index(current_item(the_menu)));
				
				return item_index(current_item(the_menu));
		}
		//mvprintw(LINES - 5, 0, "Key pressed: %u", c);
		mvprintw(LINES - 3, 0, "Press enter to select %d.", item_index(current_item(the_menu)));
		refresh();
	}


	/* Something went very wrong! */
	return -1;

}
