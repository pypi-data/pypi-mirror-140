import json
def readjson(file,mode="r"):
  d = open(str(file),str(mode))
  return json.load(d)
class use:
  def __init__(self,file,mode="r"):
    self.loc = file
    self.data = readjson(self.loc,"r")
  def getraw(self,mode="r"):
    return readjson(self.loc,"r")
  def write(self):
    d = self.data
    with open(self.loc,"w") as x:
      json.dump(d,x)
  def has(self,key,t,f):
    if key in self.data:
      t()
    else:
      f()
  def add(self,key,value):
    self.data[key] = value
    self.write()
    

  def get(self,key):
    return self.data[key]
  
    