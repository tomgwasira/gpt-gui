/**************************************************************************
 * @file		tcp_client.c
 *  
 * @copyright	Copyright (C) 2022 MLT (Pty) Ltd.
 * 
 * @brief	 	TCP/IP client implementation.
 *
 * @detail      This is an implementation of routines that will be called
 *              by Simulink device driver blocks in order to communicate
 *              with a TCP/IP server running (a GUI program) on localhost.
 * 
 * @author		Thomas Gwasira
 * @date		2022
 * 
 * @bug			No known bugs
 *
 *************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "gui.h"

#define BUFFER_LEN 13
#define BUFFER_SIZE BUFFER_LEN * 8

int socket_desc; /* socket descriptor for opened socket communication with server */
boolean_T connected_to_server; /* flag for determining whether program is connected to server */

/**
 * Connect to TCP/IP live server if not already connected.
 */
void connect_to_server(void)
{
    /* Only try to connect to server if not already connected */
	if (!connected_to_server)
    {
        struct sockaddr_in server; /* Server socket parameters */
    
	    /* Create socket and get socket descriptor */
	    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    
	    if (socket_desc < 0)
	    {
		    fprintf(stderr, "Could not create socket\n");
		    exit(EXIT_FAILURE);
	    }
    
	    /* Specify parameters for server socket */
	    server.sin_addr.s_addr = inet_addr("127.0.0.1"); /* local host IP address */
	    server.sin_family = AF_INET;
	    server.sin_port = htons(25000); /* TCP port */
    
	    /* Connect socket to server */
	    if (connect(socket_desc, (struct sockaddr *)&server, sizeof(server)) < 0)
	    {
		    fprintf(stderr, "Could not connect to server\n");
    
		    /* Close socket */
		    close(socket_desc);
		    printf("Socket closed successfully.\n");
    
		    exit(EXIT_FAILURE);
	    }

        /* Set flag to indicate connection to server */
        connected_to_server = 1;
    }
}

/**
 * Send data passed as arguments to TCP/IP server.
 *
 * @param debug Debug value.
 * @param V1 Instantaneous channel 1 voltage.
 * @param V2 Instantaneous channel 2 voltage.
 * @param V3 Instantaneous channel 3 voltage.
 * @param I1 Instantaneous channel 1 current.
 * @param I2 Instantaneous channel 2 current.
 * @param I3 Instantaneous channel 3 current.
 * @param f0_V1 Computed fundamental frequency of channel 1 voltage.
 * @param f0_V2 Computed fundamental frequency of channel 2 voltage.
 * @param f0_V3 Computed fundamental frequency of channel 3 voltage.
 * @param f0_I1 Computed fundamental frequency of channel 1 current.
 * @param f0_I2 Computed fundamental frequency of channel 2 current.
 * @param f0_I3 Computed fundamental frequency of channel 3 current.
 */
void send_socket_data(
                        real_T debug,
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
                     )
{
	int buffer_size = BUFFER_SIZE;
    real_T buffer[BUFFER_LEN] = {
                                    debug,
                                    V1,
                                    V2,
                                    V3,
                                    I1,
                                    I2,
                                    I3,
                                    f0_V1,
                                    f0_V2,
                                    f0_V3,
                                    f0_I1,
                                    f0_I2,
                                    f0_I3
                                 };

	unsigned char *buffer_ptr = (unsigned char *)buffer;
	int sent_size;

	/* Send data to server */
	while (buffer_size > 0)
	{
		if ((sent_size = send(socket_desc, buffer, buffer_size, 0)) < 0)
		{
			fprintf(stderr, "Send failed.\n");

			/* Close socket */
			close(socket_desc);
			printf("Socket closed successfully.\n");

			exit(EXIT_FAILURE);
		}

		buffer_ptr += sent_size;
		buffer_size -= sent_size;
	}
}

/**
 * Read single double value from TCP/IP receive buffer.
 *
 * @returns Double value read from TCP/IP receive buffer.
 */
real_T read_socket_data(void) {
    void *buffer;
    int_T read_size;
    real_T value;

    /* Allocate memory for one double value */
    /* Consider setting this up and cleaning it up in global scope for
       better performance */
    buffer = malloc(8);
    
    /* Blocking recv, so make sure server is sending data which doesn't
       depend on Simulink blocks */
    read_size = recv(socket_desc, buffer, 8, 0);
    /* read_size = recv(socket_desc, buffer, 8, MSG_DONTWAIT); - for non-blocking*/

    /* Get value from buffer memory before cleaning it up */
    value = *((real_T *)buffer);

    /* Clean up buffer memory */
    free(buffer);

    return value;
}

/**
 * Close TCP/IP socket communication.
 */
void close_socket(void)
{
	/* Close socket */
	close(socket_desc);
}