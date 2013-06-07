# -*- coding: cp936 -*-
import string
from matplotlib import pyplot as plt
import numpy as np
from scipy import *

class message():
    ID=0
    length=0
    location=0
class hitData():
    rtot=0
    channel=0
    riseTime=0 #2
    aeCount=0 #2
    energy=0 #2
    duration=0 #4
    amplitude=0 #1
class waveformData():
    subId=0
    tot=0
    channelNum=0
    alignNum=0
    N=0 #sample number
    dataPosition=0
    AEF=0
class dtaReader():
    def __init__(self):
        self.dtaFile=None
        self.filePath=''
        self.msgList=[]
        self.hdList=[]
        self.filePointer=0
        self.waveList=[]
        self.time_wave_dict={}
        self.index4channel={}
        self.timeOfStart="Time of start not found!"
        for i in range(1,9):
            self.index4channel['CH' +str(i)]=[]
    def open(self,path):
        self.filePath=path
        self.dtaFile=open(self.filePath,'rb')
    def analysis(self,showIDs=False,showDetail=False):
        endflag=False
        f=self.dtaFile
        f.seek(0)
        while(not endflag):
            newMsg=message()
            length=f.read(2)
            if(length==''):
                break
            newMsg.length=ord(length[0])+ord(length[1])*256
            id = ord(f.read(1))
            if(id in range(41,44)):
                id2=f.read(1)
                newMsg.length -=2
            else:
                newMsg.length -=1
            newMsg.ID=id
            newMsg.location=f.tell()
            if(showIDs):
                print 'Messages--> ID:',newMsg.ID,'length:',newMsg.length,'location:%d'%newMsg.location
            self.msgList.append(newMsg)
            self.handlingID(newMsg,showDetail)
            f.seek(newMsg.length+newMsg.location)
            #raw_input("type a directory name(eg: \"D:\\AE-Data-602\\exp10\")")
        print 'Analysis Done!Message count:',len(self.msgList)
    def handlingID(self,msg,isShow=False):
        if(msg.ID==1): #hit data
            hd=hitData()
            #print msg.length,msg.location
            self.dtaFile.seek(msg.location)
            d=self.dtaFile.read(msg.length)
            rtot=d[0:6]
            #bs=['%02x'%ord(bs[i]) for i in range(5,-1,-1) ]
            hd.rtot=self.str2num(rtot)*0.25/1000000  #int('0x'+''.join(bs),16)*0.25/1000000
            hd.channel=ord(d[6:7])
            assert hd.channel in range(1,9)
            d2=d[7:]
            hd.riseTime=self.str2num(d2[0:2])
            hd.aeCount=self.str2num(d2[2:4])
            hd.energy=self.str2num(d2[4:6])
            hd.duration = self.str2num(d2[6:10])
            hd.amplitude = ord(d2[10])
            if(isShow):
                print '\tHit--> channel:',hd.channel,hd.rtot,hd.riseTime,hd.aeCount,hd.energy,hd.duration,hd.amplitude #['%d'%ord(i) for i in d2]
            self.hdList.append(hd)
        elif(msg.ID==173):
            wf=waveformData()
            self.dtaFile.seek(msg.location)
            d=self.dtaFile.read(9)
            wf.subId=ord(d[0])
            wf.tot=self.str2num(d[1:7])*0.25/1000000
            wf.channelNum=ord(d[7])
            #wf.alignNum=ord(d[8])
            wf.N=msg.length-9 #self.str2num(d[8:9])
            if(isShow):
                print '\tWave-->time:',wf.tot,'channel:',wf.channelNum,'length:',wf.N
            wf.dataPosition=msg.location+9

            self.waveList.append(wf)
            self.index4channel['CH' +str(wf.channelNum)].append(len(self.waveList)-1)
            self.time_wave_dict[wf.tot]=wf
        elif(msg.ID==99):
            self.dtaFile.seek(msg.location)
            d=self.dtaFile.read(msg.length)
            self.timeOfStart=d
            if(isShow):
                print '\tTime of start:',self.timeOfStart
        elif(msg.ID==5):
            self.dtaFile.seek(msg.location)
            d=self.dtaFile.read(msg.length)


    def str2num(self,st):
        bs=['%02x'%ord(st[i]) for i in range(len(st)-1,-1,-1) ]
        return int('0x'+''.join(bs),16)
    def getIntWaveform(self,wf):
        self.dtaFile.seek(wf.dataPosition)
        d2=self.dtaFile.read(wf.N)
        sampleList=[]
        for i in range(0,wf.N,2):
            s=self.str2num(''.join([d2[i],d2[i+1]]))
            v=s if s<32768 else (s-65536)
            #print v
            #raw_input("press enter to continue!")
            sampleList.append(v)
        return sampleList
    def getWaveform(self,wf):
        self.dtaFile.seek(wf.dataPosition)
        d2=self.dtaFile.read(wf.N)
        sampleList=[]
        for i in range(0,wf.N,2):
            s=self.str2num(''.join([d2[i],d2[i+1]]))
            v=0.00030518*s if s<32768 else 0.00030518*(s-65536)
            #print v
            #raw_input("press enter to continue!")
            sampleList.append(v)
        return sampleList
    def getTimeOfStart(self):
        print self.timeOfStart
        return self.timeOfStart
if (__name__=='__main__'):
    dta=dtaReader()
    dta.open("D:\\AE-Data-602\\exp2\\test2-2.DTA")
    dta.analysis(True,True)
##    dta.getHitData(True,dta.filePath.split('.')[0]+'_hitData.txt')
##    dta.getWaveformData(True)
    print dta.getWaveform(dta.waveList[1])