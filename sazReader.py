# -*- coding: utf-8 -*-
import struct
import os
import matplotlib
class message():
    length=0
    location=0
    format = ''
    content = ''
    value = 0
    unit = ''
    valueDict = {}
    def __init__(self,location,length,format,unit= '',valueDict={}):
        self.length = length
        self.location = location
        self.format = format
        self.unit = unit
        self.valueDict = valueDict
class sazReader():
    '''
    超声显微镜saz文件读取库
    TODO：解析其他标签
    
    '''
    def __init__(self):
        self.sazFile=None
        self.filePath=''
        self.msgDict={}
        self.hdList=[]
        self.filePointer=0
        self.waveList=[]
        self.time_wave_dict={}
        self.index4channel={}
        self.timeOfStart="Time of start not found!"

        #message define: name , location ,length
        self.msgDict['head'] = message(0,64,'72s')
        self.msgDict['unit'] = message(128,28,'28s')
        self.msgDict['transducor'] = message(448,8,'8s')
        self.msgDict['realWidth']=message(76,4,"<L",'um')
        self.msgDict['realHeight']=message(80,4,"<L",'um')
        self.msgDict['pixelWidth']=message(88,4,"<L",'pixel')
        self.msgDict['pixelHeight']=message(92,4,"<L",'pixel')
        self.msgDict['resolutionX']=message(84,4,"<L",'pixel/mm')
        self.msgDict['resolutionY']=message(96,4,"<L",'X')
        self.msgDict['display']=message(116,4,"<i",'',{0:'1',1:'2','-1':'1/2'})
        self.msgDict['xPos']=message(100,4,"<L",'um')
        self.msgDict['yPos']=message(104,4,"<L",'um')
        self.msgDict['zPos']=message(108,4,"<L",'um')
        
        self.msgDict['cscanWidth']=message(184,4,"<L",'ns')
        self.msgDict['cscanPos']=message(180,4,"<i",'ns')
        self.msgDict['bscanPos']=message(188,4,"<i",'ns')
        self.msgDict['bscanWidth']=message(192,4,"<L",'ns')
        self.msgDict['sftPos']=message(196,4,"<i",'ns')
        self.msgDict['sftWidth']=message(200,4,"<L",'ns')
       
        self.msgDict['highResolution']=message(64,1,"<B")
        self.msgDict['highPass']=message(292,4,"<L",'MHz',{0:5,1:30})
        self.msgDict['lowPass']=message(288,4,"<L",'MHz',{0:500,1:300})
        self.msgDict['voltage']=message(280,4,"<L",'V')
        self.msgDict['gain']=message(284,4,"<L",'dB')
        
        self.msgDict['dataWidth']=message(480,4,"<L")
        self.msgDict['dataHeight']=message(484,4,"<L")
        self.msgDict['dataAspectRatio']=message(488,4,"<L")
        self.msgDict['waveformLength']=message(492,4,"<L",'byte')
        self.msgDict['Waveform']=message(496,7504,"")

        
    def open(self,path):
        self.filePath=path
        self.sazFile=open(self.filePath,'rb')
        self.fileSize = os.path.getsize(self.filePath)
        print('file size:{0}'.format(self.fileSize))
        f=self.sazFile
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
        self.msgDict['Waveform'].length = self.msgDict['waveformLength'].value
        print 'Analysis Done!Message count:',len(self.msgDict)

    def getWaveform(self,(x,y)):
        x = int(x)
        y = int(y)
        p = int(self.msgDict['Waveform'].location + (y * self.msgDict['dataWidth'].value +x)*self.msgDict['waveformLength'].value)
        f=self.sazFile
        #print p,os.fstat(f.fileno()).st_size
        try:
            f.seek(p,0)
            str = f.read(self.msgDict['Waveform'].length)
            count = self.msgDict['Waveform'].length//2
            wave = struct.unpack('>{0}h'.format(count),str)
            return wave
        except:
            return None
if (__name__=='__main__'):
    saz=sazReader()
    saz.open("./saz1.SAZ")
    print saz.getWaveform((0,0))[:10]
