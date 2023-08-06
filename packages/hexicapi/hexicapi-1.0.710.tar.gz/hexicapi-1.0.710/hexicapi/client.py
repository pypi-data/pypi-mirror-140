import socket
import traceback
from hexicapi.socketMessage import *
from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
BUFFER_SIZE = 1024

ip = "localhost"
port = 81
debug = False

functions={ # print(list(functions)) - > shows all available functions
    'connecting':None,
    'connection_fail':None,
    'connection_success':None,
    'authenticating':None,
    'authentication_fail':None,
    'authentication_success':None,
    'handshake':None,
    'disconnect':None,
    'heartbeat':None,
    'heartbeat_error':None
}
def on_calf(f):
    functions[f.__name__] = f

def calf(name):
    f = functions[name]
    if f != None:
        if type(f) == list:
            f[0](f[1])
        else:
            f()

def disconnect_socket(s):
    try:
        send_all(s, 'bye'.encode())
    except:
        pass
    s.close()

def run(app,username,password='',autoauth=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    calf('connecting')
    try:
        s.connect((ip,port))
    except:
        calf('connection_fail')
        return
    calf('connection_success')
    send_all(s, "clientGetID".encode("utf-8"))
    id = recv_all(s, BUFFER_SIZE).decode("utf-8")
    calf('handshake')
    if autoauth:
        calf('authenticating')
        try:
            send_all(s, str('auth:' + username + ':' + password + ':' + app).encode())
            auth_result = recv_all(s, BUFFER_SIZE).decode('utf-8')
        except:
            calf('disconnect')
        if auth_result == 'auth-declined' or auth_result == 'guest-declined':
            calf('authentication_fail')
        else:
            calf('authentication_success')
    class Client:
        info = {
            'ip':ip,
            'port':port,
            'socket':s,
            'id':id,
            'username':username,
            'app':app
        }
        def heartbeat(self):
            try:
                send_all(self.info['socket'], "clientGetID".encode("utf-8"))
                id = recv_all(self.info['socket'], BUFFER_SIZE).decode("utf-8")
            except:
                id=''
            if id == self.info['id']:
                calf('heartbeat')
            else:
                calf('heartbeat_error')
            return id
        def disconnect(self):
            disconnect_socket(self.info['socket'])
            calf('disconnect')
        def send(self, message):
            try:
                _ = message.decode()
                try:
                    send_all(self.info['socket'], message)
                except Exception as e:
                    print(e)
                    return False
            except:
                try:
                    send_all(self.info['socket'], message.encode())
                except Exception:
                    if debug:
                        print(traceback.format_exc())
                    try:
                        send_all(self.info['socket'], message)
                    except Exception:
                        if debug:
                            print(traceback.format_exc())
                        return False
            return True
        def receive(self, packet_size = BUFFER_SIZE):
            try:
                m = recv_all(self.info['socket'], packet_size)
            except Exception:
                if debug:
                    print(traceback.format_exc())
                return False
            try:
                return m.decode("utf-8")
            except Exception:
                if debug:
                    print(traceback.format_exc())
                return m
        def auth(self, app, username, password=''):
            calf('authenticating')
            auth_result = 'auth-declined'
            try:
                send_all(s, str('auth:' + username + ':' + password + ':' + app).encode())
                auth_result = recv_all(s, BUFFER_SIZE).decode('utf-8')
            except:
                calf('disconnect')
            if auth_result == 'auth-declined' or auth_result == 'guest-declined':
                calf('authentication_fail')
            else:
                calf('authentication_success')
    return Client()
