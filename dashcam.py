from time import sleep
from gps import get_serial, get_location, Location,distance
from picamera import PiCamera
from datetime import datetime
import os
import threading
from subprocess import call
from core import setup_logging
import json

folder = "/home/pi/Documents/videos"
camera_name = "DashCam"
log = setup_logging(name="camera daemon",fileName="/home/pi/Documents/log/camdaemon.log")


def capture_ex(fun):
    """
        decorator to put try catch around a function call and print exception message
    """
    def wrapper(*args, **kwargs):
        try:
            return fun(*args,**kwargs)
        except Exception as ex:
            log.error("exception at {0} msg: {1}", fun, str(ex))
    return wrapper


def sorted_ls(path):
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime))

def convert(filename):
        mp4name = filename.replace("h264","mp4")
        call(["MP4Box","-add", filename, mp4name])
        return mp4name

class CleanerThread(threading.Thread):

        def __init__(self, filename):
                self.file = filename
                super(CleanerThread, self).__init__()

        @capture_ex
        def process_file(self):
                mp4name = convert(self.file)
                os.remove(self.file)
                log.info("Uploading to AWS : %s"  % mp4name)
                #os.remove(mp4name)
               

        @capture_ex        
        def run(self):
            self.process_file()
                

class DashCamThread(threading.Thread):

        def __init__(self,video_length, number_to_keep,state, folder,loc):
                self.loc = loc
                self.duration = video_length
                self.files_to_keep = number_to_keep
                self.cam = PiCamera()
                self.cam.hflip = True
                self.cam.vflip = True
                self.cam.annotate_text_size = int(12)

                self.state = state
                self.folder = folder
                super(DashCamThread,self).__init__()

        def get_file_name(self):
                timestamp = lambda : datetime.now().strftime("%Y%m%d_%H%M%s")
                
                while True:
                        
                        if self.state["Mode"] == 'dashcam':
                                filename =  str.format("{0}_{1}.h264", camera_name, timestamp())
                                yield os.path.join(self.folder, filename)
                        else:
                                yield None
                        sleep(0.1)
                        
        @capture_ex        
        def run(self):
                try:
                        for filename in self.get_file_name():
                                if filename:
                                        log.info("recording %s " % filename)
                                        self.state["current_file"] = filename
                                        self.cam.start_recording(filename)
                                        start = datetime.now()
                                        while (datetime.now() - start).seconds < self.duration:
                                            loc = get_location(ser) 
                                            if loc.lat != 0: 
                                                self.cam.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + str.format(" ({0},{1}:{2})",loc.lat,loc.lng,speed_mph)
                                            else:    
                                                self.cam.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
                                            self.cam.wait_recording(0.1)

                                        self.cam.stop_recording()
                                        cleaner = CleanerThread(filename)
                                        cleaner.start()
                except Exception as ex:
                        log.error(ex)
                                
                

        
        
if __name__ == '__main__':
       
        log.info("starting camera daemone")



        log.info("LED Setup")

        camstate = {"Mode":"dashcam","current_file":"None"}
        
        camthread = DashCamThread(60, 1,camstate, folder)
      
        log.info("Starting main threads")

        camthread.start()
 
      
 
     

                
      

        
        

