- WSGI定义以及异步(https://bottlepy.org/docs/dev/async.html)


         Briefly worded, the WSGI specification (pep 3333) defines a request/response circle as follows: The application callable is invoked once for each request and must return a body iterator. The server then iterates over the body and writes each chunk to the socket. As soon as the body iterator is exhausted, the client connection is closed.