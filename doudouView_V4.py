# -*- coding: utf-8 -*-

"""
在获取的图片上按下鼠标的滚轮键，获取当前点的波形。在波形上按左键，可以获取波形上选取点的采样点的位置和幅值。load可以删除波形。

Change log:
2013-1-1 增加支持中文特征名称的功能 --OEway
2013-1-3 支持多特征热力图显示 --OEway
2013-1-3 增加对当前视图区域进行频谱分析的功能，对波形图放大后，点击功率谱图区域，即可查看当前视图范围内波形的频谱 --OEway
2013-1-10 增加读取SAM300超声显微镜的SAZ文件功能 --OEway
2013-1-10 增加读取txt文件功能 --OEway
2013-1-25 增加批量读取当前目录下所有txt文件功能 --OEway
2013-1-25 增加读取声发射DTA文件功能 --OEway
2013-3-20 增加读取陆老师家的超声F扫描的NDT文件功能 --OEway
"""
try:
    from tables import *
except:
    print('PyTables not installed! hdf file will not supported')
import codecs
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import mlab as ml
import numpy as np
import Tkinter, tkFileDialog
import string
import matplotlib.colors as colors
import webbrowser
import os
from matplotlib.widgets import Cursor, Button
import matplotlib.pyplot as plt
import numpy as np
import pointCalculateV3
import shutil
import sazReader
import ndtReader
import traceback
from numpy.random import RandomState
import pylab
import dtaReader
plt.rcParams['font.size']=8
prng = RandomState(1234567890)
class doudouView(object):
    def __init__(self,dataSet):
        """ 
        Shows a given array in a 2d-viewer.
        Input: z, an 2d array.
        x,y coordinters are optional.
        """
        self.dataSet = dataSet
        self.x =0
        self.y =0
        self.currentPos = (0,0)
        self.fig=plt.figure('doudouView V4')
        #Doing some layout with subplots:
        self.fig.subplots_adjust(0.05,0.05,0.98,0.95,0.2,0.3)
        #print dir(self)
        #self.plot(('Model length', 'Data length', 'Total message length'), 'upper center', shadow=True)
        #leg = ax.legend(('Model length', 'Data length', 'Total message length'), 'upper center', shadow=True)
        self.ScanMapPlot=plt.subplot2grid((8,4),(0,0),rowspan=7,colspan=2)
        #plt.plot(label = "$cosssss(x)$",color="red",linewidth=2)
        #self.ScanMapPlot.text(0.5, 0.5, "sin(x)" , va="top", ha="right")
        #self.ScanMapPlot.set_title(self.click.name)
        self.ScanMapPlot.matshow(self.dataSet.imgMat)
        self.ScanMapPlot.autoscale(1,'both',1)
        self.waveFormPlot=plt.subplot2grid((8,4),(0,2),rowspan=4,colspan=2)
        self.waveFormFFTPlot=plt.subplot2grid((8,4),(4,2),rowspan=4,colspan=2)
        #self.waveFormPlot.callbacks.connect('xlim_changed', self.shwoWaveformFft) 
        #Adding widgets, to not be gc'ed, they are put in a list:

        #cursor=Cursor(self.ScanMapPlot, useblit=True, color='black', linewidth=0.5 )
        but_ax=plt.subplot2grid((8,4),(7,0),colspan=1)
        load_button=Button(but_ax,'Load')
        but_ax2=plt.subplot2grid((8,4),(7,1),colspan=1)
        generate_button=Button(but_ax2,'Generate')
        self._widgets=[load_button,generate_button]#cursor
        #connect events
        load_button.on_clicked(self.load)
        generate_button.on_clicked(self.generate)
        self.fig.canvas.mpl_connect('button_press_event',self.click)
        self.clickMode4fft = 'sfft'
        self.argsDict = {}
        self.argsDict['stepSize'] = self.dataSet.stepSize
        self.argsDict['batchMode'] = False
        self.argsDict['workDir'] = self.dataSet.fpath
        self.argsDict['dataMode'] = self.dataSet.mode
    def genScalarMap(self,Valmin,Valmax):    
        jet = cmm = plt.get_cmap('jet') 
        cNorm  = colors.Normalize(vmin=Valmin,vmax =Valmax)
        self.scalarMap = cm.ScalarMappable(norm=cNorm, cmap=jet)
        print self.scalarMap.get_clim()
        #colorVal = scalarMap.to_rgba(0.5)
        #print colorVal
        return self.scalarMap
    def generate(self, event):
        #data = np.zeros((len(keys),3))
        #print('len',len(keys))
        try:
            reload(pointCalculateV3)
        except:
            print("reload error!")
        f = codecs.open(os.path.join(self.dataSet.fpath,self.dataSet.fname+"_FscanData.csv"),'w', "gbk")
        titles = False
        count = 0
        mapDict = {}
        xlims = self.ScanMapPlot.get_xlim()
        ylims = self.ScanMapPlot.get_ylim()
        xlims = (min(xlims)+self.dataSet.minX,max(xlims)+self.dataSet.minX)
        ylims = (min(ylims)+self.dataSet.minY,max(ylims)+self.dataSet.minY)
        print xlims,ylims

        self.argsDict['batchMode'] = True
        for cord in self.dataSet:
            array,st = self.dataSet.getWaveform(cord)
            self.argsDict['label'] = st
            #print array
            if array is None:
                continue
            #print array[:10]
            px = cord[0]
            py = cord[1]
            if px > xlims[1] or px < xlims[0] or py > ylims[1] or py < ylims[0]:
                #print px,py,xlims,ylims
                continue
            # else:
                # print px,py
            try:
                annotateDict = pointCalculateV3.calculatePoint((px,py),array,self.argsDict)
            except:
                annotateDict ={}
                traceback.print_exc()
            if not titles:
                for k in  annotateDict.keys():
                    if '_label' in k:
                        continue
                    if '_waveform' in k:
                        continue
                    f.write("{0},".format(k.replace('_label','').replace('_map','').replace('_background','')))
                f.write("\n")
                titles = True
            for k in annotateDict.keys():
                if '_label' in k:
                    continue
                if '_waveform' in k:
                    continue
                try:
                    f.write("{0},".format(annotateDict[k]))
                    if '_map' in k or '_background' in k:
                        if not mapDict.has_key(k):
                            Z = np.zeros((self.dataSet.yCount,self.dataSet.xCount))
                            Z[:,:] = np.nan
                            mapDict[k] = Z
                        val = annotateDict[k]
                        inx = int((px-self.dataSet.minX)/self.dataSet.stepSize[0])
                        iny = int((py-self.dataSet.minY)/self.dataSet.stepSize[1])
                        # if inx < self.dataSet.maxX/self.dataSet.stepSize[0] and inx > self.dataSet.minX/self.dataSet.stepSize[0]:
                        #if self.dataSet.mode == 'h5':
                        #    if iny%2 == 0 and inx >= 2:
                            #print iny,inx
                        #        mapDict[k][iny][inx-2] = val
                        #    if iny%2 == 1:
                        #        mapDict[k][iny][inx] = val
                        #else:
                        mapDict[k][iny][inx] = val
                except:
                    f.write("error,")
                    print('key value error: {0}'.format(repr(k)))
            f.write("\n")
            print '.',
            count += 1
        f.close()
        self.argsDict['batchMode'] = False
        # colormap
        cmap = cm.jet
        settings = pointCalculateV3.settings()
        if settings.has_key('colorMap'):
            cmap = settings['colorMap']
        # set NaN values as white
        cmap.set_bad('w')
        for k in mapDict.keys():
            if '_background' in k:
                self.ScanMapPlot.matshow(mapDict[k],cmap = cmap, interpolation='nearest')
                self.ScanMapPlot.autoscale(1,'both',1)
                continue
            try:
                if settings.has_key('flip'): 
                    mapDict[k] = settings['flip'](mapDict[k])
            except:
                print('flip error!')

            fig2=plt.figure(self.dataSet.fname+"_"+k)
            fig2.clf()
            ax = fig2.add_subplot(111)
            imm = ax.matshow(mapDict[k],cmap = cmap, interpolation='nearest')
            
            # xt = np.arange(self.dataSet.minX,self.dataSet.maxX+1,self.dataSet.stepSize[0])
            # xt = map(str,xt)
            # yt = np.arange(self.dataSet.minY,self.dataSet.maxY+1,self.dataSet.stepSize[1])
            # yt = map(str,yt) 
            # ax.set_xticks(np.arange(len(xt)),xt)
            # ax.set_yticks(np.arange(len(yt)),yt)
            #ax.set_xticklabels(['']+xt)
            #ax.set_yticklabels(['']+yt)
            ax.set_axis_off()
            plt.axis('off')
            plt.savefig(os.path.join(self.dataSet.fpath,self.dataSet.fname+"_"+k+"_"+".png"),bbox_inches='tight')
            ax.set_axis_on()
            plt.axis('on')
            
            fig2.colorbar(imm)
            fig2.savefig(os.path.join(self.dataSet.fpath,self.dataSet.fname+"_"+k+".png"))
            fig2.show()
        try:
            tmp1,tmp2=os.path.split(pointCalculateV3.__file__.replace(".pyc",".py"))
            shutil.copyfile(pointCalculateV3.__file__.replace(".pyc",".py"),os.path.join(self.dataSet.fpath,tmp2))
            tmp1,tmp2=os.path.split(__file__)
            shutil.copyfile(__file__,os.path.join(self.dataSet.fpath,tmp2))
        except:
            pass
        print("Done!")
        
    def load(self,event):
        """Clears the subplots."""
        try:
            reload(pointCalculateV3)
        except:
            print("reload error!")
        del self.dataSet
        self.dataSet = DataSet()
        self.argsDict['stepSize'] = self.dataSet.stepSize
        self.argsDict['batchMode'] = False
        self.argsDict['workDir'] = self.dataSet.fpath
        self.argsDict['dataMode'] = self.dataSet.mode
        #Put it in the viewer
        self.ScanMapPlot.cla()
        self.ScanMapPlot.matshow(self.dataSet.imgMat)
        self.ScanMapPlot.autoscale(1,'both',1)
        
    def onpick(self,event):
        try:
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print 'onpick points:', zip(xdata[ind], ydata[ind])
        except:
            pass
    def click(self,event):
        """
        What to do, if a click on the figure happens:
        1. Check which axis
        2. Get data coord's.
        3. Plot resulting data.
        4. Update Figure
        """

        if event.inaxes == self.ScanMapPlot:
            if event.button == 1 :
                try:
                    reload(pointCalculateV3)
                except:
                    print("reload error!")
                self.waveFormFFTPlot.cla()
                self.waveFormPlot.cla()
                xpos=int(event.xdata + 0.5)
                ypos=int(event.ydata + 0.5)
                cor = (self.dataSet.stepSize[0]*xpos+self.dataSet.minX ,self.dataSet.stepSize[1]*ypos+self.dataSet.minY)
                print("-----------------------------------------------")
                print cor
                print("***********************************************")
                self.currentPos = cor
                data,st = self.dataSet.getWaveform(cor)
                self.argsDict['label'] = st
                #self.ScanMapPlot.set_title(st)
                self.ScanMapPlot.set_xlabel(st, fontsize=12)
                self.argsDict['batchMode'] = False
                if data  is not None:
                    self.showWaveform(data)
                    try:
                        annotateDict = pointCalculateV3.calculatePoint((cor[0],cor[1]),data,self.argsDict)
                    except:
                        traceback.print_exc()
                        annotateDict ={}
                    backSeted = False
                    for an in annotateDict.keys():
                        try:
                            if "_label" in an:
                                try:
                                    self.waveFormPlot.annotate(an.replace("_label",""), xy=(annotateDict[an],data[annotateDict[an]]),  xycoords='data',xytext=(0, 10), textcoords='offset points',size=10,arrowprops=dict(arrowstyle="->"))
                                except:
                                    print("error in annotate!")
                                print("{0}:{1}".format(repr(an),annotateDict[an]))
                            if '_waveform' in an:
                                dat=annotateDict[an]
                                self.waveFormPlot.plot(dat,picker = 5,label = an.replace('_waveform',''))
                                print("{0}".format(repr(an)))
                        except:
                            print('error in key {0}'.format(repr(an)))
                    self.waveFormPlot.legend()
                    self.shwoWaveformFft(self.clickMode4fft)
                else:
                    print("not found!")

##        if event.inaxes==self.waveFormFFTPlot:
##            ypos=np.argmin(np.abs(event.xdata-self.y))
##            c=self.waveFormPlot.plot(self.x, self.z[ypos,:],label=str(self.y[ypos]))
##            self.ScanMapPlot.axhline(self.y[ypos],color=c.get_color(),lw=2)
##
        if event.inaxes==self.waveFormPlot:
            print event.button,event.key ,self.clickMode4fft
            if event.key is None:
                return
            if event.button == 1 and ' ' in event.key  and self.clickMode4fft == 'sfft':
                self.clickMode4fft = 'fft'
                self.shwoWaveformFft(self.clickMode4fft)
                
            elif event.button == 1 and ' ' in event.key and self.clickMode4fft == 'fft':
                self.clickMode4fft = 'sfft'
                self.shwoWaveformFft(self.clickMode4fft)
                
            print('mode:{0}'.format(self.clickMode4fft))
        #Show it
        plt.draw()
        if event.inaxes==self.waveFormFFTPlot:
            if event.key is None:
                return
            if event.button == 1 and ' ' in event.key:
                line = self.waveFormFFTPlot.get_lines()[0]
                xd = line.get_xdata()
                yd = line.get_ydata()
                j=codecs.open(os.path.join(self.dataSet.fpath,self.dataSet.fname+"_fft.csv"),'w', "gbk")
                j.write("X,Y\n")
                for i in xrange(len(xd)):
                    j.write("%.3f,%.3f\n"%(xd[i],yd[i]))
                j.close()
                print('file had saved to:{0}'.format(os.path.join(self.dataSet.fpath,self.dataSet.fname+"_fft.csv")))
    def showWaveform(self,dataset):
        #name = self.group._v_children.keys()[index]
        #deepthStep =1.0/100000*1450/2
        #t = np.arange(offset* deepthStep ,(offset+length)*deepthStep,deepthStep)[:len(dataset)]
        p = np.arange(len(dataset))
        #print p,t
        timeStep = 1.0/100000000
        self.waveFormPlot.plot(p,dataset,picker = 5,label='waveform')
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
    def shwoWaveformFft(self,mode):
        self.waveFormFFTPlot.cla()
        xlims = self.waveFormPlot.get_xlim()
        timeStep = 1.0/100000000
        dataset,st = self.dataSet.getWaveform(self.currentPos)
        self.argsDict['label'] = st
        if dataset == None:
            return
        l = len(dataset)
        d = max(0,xlims[0])
        u = min(l-1,xlims[1])
        #print d,u
        dataset = dataset[int(d):int(u)]
        if mode == 'fft':
            sp = np.fft.fft((dataset*np.hanning((int(u)-int(d))))/np.mean(dataset))
            freq = np.fft.fftfreq(len(dataset),d = timeStep)
            x = freq[1:len(dataset)/2]
            y = np.abs(sp)[1:len(dataset)/2]
            mx = np.argmax(y)
            
            try:
                self.waveFormFFTPlot.annotate(str(x[mx]), xy=(x[mx],y[mx]),  xycoords='data',xytext=(30, 0), textcoords='offset points',size=10,arrowprops=dict(arrowstyle="->"))
            except:
                print("error in annotate!")
            #plt.plot(label = "$sin(x)$",color="red",linewidth=2)
            self.waveFormFFTPlot.plot(x, y)
        if mode == 'sfft':
            self.waveFormFFTPlot.specgram(dataset, NFFT=64, Fs=100000000, noverlap=16)
        plt.draw()
class DataSet():
    stepSize = [1.0,1.0]
    totalPointCount = 480*640
    cordTable ={}
    img = None
    maxX = 0
    maxY = 0
    minX = 480
    minY = 640
    mode = 'h5'
    saz = None
    h5file = None
    ndt = None
    width = 0
    height = 0
    def __init__(self):
        root = Tkinter.Tk()
        root.withdraw()
        self.filePath = tkFileDialog.askopenfilename(parent=root)
        self.fpath,self.fname=os.path.split(self.filePath)
        self.xCount = 0
        self.yCount = 0
        self.cordTable = {}
        self.stepSize=[1,1]
        try:
            self.minX =0
            self.minY =0
            self.imgMat = np.zeros((1,1))
            if '.h5' in self.filePath.lower():
                self.minX =480
                self.minY =640
                self.loadH5File(self.filePath)
                self.mode = 'h5'
                self.currentPos = self.cordTable.values()[0]
                try:
                    xys = np.array(self.cordTable.keys(),dtype = np.float)
                    xys[:,0] -=self.minX
                    xys[:,1] -=self.minY
                    xys[:,0] /=self.stepSize[0]
                    xys[:,1] /=self.stepSize[1]
                    xys = xys.astype(int)
                    #print xys
                    #img = pylab.imread(os.path.join(self.fpath,'testPic.bmp'))
                    #self.imgMat = pylab.mean(img,2)[int(self.minY/self.stepSize[1]):int(self.minY/self.stepSize[1])+self.yCount,int(self.minX/self.stepSize[0]):int(self.minX/self.stepSize[0])+self.xCount]
                    #mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                    self.imgMat = np.zeros((self.yCount,self.xCount))#mat.reshape((self.yCount,self.xCount))
                    self.imgMat[xys[:,1],xys[:,0]] = 255
                except:
                    traceback.print_exc()
                    mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                    self.imgMat = mat.reshape((self.yCount,self.xCount))
            elif '.saz' in self.filePath.lower():
                self.saz = sazReader.sazReader()
                self.saz.open(self.filePath)
                self.width,self.height = self.saz.msgDict['pixelWidth'].value,self.saz.msgDict['pixelHeight'].value
                print("{0},{1}".format(self.width, self.height))
                self.xCount = self.width
                self.yCount = self.height
                self.mode = 'saz'
                mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                self.imgMat = mat.reshape((self.yCount,self.xCount))
            elif '.ndt' in self.filePath.lower():
                self.ndt = ndtReader.ndtReader()
                self.ndt.open(self.filePath)
                self.width,self.height = self.ndt.msgDict['pixelWidth'].value,self.ndt.msgDict['pixelHeight'].value
                print("{0},{1}".format(self.width, self.height))
                self.xCount = self.width
                self.yCount = self.height
                self.mode = 'ndt'
                mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                self.imgMat = self.ndt.image#mat.reshape((self.yCount,self.xCount))
            elif '.txt' in self.filePath.lower():
                self.mode = 'txt'
                from fnmatch import fnmatch
                root = self.fpath
                pattern = "*.txt"
                
                fL = []
                for path, subdirs, files in os.walk(root):
                    for name in files:
                        if fnmatch(name, pattern):
                            print os.path.join(path, name)
                            fL.append(os.path.join(path, name))
                n = len(fL)
                self.width,self.height = int(np.sqrt(n)+1),int(np.sqrt(n)+0.5)
                i = 0
                for fn in fL:
                    self.cordTable[(i%self.width,i//self.width)] = fn
                    i +=1
                self.xCount = self.width
                self.yCount = self.height
                mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                self.imgMat = mat.reshape((self.yCount,self.xCount))
            elif '.dta' in self.filePath.lower():
                self.dta = dtaReader.dtaReader()
                self.dta.open(self.filePath)
                self.dta.analysis()
                n = len(self.dta.waveList)
                self.width,self.height = int(np.sqrt(n)+0.5),int(np.sqrt(n)+0.5)
                print("{0},{1}".format(self.width, self.height))
                self.xCount = self.width
                self.yCount = self.height
                self.mode = 'dta'
                mat = prng.randint(0, 255, size=self.yCount*self.xCount)
                self.imgMat = mat.reshape((self.yCount,self.xCount))
        except:
            traceback.print_exc()
            print("mode error!")
            self.mode = 'error'
        #root.after(1000, root.quit)
    def __iter__(self):
        self.iterI = 0
        self.iterJ = 0
        if self.mode == 'h5':
            return  iter(self.cordTable.iterkeys())
        if self.mode == 'txt':
            return  iter(self.cordTable.iterkeys())            
        elif self.mode == 'saz':
            return self
        elif self.mode == 'ndt':
            return self
        elif self.mode == 'dta':
            return self
        
        else:
            return self
    def next(self):
        if self.mode == 'saz' or 'ndt':
            self.iterI +=1
            if self.iterI > self.width:
                self.iterI = 0
                self.iterJ +=1
                if self.iterJ >self.height:
                    self.iterI = 0
                    self.iterJ = 0
                    raise StopIteration
            return (self.iterI-1 ,self.iterJ)
        if self.mode == 'dta':
            self.iterI +=1
            if self.iterI > self.width:
                self.iterI = 0
                self.iterJ +=1
                if self.iterJ >self.height:
                    self.iterI = 0
                    self.iterJ = 0
                    raise StopIteration
            return (self.iterI-1 ,self.iterJ)            
        else:
            self.iterI +=1
            if self.iterI <2:
                self.iterI = 0
                self.iterJ = 0
                return (self.iterI ,self.iterJ)
            else:
                raise StopIteration
    def getWaveform(self,cord):
        try:
            if self.mode == 'h5':
                cor = (cord[0],cord[1])
                if self.cordTable.has_key(cor):
                    #print self.cordTable[cor]
                    return self.group._v_children[self.cordTable[cor]][:],self.fname+": "+self.cordTable[cor]
                else:
                    return None,"Not Found"
            elif self.mode == 'saz':
                wav = self.saz.getWaveform((cord[0],cord[1]))
                if wav is None:
                    return None,"Not Found"
                else:
                    return np.array(wav),"%s:%d %d"%(self.fname,cord[0],cord[1])
            elif self.mode == 'ndt':
                wav = self.ndt.getWaveform((cord[0],cord[1]))
                if wav is None:
                    return None,"Not Found"
                else:
                    return np.array(wav),"%s:%d %d"%(self.fname,cord[0],cord[1])
            elif self.mode == 'dta':
                try:
                    wf=self.dta.waveList[int(cord[1]* self.width+cord[0])]
                    wav = self.dta.getWaveform(wf)
                    return np.array(wav),"t:{0} ch:{1}".format(wf.tot,wf.channelNum)
                except:
                    traceback.print_exc()
                    return None,"Not Found"
                    
            elif self.mode == 'txt':
                if self.cordTable.has_key((cord[0],cord[1])):
                    try:
                        filename = self.cordTable[(cord[0],cord[1])]
                        ff,nn = os.path.split(filename)
                        return np.loadtxt(filename),nn
                    except:
                        return None,"File Error!"
                else:
                    return None,"Not Found"
            else:
                return None,"Mode Error"
        except:
            return None,"Error"
    def loadH5File(self,filePath):
        self.h5file=openFile(filePath,'a')
        self.group = self.h5file.getNode('/original0')
        attrs = self.h5file.root._v_attrs
        if "stepSize" in attrs._v_attrnames:
            ss = attrs.stepSize
            ss = ss.split(",")
            self.stepSize[0] = float(ss[0])
            self.stepSize[1] = float(ss[1])
        if "recordDate" in attrs._v_attrnames:
            print "recordDate:",attrs.recordDate
        if "totalPointCount" in attrs._v_attrnames:
            print "totalPointCount:",attrs.totalPointCount
            self.totalPointCount = string.atof(attrs.totalPointCount)
            print "stepSize:", self.stepSize
            keys = self.group._v_children.keys()
        for key in keys:
            array = self.group._v_children[key]
            name=self.group._v_children[key]._v_name
            px,name=name.split('N')[1].split('x')
            py,name=name.split('y')
            pz=name.split('z')[0]
            
            py = int(float(py)/1000+0.5)
            px = int(float(px)/1000+0.5)
            self.cordTable[(px,py)] = key
            if px < self.minX:
                self.minX = px
            if px > self.maxX:
                self.maxX = px
            if py < self.minY:
                self.minY = py
            if py > self.maxY:
                self.maxY = py
            #print(px,py,self.minX,self.minY,self.maxX,self.maxY)
            #maxa,maxa_coord,mina,mina_coord,maxb,maxb_coord,minb,minb_coord,maxc,maxc_coord,minc,minc_coord,maxd,maxd_coord,mind,mind_coord = calculatePoint((px,py,pz),(stepSizeX,stepSizeY),array)
            
            #print (px,py),key
            #table1[(px,py)]= [(maxa,maxa_coord,mina,mina_coord,maxb,maxb_coord,minb,minb_coord,maxc,maxc_coord,minc,minc_coord,maxd,maxd_coord,mind,mind_coord)]
            #print table1
        # self.minX = 0
        # self.maxX = 270
        self.xCount = int((self.maxX-self.minX)/self.stepSize[0]+1.5)
        self.yCount = int((self.maxY-self.minY)/self.stepSize[1]+1.5)
        print(self.minX,self.minY,self.maxX,self.maxY,self.xCount,self.yCount)
        #Image.open(os.path.join(self.fpath,"testPic.bmp")).crop((int(self.minX),int(self.minY),int(self.maxX),int(self.maxY)))
if __name__=='__main__':
    d = DataSet()
    #Put it in the viewer
    fig_v=doudouView(d)
    #viewer_2d.group = d.group
    #fig_v2=viewer_2d(A)
    #Show it
    plt.show()
    #root.after(1000, root.quit)


