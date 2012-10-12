#include <libssh/libssh.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <ncurses.h>

int start_session(ssh_session *session, char* remote_host);
int authenticate_pubkey(ssh_session *session);
int authenticate_pass(ssh_session *session);
int remote_vboxmanage(char* output, ssh_session *session, char* cmd);
int close_session(ssh_session *session);
int verify_knownhost(ssh_session *session);


int start_session(ssh_session *session, char* remote_host) {

	int verbosity = 0;
	//verbosity = SSH_LOG_PROTOCOL;
	//int port = 22;
	int rc;
	//char* password;

	*session = ssh_new();

	if (*session == NULL) {
		endwin(); //unfortunately needs to be here to keep the terminal from blowing up when the program exits.
		exit(-1);
	}

	ssh_options_set(*session, SSH_OPTIONS_HOST, remote_host);

	ssh_options_set(*session, SSH_OPTIONS_LOG_VERBOSITY, &verbosity);

	rc = ssh_connect(*session);
	if (rc != SSH_OK) {
		endwin(); //unfortunately needs to be here to keep the terminal from blowing up when the program exits.
		fprintf(stderr, "Error connecting to %s: %s\n", remote_host, ssh_get_error(session));
		exit(-1);
	}

	return 0;

}

int authenticate_pubkey(ssh_session *session) {
	int rc;

	rc = ssh_userauth_autopubkey(*session, NULL);

	if (rc == SSH_REQUEST_AUTH) {
		endwin(); //unfortunately needs to be here to keep the terminal from blowing up when the program exits.
		fprintf(stderr, "Authentication failed: %s\n\nYou must have a public key on the remote machine.\n\nUse ssh-copy-id or append the contents of the .pub file in ~/.ssh to the remote user's ~/.ssh/authorized_keys file.\n" , ssh_get_error(session));
		ssh_disconnect(*session);
		ssh_free(*session);
		exit(-1);
	}

	return rc;
}

int authenticate_pass(ssh_session *session) {
	char* password;
	int rc;

//	if (rc == SSH_REQUEST_AUTH) {
		password = getpass("Password: ");
		rc = ssh_userauth_password(*session, NULL, password);
		if (rc != SSH_AUTH_SUCCESS) {
			endwin(); //unfortunately needs to be here to keep the terminal from blowing up when the program exits.
			fprintf(stderr, "Error authenticating with password: %s\n", ssh_get_error(*session));
			ssh_disconnect(*session);
			ssh_free(*session);
			return -1;
		}
//	}

	return 0;

}

int remote_vboxmanage(char* output, ssh_session *session, char* cmd) {

	ssh_channel channel;
	int rc;

	char buffer[256];
	unsigned int nbytes;

	char c[256] = "vboxmanage ";
	strcat(c, cmd);

	channel = ssh_channel_new(*session);
	if (channel == NULL) 
		return SSH_ERROR;

	rc = ssh_channel_open_session(channel);
	if (rc != SSH_OK) {
		ssh_channel_free(channel);
		return rc;
	}

	rc = ssh_channel_request_exec(channel, c);

	if (rc != SSH_OK) {
		ssh_channel_close(channel);
		ssh_channel_free(channel);
		return rc;
	}

	// Copy the output into nbytes
	nbytes = ssh_channel_read(channel, buffer, sizeof(buffer), 0);
	
	while (nbytes > 0) {
		strncat(output, buffer, nbytes);
		nbytes = ssh_channel_read(channel, buffer, sizeof(buffer), 0);
	}

	if (nbytes < 0) {
		ssh_channel_close(channel);
		ssh_channel_free(channel);
		return SSH_ERROR;
	}

	ssh_channel_send_eof(channel);
	ssh_channel_close(channel);
	ssh_channel_free(channel);
	
	return SSH_OK;

}

int close_session(ssh_session *session) {

	ssh_disconnect(*session);
	ssh_free(*session);

	return 0;
}

int verify_knownhost(ssh_session *session) {

	int state, hlen;
	unsigned char *hash = NULL;
	char *hexa;
	char buf[10];

	state = ssh_is_server_known(*session);
	hlen = ssh_get_pubkey_hash(*session, &hash);

	if (hlen < 0)
		return -1;

	if (state == SSH_SERVER_NOT_KNOWN) {
		hexa = ssh_get_hexa(hash, hlen);
		fprintf(stderr,"The server is unknown. Do you trust the host key?\n");
		fprintf(stderr, "Public key hash: %s\n", hexa);
		if (fgets(buf, sizeof(buf), stdin) == NULL)
			return -1;
		if (strncasecmp(buf, "yes", 3) != 0)
			return -1;
		if (ssh_write_knownhost(*session) < 0) {
			fprintf(stderr, "Error %s\n", strerror(errno));
			return -1;
		}
	}

	else if (state < 0) {
		fprintf(stderr, "Something went wrong, the host could not be verified.\nError %d\n", state);
		return -1;
	}

	return 0;
}

