'''
Helper class to update lamp firmware

NB !!!
update uses GitPython
Make sure you install GitPython to use update
1. Open System Shell in Thonny - Tools->Open System Shell
2. use command  - pip install GitPython

Usage -
1. import update
2. create update object (parameter should be lamp authentication password, default is 'dsputnik')
3. use 'object_name'.update() to update all firmware (opens a filedialog where you must select the folder that contains the firmware)
4. use 'object_name'.files() to update specific firmware files (opens a filedialog where you must select the files you with tu upload)
5. use 'object_name'.restart() to reset the lamp and apply the new firmware
6. use 'object_name'.cancel() to cancel an ongoing upload on lamp
7. use 'object_name'.authenticate() to reauthenticate lamps

All functions accept tags parameter to use the command with a specific lamp

To update prior v1.2 rewriter

1. import update
2. u = update.update()
3. u.lamps.update_rewriter('lamp_tag') #lamp tag as in "Apollo0001"
# make sure you are in the correct wifi after reboot
5. u = update.update()
4. u.update()
'''

import os
import asyncio
import DSDMpy
from tkinter import Tk, filedialog
from git import Repo

class update:
    '''Update object, use this to update lamps'''
    
    def __init__(self, pw='dsputnik'):
        self.lamps = DSDMpy.DSDMpy()
        self.lamps.authenticate(pw)
        self.loop = asyncio.get_event_loop()
        self.updating = False
    
    def authenticate(self, pw='dsputnik'):
        '''Method to reauthenticate lamps should the initial authentication not work'''
        self.lamps.authenticate(pw)
        
    def update(self, tag):
        '''
        Opens filedialog to pick a directory where the lamp firmware is stored
        When selection is made, all .py files in folder are uploaded to lamp
        '''
        if not self.updating and isinstance(tag, str):
            self.updating = True
            self.loop.run_until_complete(self._update_all_async(tag))
    
    def files(self, tag):
        '''
        Opens filedialog to pick a .py firmware files
        When selection is made, all selected files are uploaded to lamp
        '''
        if not self.updating and isinstance(tag, str):
            self.updating = True
            self.loop.run_until_complete(self._update_files_async(tag))
    
    def cancel(self, tag):
        '''Cancels current upload'''
        if self.updating and isinstance(tag, str):
            self.lamps.send_command("import rewriter\nrewriter.cancel()", tags=[tag])
    
    def restart(self, tag):
        '''Restarts lamps to apply new firmware'''
        if not self.updating and isinstance(tag, str):
            self.lamps.send_command("import machine\nmachine.reset()", tags=[tag])

    async def _update_all_async(self, tags):
        '''Internal update function, do not use manually'''
        root = Tk() # pointing root to Tk() to use it as Tk() in program.
        root.withdraw() # Hides small tkinter window.
        root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
        soft_folder = filedialog.askdirectory() # Returns directory path

        obj = os.scandir(soft_folder) # Scans all folders and files in chosen directory
    
        repo = Repo(soft_folder)
    
        for entry in obj:
            if entry.is_file() and entry.path.endswith('.py'): # Check if file is .py file
                self.lamps.send_file(entry.path, tags, entry.name, True) # Send file using DSDMpy
                while self.lamps.all_sent is False: # Wait until file is sent
                    await asyncio.sleep(1) # Sleep while waiting
                await asyncio.sleep(0.2) # Sleep to make sure all processes are finished
    
        repo_hash_updated = False
        
        def repo_hash_callback(device_id, data):
            nonlocal repo_hash_updated
            repo_hash_updated = True
            print("Lamp repo hash updated")
        
        while (repo_hash_updated == False):
            self.lamps.send_command("rewriter.update_repo_hash('" + repo.head.object.hexsha + "')", [tags], repo_hash_callback)
            await asyncio.sleep(0.3)
    
        self.updating = False
        print("Lamp Updated")
    
    async def _update_files_async(self, tag):
        '''Internal update function, do not use manually'''
        root = Tk() # pointing root to Tk() to use it as Tk() in program.
        root.withdraw() # Hides small tkinter window.
        root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
        files = filedialog.askopenfiles() # Returns selected filepaths
        
        for file in files:
            if os.path.basename(file.name).endswith('.py'): # Check if file is .py file
                self.lamps.send_file(file.name, tag, os.path.basename(file.name)) # Send file using DSDMpy
                while self.lamps.all_sent is False: # Wait until file is sent
                    await asyncio.sleep(1) # Sleep while waiting
                await asyncio.sleep(0.2) # Sleep to make sure all processes are finished
    
        self.updating = False
        print("Lamp Updated")