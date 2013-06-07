# -*- coding: utf-8 -*-
import math
import numpy as np
import os
from collections import OrderedDict
#----------------------------------------------------------------------------------------------------------------------------

Start = 4000  #搜索最大值起点
width = 500 #搜索宽度范围

ignoreLevelUp = 100 #正幅度阈值 高于该阈值的信号才被检测
ignoreLevelDown = 100 #负幅度阈值 低于该阈值的信号才被检测

#----------------------------------------------------------------------------------------------------------------------------
try:
    from scipy import fftpack
except:
    print('scipy is not found!')
from matplotlib import cm
def settings():
    '''
    参数设置字典
    colorMap：特征热力图所使用的颜色表
    flip: 对图像矩阵进行旋转、转置等操作可以设置为:np.fliplr 左右旋转  np.flipud 上下旋转 np.transpose 转置 np.rot90 逆时针旋转90度等操作
    '''
    settings = {}
    settings['colorMap'] = cm.gray
    settings['flip'] = np.fliplr
    return settings
def calculatePoint((x,y),waveform,argsDict):
    '''
    点计算函数
    x,y,z:点的坐标

    waveform:波形数据
    returnDict:返回的字典，字典的键值为名称，
    如果键值中含有_label则会在波形图中显示该点的位置.
    如果键值中含有_map则会生成该特征的热力图.
    如果键值中含有_waveform则会在波形图中显示该曲线.  
    如果键值中含有_background则会在作为背景显示.  
	
    args为参数字典，目前支持以下参数：
        batchMode： 表示是否批处理生成模式，可以利用这个变量来分别是否是单次选取波形还是批量生成数据
        stepSizeX:x轴每步走的步距
        stepSizeY:y轴每步走的步距
        workDir:工作目录
        dataMode:文件模式，有txt/h5/saz三种模式
        label: 当前波形的标签，类型string,txt模式下是文件名，其他模式下含有坐标
		
    '''
    returnDict = OrderedDict()
	
    if not argsDict['batchMode']:#只在点击的时候保存文件
        np.savetxt(os.path.join(argsDict['workDir'],'data.txt'),waveform,fmt='%d') #保存文件到C盘
        #returnDict['zeroline_waveform'] = 0*waveform #零线
    #try:
        #hx = fftpack.hilbert(waveform[:])
        #envelop = np.sqrt(hx**2 +waveform[:]**2)
        #returnDict['envelop_waveform'] = envelop #包络检测
    #except:
        #pass
    #returnDict['zeroline_waveform'] = 0*waveform
    csloc = waveform[Start:Start+ width].argmax()
    returnDict['TOF_label'] = Start+csloc
    returnDict['TOF_map'] = Start+csloc
    returnDict['cScan_map'] = waveform[returnDict['TOF_map']]
    if ignoreLevelUp > returnDict['cScan_map'] and ignoreLevelDown<returnDict['cScan_map'] :
        returnDict['cScan_map'] = np.NAN
        returnDict['TOF_map'] = np.NAN
    returnDict['cScan_background'] = returnDict['cScan_map']
    return returnDict