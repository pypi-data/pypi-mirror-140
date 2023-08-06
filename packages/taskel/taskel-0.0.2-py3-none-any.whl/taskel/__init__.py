from threading import Thread
import time
import random


def run(t):
  t.start()

class utils:
  def gettime():
    current = time.asctime( time.localtime(time.time()))
    current = current.split()
    current = current[3]
    current = current.replace(":"," ")
    current = current.split()
    hours = current[0]
    minutes = current[1]
    sec = current[2]
    return current

  def getsecs():
    current = utils.gettime()
    hours = current[0]
    minutes = current[1]
    sec = current[2]
    sec = int(sec)
    e = int(hours)*360
    sec += int(e)
    f = int(minutes)*60

    sec += int(f)
    return sec

  def roundcd(seconds):
    sec = utils.getsecs()
    if int(sec) > int(seconds):
      return
    sec = int(seconds) - int(sec)
    if sec < 60:
      return {"value":round(sec),"type":"seconds"}
    if sec < 360:
      return {"value":round(sec/60),"type":"minutes"}
    if sec < 21600:
      return {"value":round(sec/360),"type":"hours"}
    if sec < 86400:
      return {"value":round(sec/21600),"type":"days"}

def runtask(t):

  t.start()



class handler:
  def __init__(self,target,args,name,daemonz):
    self.args = 0
    if len(args) > 1:
      locel = {}
      st = "("
      for item in args:
        st += f"'{item}'" + ","
      st += ")"
    
      
      exec(f"ll = {st}",{},locel)
      self.args = locel["ll"]
    elif len(args) == 0:
      self.args = ()
    else:
      self.args = (args[0],)
    self.name = name
    self.target = target
    self.looptime = 0
    self.rn = 0
    self.exit = False
    self.running = False
    self.rn = False
    self.next = 0
    self.obj = None
    self.norm = False
    self.looping = False
    self.daemon = daemonz

  def force(self,tf):
    if tf == "stop":
      try:
        self.obj.join()
      except:
        self.exit = True
        if self.norm == True:
          self.obj.join()
        
  def stop(self):
    
    if self.rn == False:
      self.exit = True
      print(f"{self.name}: Terminated")
      
    else:
      def endtask(self,t):
        
        while self.rn == True:
          ok = "frenchbaby seal"
        self.exit = True
        if self.norm == True:
          self.obj.join()
    
      t = Thread(target=endtask,args=(self,self.obj,),daemon = False)
      t.start()
      print(f"{self.name}: Terminated")
      
    
      
  def loop(self,sec=0,min=0,hr=0):
    if self.norm == True:
      return print(f"{self.name} already started, cannot loop")
    smin = min*60
    shr = hr*3600
    sec += smin
    sec += shr
    
    if self.daemon == "0":
      self.daemon = True
    self.looping = True
    self.looptime = sec
    self.rn = utils.getsecs()
    self.running = True
    self.next = self.rn + self.looptime
    self.obj = Thread(target=self.target,args=self.args,daemon = self.daemon)
    runtask(self.obj)
    self.obj = Thread(target=self.target,args=self.args,daemon = self.daemon)
    def looptask(self):
      while self.exit != True:
        time = utils.getsecs()
        if time == self.next:
          self.rn = True
          
          runtask(self.obj)
          self.obj = Thread(target=self.target,args=self.args,daemon = self.daemon)
          self.rn = False
          
          self.next += self.looptime
    lt = Thread(target=looptask,args=(self,),daemon = self.daemon)
    lt.start()
    
  def start(self):
    if self.looping == True:
      return print(f"{self.name} already looped, cannot start")
    if self.daemon == "0":
      self.daemon = False
      self.obj = Thread(target=self.target,args=self.args,daemon = self.daemon)
      self.rn = True
      runtask(self.obj)
      self.rn = False

    
    
    
    

class Tasks:
  def __init__(self):
    self.tasklist = []

  def create(self,target,args=(),name="Task",daemon="0"):
    
    if name in self.tasklist:
      namez = name
      while namez in self.tasklist:
        namez = ""
        num = random.randint(1,1000)
        namez = name + " <" + str(num) + ">"
        self.tasklist.append(name)
    else:
      self.tasklist.append(name)
    t = handler(target=target,args=args,name=name,daemonz=daemon)
    return t
  def end(self,t,force=False):
    self.tasklist.remove(t.name)
    if force == False:
      t.stop()
    else:
      t.force("stop")
  def clone(self,t):
    return self.clones[t.name]