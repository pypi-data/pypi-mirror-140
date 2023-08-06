'''
Library to communicate over wifi using Artnet/Artnet-Repl

NB !!!
update uses GitPython
Make sure you install GitPython to use update
1. Open System Shell in Thonny - Tools->Open System Shell
2. use command  - pip install GitPython

An example to assing all lamp's tags to a variable and print them out using DSDMpy -

import DSDMpy module by writing thew following into the console
import DSDMpy
next create an object using the following line

d = DSDMpy.DSDMpy()

paste these functions starting with parse_list() into the console for use as a callback

def parse_list(string):
    try:
        s = eval(string)
        if type(s) == list:
            return s
    except:
        pass

def print_out(device_id, str_in):
    tags_list = parse_list(str_in)
    print(device_id + " has tags ")
    for tag in tags_list:
        print(tag + " - ")
        
now make sure you are connected to the lamps you with to receive tags from
and send the following commands

d.send_command([], "import tags")
d.send_command([], "print(tags.get_all_tags())", print_out)

'''

import socket
import _thread
import time
import uuid
import hashlib, binascii
from git import Repo
import os

class DSDMpy:
    
    def __init__(self, reply = True):
        self.ip = '255.255.255.255'
        self.port = 6454
        
        self.lamp_rewriter_versions = {} # Dict of lamps and their rewriter versions {(lamp_name, rewriter_ver), ..}
        
        self.AP = 0
        self.CLIENT = 1
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
        if reply:
            self.callbacks = []
            _thread.start_new_thread(self.udp_reader_loop,())
        
    def udp_reader_loop(self):
        '''loop that manages incoming packets'''
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if len(data) > 0:
                    incoming_data = self.parse_tuple(data.decode())
                    device_id = incoming_data[0]
                    identifier = incoming_data[1]
                    result = incoming_data[2]
                    for callback in self.callbacks:
                        if callback[0] == identifier:
                            if callback[1] is not None:
                                callback[1](device_id, result.decode())
                            else:
                                print(device_id + " - " + result.decode())
                time.sleep(0.1)
            except Exception as e:
                time.sleep(0.1) 

    def detect(self):
        '''Function that prints existing lamps in network'''
        self.send_command("print('here')")

    def authenticate(self, password, tags=[]):
        '''Function to authenticate lamp rewriter'''
        self.lamp_rewriter_versions = {}  # Resetting checked lamp rewriter version due to a new authentication
        self.send_command("import rewriter", tags)
        self.send_command("rewriter.auth('" + password + "')", tags)
    
    def verify_rewriter_version(self, tag):
        '''Function that checks lamp rewriter version, used internally'''
        if isinstance(tag, str):
            self.send_command("import rewriter", [tag])
            self.send_command("print(rewriter.version)", [tag], self.rewriter_version_callback) # Callback automatically updates the rewriter ver list on line 48
        else:
            print("Incorrect tag format")
        
    def update_rewriter(self, tag):
        '''Function that updates a specific lamps rewriter version to support byte arrays as incoming data'''
        if isinstance(tag, str):
            print("Updating rewriter")
            self.send_file_as_string("Extras/rewriter.py", tag, "rewriter.py")
            print("Restarting lamp")
            self.send_command("import machine", [tag])
            self.send_command("machine.reset()", [tag])
        else:
            print("Incorrect tag format")
        
    def send_file(self, local_file_path, tag, remote_file_path=None, clean_upload=False):
        '''
        Use this function to send files to a specific lamp
        This function checks the lamps rewriter version to send the file in a supported format
        '''
        if isinstance(tag, str):
            while tag not in self.lamp_rewriter_versions:
                self.verify_rewriter_version(tag)
                time.sleep(0.5) # Sleep to not clutter network with too many verification packets
        
            if self.lamp_rewriter_versions[tag] == 1.1: # ByteArray format is supported from version 1.1
                print("Sending byte")
                self.send_file_as_byte(local_file_path, tag, remote_file_path)
            elif self.lamp_rewriter_versions[tag] == 1.2: # Hashing is supported from version 1.2
                print("Sending byte with hash")
                self.send_file_as_byte(local_file_path, tag, remote_file_path, True)
            elif self.lamp_rewriter_versions[tag] >= 1.3: # Git Hashes supported from version 1.3
                if clean_upload:
                    print("Sending byte with hash and repo check")
                    self.send_file_as_byte(local_file_path, tag, remote_file_path, True, True)
                else:
                    print("Sending byte with hash and repo check (not clean upload)")
                    self.send_file_as_byte(local_file_path, tag, remote_file_path, True)
            else:
                print("Sending string")
                self.send_file_as_string(local_file_path, tag, remote_file_path)
        else:
            print("Incorrect tag format")
    
    def send_file_as_byte(self, local_file_path, tag, remote_file_path=None, hash_file = False, check_file_dirty=False):
        '''
        Use this function to manually send a file to a lamp using bytearray format
        '''
        if isinstance(tag, str):
            if remote_file_path == None:
                remote_file_path = local_file_path
        
            file_hash = None
            
            if hash_file:
                file_hash = self._hash_file(local_file_path)
            
            is_dirty = False
            
            if check_file_dirty == True:
                repo = Repo(os.path.dirname(local_file_path), search_parent_directories=True)
                
                file_names = []
        
                for item in repo.index.diff(None):
                    file_names.append(item.a_path)
        
                if os.path.basename(local_file_path) in file_names:
                    is_dirty = True
            else:
                is_dirty = True
                
            f = open(local_file_path, "rb")
        
            data = []
        
            while True:
                buf = f.read(512) # File is sent in 512 bytearray bundles
                if not buf:
                    break
                data.append(buf)
        
            print("Sending file: " + local_file_path + ", in " + str(len(data)) + " parts")
            self._send_file_internal(remote_file_path, data, True, tag, file_hash, is_dirty)
        else:
            print("Incorrect tag format")
            
    def send_file_as_string(self, local_file_path, tag, remote_file_path=None):
        '''
        Use this function to manually send a file to a lamp using string (slower and more prone to errors) format
        Use only when byte cannot be used. Otherwise prefer Byte file sending.
        '''
        if isinstance(tag, str):
            if remote_file_path == None:
                remote_file_path = local_file_path
        
            f = open(local_file_path)
            lines = f.readlines() # File is sent line by line
        
            data = []
        
            for line in lines:
                line_newline_fix = line.replace("\n", "\\n") # Filtering to avoid some newline errors
                data.append(line_newline_fix.replace("'", "\\'")) # Filtering to avoid some newline errors
        
            print("Sending file: " + local_file_path + ", in " + str(len(data)) + " parts")
            self._send_file_internal(remote_file_path, data, False, tag)
        else:
            print("Incorrect tag format")
            
    def _send_file_internal(self, remote_file_path, data, is_byte, tag, file_hash = None, is_dirty=True):
        '''
        Internal function that handles sending the file, checks for missing parts and resends them
        '''
        if isinstance(tag, str):
            self.missing_pieces = []
            self.all_sent = False # Bool for outside modules to check if file has been sent
            
            self.send_command("import rewriter", [tag])
            
            if file_hash is not None:
                file_checked = False
                send_file = True
                
                def hash_check_callback(device_id, data):
                    nonlocal send_file, file_checked
                    if "correct" in data:
                        send_file = False
                    file_checked = True
                
                while file_checked == False:
                    self.send_command("print(rewriter.check_file_hash('" + remote_file_path + "', '" + file_hash + "'))", [tag], hash_check_callback)
                    time.sleep(0.5)
                
                if send_file == False:
                    print("File already updated")
                    print("Checking Dirty Status")
                    git_modified = False
            
                    def git_callback(device_id, data):
                        nonlocal git_modified
                        git_modified = True
                        print("Dirty list updated")
            
                    while (git_modified == False):
                        if is_dirty:
                            self.send_command("rewriter.add_dirty_file('" + remote_file_path + "')", [tag], git_callback)
                        else:
                            self.send_command("rewriter.remove_dirty_file('" + remote_file_path + "')", [tag], git_callback)
                        time.sleep(0.3)
                    
                    self.all_sent = True
                    return 0
                
                self.send_command("rewriter.start_file_upload('" + remote_file_path + "'," + str(len(data)) + ", '" + file_hash + "')", [tag])
            else:
                self.send_command("rewriter.start_file_upload('" + remote_file_path + "'," + str(len(data)) + ")", [tag])
        
            for index, piece in enumerate(data):
                if is_byte:
                    payload = "rewriter.send_file_piece(" + str(index) + " ," + str(piece) + ", " + str(is_byte) + ")"
                else:
                    payload = "rewriter.send_file_piece(" + str(index) + " ,'" + str(piece) + "')"
                self.send_command(payload, [tag])
                time.sleep(0.1)
        
            while self.missing_pieces == (): # Ask for missing pieces
                self.send_command("print(rewriter.missing_pieces())", [tag], self.missing_pieces_callback)
                time.sleep(1)
            time.sleep(0.1)
        
            while self.missing_pieces != None: # Send and reask for missing pieces until there are none
                for index in self.missing_pieces:
                    if is_byte:
                        payload = "rewriter.send_file_piece(" + str(index) + " ," + str(data[index]) + ", " + str(is_byte) + ")"
                    else:
                        payload = "rewriter.send_file_piece(" + str(index) + " ,'" + str(data[index]) + "')"
                    self.send_command(payload, [tag])
                    time.sleep(0.3)
                self.send_command("print(rewriter.missing_pieces())", [tag], self.missing_pieces_callback)
                time.sleep(1)
            time.sleep(0.1)
            
            self.all_sent = True
        else:
            print("Incorrect tag format")
        
    def set_wifi(self, mode = 0, ssid=None, pw=None, tags = []):
        '''
        Function to set lamp to a specific wifi mode (CLIENT = 1/AP = 0)
        '''
        self.send_command("import wifi", tags)
        command = ""
        if mode == self.CLIENT:
            if ssid is not None:
                secure_pw = self.wpa_psk(ssid,pw)
                command = "wifi.change_network_mode(" + str(mode) + ", '" + ssid + "', '" + secure_pw.decode("utf-8") + "')"
            else:
                command = "wifi.change_network_mode(" + str(mode) + ")"
        else:
            command = "wifi.change_network_mode(" + str(mode) + ")"
        self.send_command(command, tags)
        print("Setting lamp to mode " + str(mode))
        
    # Test sync on lamp by first running prepare_sync_test() and then sync()
    # Lamps should turn on and off in one second interval
    # When connected to the lamp with usb, delay time is printed
    def sync(self):
        device_time = round(time.time() * 1000)
        self.send_command("import timesync")
        self.send_command("timesync.sync(" + str(device_time) + ")")
        
    def prepare_sync_test(self):
        with open('Extras/sync_test.txt', 'r') as file:
            data = file.read()
            self.send_command(data)
    
    def rewriter_version_callback(self, device_id, data):
        '''
        Callback to rewriter version check
        '''
        try:
            version = float(data)
            if version == 1.1:
                print("Its recommended to upgrade your lamps rewriter version to 1.2 to get hashing support")
            if version == 1.2:
                print("Its recommended to upgrade your lamps rewriter version to 1.3 to get git hash support")
        except:
            version = 1.0
            print("Current rewriter version on lamp " + device_id + " is outdated.")
            print("It is recommended to update your lamps rewriter using DSDMpy.update_rewriter('lampname')")
            print("This is to avoid issues with file parsing that exist in the previous rewriter version")
            
        self.lamp_rewriter_versions[device_id] = version
            
    def missing_pieces_callback(self, device_id, data):
        '''
        Callback to sent file missing pieces
        '''
        if data == "False":
            self.missing_pieces = None
        else:
            self.missing_pieces = self.parse_tuple(data)
            if self.missing_pieces == ():
                self.missing_pieces = None
        
    def send_command(self, command, tags=[], callback = None):
        '''
        Send command to lamps in tags parameter.
        Has optional callback functionality described in description
        '''
        header = self.generate_header(0x40)
        packet = bytearray()
        packet.extend(header)
        packet_uuid = str(uuid.uuid4())
        self.callbacks.append((packet_uuid, callback))
        packet_data = str((packet_uuid, tags, command)) 
        packet.extend(packet_data.encode())
        self.send_packet(packet)
        
    def send_color(self, color, channel = 0):
        '''
        Send a regular artnet color packet
        '''
        header = self.generate_header(0x50)
        packet = bytearray()
        packet.extend(header)
        
        for i in range(channel):
            for i in range(5):
                packet.append(0)
        
        packet.append(color[0])
        packet.append(color[1])
        packet.append(color[2])
        packet.append(color[3])
        
        if (len(color) == 5):
            packet.append(color[4])
        else:
            packet.append(0)
        
        self.send_packet(packet)
    
    def send_packet(self, packet):
        '''
        Internal function that handles packet sending
        '''
        try:
            self.sock.sendto(packet, (self.ip, self.port))
        except Exception as e:
            print("ERROR: Socket error with exception: %s" % e)
    
    def generate_header(self, op_code):
        '''
        Generates artnet packet header with correct op_code
        '''
        header = bytearray()
        header.extend(bytearray('Art-Net', 'utf8'))
        header.append(0x0)
        header.append(0x0)
        header.append(op_code)
        header.append(0x0)
        header.append(0x0)
        header.append(0x0)
        header.append(0x0)
        header.append(0x1) #Universe
        header.append(0x0)
        header.append(0x0) 
        header.append(0x0)
        return header
    
    def wpa_psk(self, ssid, password):
        '''
        Generates secure password for wifi connection
        '''
        dk = hashlib.pbkdf2_hmac('sha1', str.encode(password), str.encode(ssid), 4096, 32)
        return (binascii.hexlify(dk))

    def parse_tuple(self, string):
        '''
        Helper function that returns a tuple from a string in a tuple format
        '''
        try:
            s = eval(string)
            if type(s) == tuple:
                return s
            else:
                return None
        except:
            return None
    
    def parse_list(self, string):
        '''
        Helper function that returns a list from a string in a list format
        '''
        try:
            s = eval(string)
            if type(s) == list:
                return s
            else:
                return None
        except:
            pass
    
    def parse_dict(self, string):
        '''
        Helper function that returns a list from a string in a list format
        '''
        try:
            s = eval(string)
            if type(s) == dict:
                return s
            else:
                return None
        except:
            pass
        
    def _hash_file(self, file_in):
        """
        Hash a single file
        :param str filename with relative path
        :return str md5 hash
        """
        file_hash = hashlib.md5()
        with open(file_in,"r") as file:
            buffer = file.read()
            file_hash.update(buffer.encode())
            
        return file_hash.hexdigest()    