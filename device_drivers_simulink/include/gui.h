/**
 * @file		gui.h
 *
 * @brief       Header for GPT GUI device driver package.
 */

#ifndef _GUI_H_
#define _GUI_H_
#include "rtwtypes.h"

#define SERVER_TCP_IP "127.0.0.1" /* Server (storage management device) IP address */
#define CLIENT_TCP_IP "127.0.0.1" /* Client (RedPitaya) IP address */
#define TCP_PORT 25000            /* Any available port for TCP socket communication */
#define TCP_BACKLOG 10            /* Maximum length for the queue of pending connections */
#define TCP_BUFFER_SIZE 1024      /* Maximum buffer size (in bytes) for socket send */

void connect_to_server(void);
void send_socket_data(
                        real_T t,
                        real_T V1,
                        real_T V2,
                        real_T V3,
                        real_T I1,
                        real_T I2,
                        real_T I3,
                        real_T f0_V1,
                        real_T f0_V2,
                        real_T f0_V3,
                        real_T f0_I1,
                        real_T f0_I2,
                        real_T f0_I3
                     );
real_T read_socket_data(void);
void close_socket(void);

#endif /* _GUI_H */