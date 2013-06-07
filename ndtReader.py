# -*- coding: utf-8 -*-

import struct
import os
import matplotlib
import numpy as np
class message():
    length=0
    location=0
    format = ''
    content = ''
    value = 0
    unit = ''
    valueDict = {}
    def __init__(self,location=-1,length=-1,format="",unit= '',valueDict={},value=0):
        self.length = length
        self.location = location
        self.format = format
        self.unit = unit
        self.valueDict = valueDict
        self.value = value
class ndtReader():
    '''
    超声F扫描ndt文件读取库
    TODO：解析其他标签
    
    '''
    def __init__(self):
        self.ndtFile=None
        self.filePath=''
        self.msgDict={}
        self.hdList=[]
        self.filePointer=0
        self.waveList=[]
        self.time_wave_dict={}
        self.index4channel={}
        self.timeOfStart="Time of start not found!"
        self.offset = 112
        self.width = -1
        self.height = -1
        #message define: name , location ,length
        self.msgDict['dataWidth'] = message(22,2,'H')
        self.msgDict['pixelWidth'] = message(22,2,'H')
        self.msgDict['pixelHeight'] = message(24,2,'H')
        self.msgDict['waveformLength'] = message(value = 564*2)
        self.msgDict['Waveform']=message(-1,564*2,"")
        
    def open(self,path):
        self.filePath=path
        self.ndtFile=open(self.filePath,'rb')
        f=self.ndtFile
        self.fileSize = os.path.getsize(self.filePath)
        print('file size:{0}'.format(self.fileSize))
        for name,msg in self.msgDict.items():
            try:
                if struct.calcsize(msg.format) != msg.length:
                    print('format error:{0}'.format(name))
                    continue
                f.seek(msg.location)
                msg.content = f.read(msg.length)
                #print("{0}:{1}".format(name,msg.content))
                msg.value, =  struct.unpack(msg.format,msg.content)
                if msg.valueDict.has_key(msg.value):
                    msg.value = msg.valueDict[msg.value]
                print("{0}:{1} {2}".format(name,msg.value,msg.unit))
            except:
                print('error:{0}'.format(name))
                continue
        self.width = self.msgDict['pixelWidth'].value
        self.height = self.msgDict['pixelHeight'].value
        #read the image
        f.seek(self.offset,0)
        str = f.read( self.width* self.height *4)
        count = self.width* self.height 
        data = np.array(struct.unpack('>{0}I'.format(count),str))
        self.image = data.reshape(self.height,-1)
        print self.image.shape
        
        self.msgDict['Waveform'].location = self.offset + self.width* self.height *4 + self.width *4
        self.msgDict['waveformLength'].value = int((self.fileSize -self.msgDict['Waveform'].location) / (self.width*self.height) +0.5)
        self.msgDict['Waveform'].length = self.msgDict['waveformLength'].value*2
        print 'waveform location',self.msgDict['Waveform'].location
        print 'waveform length',self.msgDict['waveformLength'].value
        print 'Analysis Done!Message count:',len(self.msgDict)

    def getWaveform(self,(x,y)):
        x = int(x)
        y = int(y)
        p = int(self.msgDict['Waveform'].location + (y * self.msgDict['dataWidth'].value +x)*self.msgDict['waveformLength'].value)
        f=self.ndtFile
        #print x,y,p
        #print p,os.fstat(f.fileno()).st_size
        try:
            f.seek(p,0)
            str = f.read(self.msgDict['Waveform'].length)
            #print len(str)
            count = self.msgDict['Waveform'].length//2
            wave = struct.unpack('>{0}H'.format(count),str)
            return wave[:len(wave)//2]
        except:
            return None
if (__name__=='__main__'):
    ndt=ndtReader()
    ndt.open("./ndt1.ndt")
    print ndt.getWaveform((0,0))[:10]
