#ifndef _rs_H_
#define _rs_H_

int start_session(ssh_session *session, char* remote_host);
int authenticate_pubkey(ssh_session *session);
int authenticate_pass(ssh_session *session);
int remote_vboxmanage(char* output, ssh_session *session, char* cmd);
int close_session(ssh_session *session);
int verify_knownhost(ssh_session *session);

#endif // _rs_H_
