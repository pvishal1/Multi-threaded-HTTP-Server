import socket
import sys
import os
import mimetypes
import locale, datetime
import thread
import threading

lock = threading.Lock()
shared_dict = {}

def main():
    if(os.path.isdir(os.getcwd() + "/www")):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 0))
            s.listen(1)
            port = int(s.getsockname()[1])

            print("###########################################Port: ",port, socket.gethostname());
            while True:
                clientsocket, clientaddress = s.accept();
                thread.start_new_thread(client_exec, (clientsocket, clientaddress,))

        except socket.error:
            print("Failed to connect/bind")
            sys.exit();
        except KeyboardInterrupt:
            print("\nKeyBoardInterrupt found...Quitting")
        finally:
            s.close();

    else:
        print("www folder not found");


def client_exec(clientsocket, clientaddress):

    data = clientsocket.recv(1000);
    clientfilename = data.split()[1];

    if(clientfilename == '/') :
        clientfilename = '/error.txt'


    fName = os.getcwd() + '/www'+clientfilename;

    if (os.path.isfile(fName)):
        def add_dict(clientfilename):
            lock.acquire()
            try:
                if not clientfilename in shared_dict:
                    shared_dict[clientfilename] = 1
                else:
                    value = shared_dict[clientfilename]
                    shared_dict[clientfilename] = value+1
            finally:
                lock.release()

        response_body_raw = ""
        file_type, file_encoding = mimetypes.guess_type(fName, True);

        if (file_type == None):
            file_type = 'application/octet-stream'


        f = open(fName, "r")
        response_body_raw = f.read()

        #locale.setlocale(locale.LC_TIME, 'en_US')
        current_date = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        file_modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(fName)).strftime('%a, %d %b %Y %H:%M:%S GMT')

        response_headers_raw = 'HTTP/1.1 200 OK\nDate: '+str(current_date)+'\nServer: Apache/2.2.16 (Debian)\nLast-Modified: '+str(file_modified_date)+\
                               '\nContent-Length: '+str(os.path.getsize(fName))+'\nContent-Type: '+file_type+'\n\n'

        response_headers_raw = response_headers_raw + response_body_raw;

    else:
        response_headers_raw = "HTTP/1.0 404 ERR"+\
                            "\nServer: Apache/2.2.16 (Debian)\nContent-Length: 13\nContent-Type: text/plain\n\n"+\
                            "404 Not Found"

    try:
        add_dict(clientfilename)
    except:
        print("")
    clientsocket.send(response_headers_raw)

    clientsocket.close();

    for item in shared_dict:
        print (str(item)+'|'+str(clientaddress[0])+'|'+str(clientaddress[1])+'|'+str(shared_dict[item]))


if __name__ == '__main__':
    main()
    sys.exit(0)
