"""
Defines a logging handler for logging to a pcas logd server.
"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import grpc
import logging
import os

from ._logd_pb2_grpc import LoggerStub
from ._logd_pb2 import Message
from .exceptions import HandlerClosedError
from .. import PCAS_ROOT_CERTIFICATE

class LogHandler(logging.Handler):
    """
    A handler class which writes logging records to a PCAS log server.
    
    Logging to this handler blocks if the logger is unavailable. Use AsyncHandler
    for non-blocking logging to a pcas logd server. The caller should call the 
    close method of the returned handler once logging is finished, otherwise 
    resources may leak.

    Args:
        address: The address of the PCAS logd server.
        certificate: The SSL certificate.

    If the address parameter is None, its value will be read from the environment
    variable "PCAS_LOG_ADDRESS". If the certificate is None, its value will be read
    from the environment variable "PCAS_SSL_CERT".

    The name of the log to write to is specified by the name of the logger.Logger 
    that this is handling.
    """

    def __init__(self, address=None, certificate=None):
        # Initialise the underlying handler
        logging.Handler.__init__(self)
        # Populate the address and certificate, unless they were passed to us
        if address is None:
            address = os.environ.get("PCAS_LOG_ADDRESS", "")
        if certificate is None:
            certificate = os.environ.get("PCAS_SSL_CERT", "").strip().encode() + b'\n'
        # We trust any certificate signed by the PCAS root signing key
        certificate = certificate + PCAS_ROOT_CERTIFICATE
        # Create the gRPC channel
        creds = grpc.ssl_channel_credentials(root_certificates=certificate)
        channel = grpc.secure_channel(address, creds)
        self._channel = channel
        # Create the logger
        self._is_closed = False
        self.stub = LoggerStub(channel)

    def __del__(self):
        """Close the handler when it is garbage collected."""
        self.close()
        
    def close(self):
        """Close the handler."""
        if not self._is_closed:
            self._is_closed = True
            self._channel.close()

    def emit(self, record):
        """
        Emit a record. 

        Returns: None

        Raises:
            HandlerClosedError: if the handler is closed
        
        """
        if self._is_closed:
            raise HandlerClosedError
        msg = Message(
            identifier='pcas-python-interface', 
            log_name=record.name, 
            log_message=self.format(record),
            )
        self.stub.LogMessage.with_call(msg)

# class AsyncHandler(QueueHandler):
#     """
#     A handler class which writes logging records to a PCAS log server.
    
#     Logging to this handler does not block if the logger is unavailable. In this
#     situation log messages may be silently discarded. The caller should call the 
#     close method of the returned handler once logging is finished, otherwise
#     resources may leak.

#     Args:
#         address: The address of the PCAS logd server.
#         certificate: The SSL certificate.

#     If the address parameter is None, its value will be read from the environment
#     variable "PCAS_LOG_ADDRESS". If the certificate is None, its value will be read
#     from the environment variable "PCAS_SSL_CERT".

#     The name of the log to write to is specified by the name of the logger.Logger 
#     that this is handling.

#     """

#     def __init__(self, address=None, certificate=None):
#         # Create the synchronous handler
#         self._lh = LogHandler(address=address, certificate=certificate)
#         # Create the queue
#         self._q = multiprocessing.Queue(-1)
#         # Start the listener
#         self._ql = QueueListener(self._q, self._lh)
#         self._ql.start()
#         # Initialise the underlying queue handler
#         super().__init__(self._q)

#     def close(self):
#         """Close the handler."""
#         self._ql.stop()
#         self._q.close()
#         self._lh.close()
#         del self._ql
#         del self._q
