# -*- coding:utf-8 -*-

import serial
import threading
import os
import sys
import signal
import re
import time
import datetime
import struct
import binascii
import string
from loguru import logger
from ctypes import *
import math
import keyboard
    

# RFData = {'Frame_Header':[],'Nick_name':[], 'CMD':[], 'DataLen':[], 'Data':[], 'CheckSum':[]}

os.system('')
SerialNumberList = os.system('python -m serial.tools.list_ports')

InputSerialNumber = input("请输入使用的串口号数字：")
SerialNumber = 'COM'+InputSerialNumber
print("SerialNumberList=%s\n"%SerialNumber)
#'COMx', 波特率=115200, bytesize=8, parity='N', stopbits=1,timeRcvSerialData=2s
ser = serial.Serial(SerialNumber,115200,8,'N',1,timeout=2)   

# logger.add(r'.\report\LoggerTest_{time}.log', format="{time} {level} {message}", filter="A_test_RF_PER_OC", level="TRACE", rotation="50 MB")
# logger.debug('SerialPort Open Success\n')
# logger.debug('SerialPort Open Fail\n')
# logger.debug('This is debug information')
# logger.info('This is info information')
# logger.warning('This is warn information')
# logger.error('This is error information')

if ser.isOpen():
    print('SerialPort Open Success\n')
    # logger.debug('SerialPort Open Success\n')
    # ser.close()
else:
    print('SerialPort Open Fail\n')
    # logger.debug('SerialPort Open Fail\n')
    
ManualRecordWaveCnt = 0
def sends():
    """ 发送数据 """
    global ManualRecordWaveCnt
    TestCnt = 1
    
    while True:
        try:
            inputstr, TestCnt = input("请输入测试命令: 测试次数:\n").split()
            # print('inputstr:%s TestCnt:%s'%(inputstr,TestCnt))
            inputstr = inputstr.encode('utf-8')
            
            if inputstr != '':
                if inputstr == b'wave' and TestCnt.isdigit() == True:
                    for i in range(1,int(TestCnt)+1,1):
                        ser.write(inputstr)  # 发送
                        ManualRecordWaveCnt += 1
                        print('测试次数:%s 手动触发录波计数: \033[1;33m%s\033[0m'%(i,ManualRecordWaveCnt))
                        time.sleep(65)  #录波测试间隔
                elif inputstr != b'wave' and TestCnt.isdigit() == True:
                    print('输入测试命令不支持！')
                else:
                    print('输入测试命令格式有误!\n参考格式：wave 5')
        except BaseException as e:
            # print('错误类型: ',e.__class__.__name__)
            # print('错误明细: ',e)    
            if isinstance(e, EOFError):
                # print('Input CTRL+C')
                sys.exit(1)
                # os.system('"taskkill /F /IM python.exe"')
            else:
                print('输入测试命令格式有误, 参考格式：wave 5')
        # except KeyboardInterrupt:
        #    sys.exit(1)
        # except:
            # print('输入测试命令格式有误, 参考格式：wave 5')

        finally:
            inputstr = ''
            # keyboard.add_hotkey('ctrl+c', TestExit)

OC_Reset_Count = 0

OC_Send_Data_to_DM_Flg = False
OC_Rcv_Data_to_DM_Flg = False
n = 0
ReportDMOldTicks = 0.0

IEC10X_Reade_Flg = False
IEC10X_Write_Flg = False
k = 0
ReportIEC10XOldTicks = 0.0

RecordWaveBroadcastCnt_I = 0
RecordWaveBroadcastCnt_IA = 0
RecordWaveBroadcastCnt_IB = 0
RecordWaveBroadcastCnt_IC = 0

RecordWaveBroadcastCnt_V = 0
RecordWaveBroadcastCnt_VA = 0
RecordWaveBroadcastCnt_VB = 0
RecordWaveBroadcastCnt_VC = 0

RecordWaveResponseCnt_I = 0
RecordWaveResponseCnt_IA = 0
RecordWaveResponseCnt_IB = 0
RecordWaveResponseCnt_IC = 0
    
RecordWaveResponseCnt_V = 0
RecordWaveResponseCnt_VA = 0
RecordWaveResponseCnt_VB = 0
RecordWaveResponseCnt_VC = 0

ZeroSequenceComponentUploadCnt_I = 0
ZeroSequenceComponentUploadCnt_IA = 0
ZeroSequenceComponentUploadCnt_IB = 0
ZeroSequenceComponentUploadCnt_IC = 0

ZeroSequenceComponentUploadCnt_V = 0
ZeroSequenceComponentUploadCnt_VA = 0
ZeroSequenceComponentUploadCnt_VB = 0
ZeroSequenceComponentUploadCnt_VC = 0

FwUpdateResponseCnt = 0
FwUpdateResponseCnt_A = 0
FwUpdateResponseCnt_B = 0
FwUpdateResponseCnt_C = 0

FwUpdateResponseOKCnt_A = 0
FwUpdateResponseOKCnt_B = 0
FwUpdateResponseOKCnt_C = 0

FwUpdateResponseErCnt_A = 0
FwUpdateResponseErCnt_B = 0
FwUpdateResponseErCnt_C = 0

FwWriteFlashCnt = 0
FwWriteFlashCnt_A = 0
FwWriteFlashCnt_B = 0
FwWriteFlashCnt_C = 0

FwUpdateTxCnt = 0
FwUpdateTxCnt_A = 0
FwUpdateTxCnt_B = 0
FwUpdateTxCnt_C = 0

ZeroSeqASNIntervalOKCnt_A = 0
ZeroSeqASNIntervalErCnt_A = 0
ZeroSeqASNIntervalOKCnt_B = 0
ZeroSeqASNIntervalErCnt_B = 0
ZeroSeqASNIntervalOKCnt_C = 0
ZeroSeqASNIntervalErCnt_C = 0

RF_CRC_Error_Count = 0
ZeroSeqASN_PLC_A = 0
ZeroSeqASN_PLC_B = 0
ZeroSeqASN_PLC_C = 0

ZeroSeqASNRepeatCnt_A = 0
ZeroSeqASNRepeatCnt_B = 0
ZeroSeqASNRepeatCnt_C = 0

def reads():
    """ 读取并解析数据 """
    RcvSerialData = ''
    i = 0
    Ai = 0
    Bi = 0
    Ci = 0
    j = 0
    Aj = 0
    Bj = 0
    Cj = 0
    
    DLCfgTicks = 0.0
    A_ReportLineOldTicks = 0
    B_ReportLineOldTicks = 0
    C_ReportLineOldTicks = 0
    A_ReportLine2OldTicks = 0
    B_ReportLine2OldTicks = 0
    C_ReportLine2OldTicks = 0
    
    A_Line_State_Test_Pass_Count = 0
    A_Line_State_Test_Fail_Count = 0
    B_Line_State_Test_Pass_Count = 0
    B_Line_State_Test_Fail_Count = 0
    C_Line_State_Test_Pass_Count = 0
    C_Line_State_Test_Fail_Count = 0
    
    A_Line2_State_Test_Pass_Count = 0
    A_Line2_State_Test_Fail_Count = 0
    B_Line2_State_Test_Pass_Count = 0
    B_Line2_State_Test_Fail_Count = 0
    C_Line2_State_Test_Pass_Count = 0
    C_Line2_State_Test_Fail_Count = 0
    
    A_OnLineState = ''
    B_OnLineState = ''
    C_OnLineState = ''
    
    A_OnLineCount = 0
    B_OnLineCount = 0
    C_OnLineCount = 0
    
    A_OffLineCount = 0
    B_OffLineCount = 0
    C_OffLineCount = 0
    
    SaveRcvSerialData = ''
    
    Update_PER_A = 0.0
    Update_PER_B = 0.0
    Update_PER_C = 0.0
    
    RecordWave_PER_IA = 0.0
    RecordWave_PER_IB = 0.0
    RecordWave_PER_IC = 0.0

    RecordWave_PER_VA = 0.0
    RecordWave_PER_VB = 0.0
    RecordWave_PER_VC = 0.0
    
    global FwUpdateResponseCnt
    global FwUpdateResponseCnt_A
    global FwUpdateResponseCnt_B
    global FwUpdateResponseCnt_C
    
    global FwUpdateResponseOKCnt_A
    global FwUpdateResponseOKCnt_B
    global FwUpdateResponseOKCnt_C
    
    global FwUpdateResponseErCnt_A
    global FwUpdateResponseErCnt_B
    global FwUpdateResponseErCnt_C
    
    global FwWriteFlashCnt_A
    global FwWriteFlashCnt_B
    global FwWriteFlashCnt_C
    
    global ManualRecordWaveCnt
    global RecordWaveBroadcastCnt_I
    global RecordWaveBroadcastCnt_IA
    global RecordWaveBroadcastCnt_IB
    global RecordWaveBroadcastCnt_IC
    global RecordWaveResponseCnt_I
    global RecordWaveResponseCnt_IA
    global RecordWaveResponseCnt_IB
    global RecordWaveResponseCnt_IC
    
    global RecordWaveBroadcastCnt_V
    global RecordWaveBroadcastCnt_VA
    global RecordWaveBroadcastCnt_VB
    global RecordWaveBroadcastCnt_VC
    global RecordWaveResponseCnt_V
    global RecordWaveResponseCnt_VA
    global RecordWaveResponseCnt_VB
    global RecordWaveResponseCnt_VC
    
    global ZeroSequenceComponentUploadCnt_I
    global ZeroSequenceComponentUploadCnt_IA
    global ZeroSequenceComponentUploadCnt_IB
    global ZeroSequenceComponentUploadCnt_IC
    
    global FwUpdateTxCnt
    global FwUpdateTxCnt_A
    global FwUpdateTxCnt_B
    global FwUpdateTxCnt_C
    
    global FwUpdateTimeoutResendCnt_A
    global FwUpdateTimeoutResendCnt_B
    global FwUpdateTimeoutResendCnt_C
    
    global ZeroSeqASNIntervalOKCnt_A
    global ZeroSeqASNIntervalErCnt_A
    global ZeroSeqASNIntervalOKCnt_B
    global ZeroSeqASNIntervalErCnt_B
    global ZeroSeqASNIntervalOKCnt_C
    global ZeroSeqASNIntervalErCnt_C
    
    global ZeroSeqASN_PLC_A
    global ZeroSeqASN_PLC_B
    global ZeroSeqASN_PLC_C
    
    global ZeroSeqASNRepeatCnt_A
    global ZeroSeqASNRepeatCnt_B
    global ZeroSeqASNRepeatCnt_C
    
    NowTime = time.strftime("%Y-%m-%d %H-%M-%S",time.localtime())
        
    while True:
        while ser.inWaiting() > 0:
            RcvSerialData = ser.readline().decode('utf-8')
           
        if RcvSerialData != '':
            # print('\n串口接收数据:%s'%RcvSerialData)
            SaveRcvSerialData = RcvSerialData[0:-2]+'\n'  
             
            with open(r".\report\IWOC\433M_RcvSerialData_OC_15m " + NowTime + ".log","a+") as fp:
                fp.write(SaveRcvSerialData)
            
            CurrentTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            f = open(r".\report\IWOC\\433M_RFData_test_OC_15m " + NowTime + ".log","a+") 
            
            Get_OC_RSSI(RcvSerialData,f,CurrentTime)
            RF_CRC_Error_Cnt(RcvSerialData,f,CurrentTime)
            AcquUnitFwUpdate_PER(RcvSerialData,f,CurrentTime)
            UploadWave_PER(RcvSerialData,f,CurrentTime)
               
            DataLen = ''
            length = 0
            if RcvSerialData[0:4] == "5AA5":
                # print('\nnRcvBytes:',len(RcvSerialData)-2) #减去\r\n
                # print("Find Frame Header")
                RFData = RcvSerialData[0:-2]
                
                with open(r".\report\433M_RcvRFData_OC_15m.log","a+") as fps:
                    fps.write(RcvSerialData[0:-2]+'\n')
                
                print('\n'+RFData)
                word_checksum(RFData)
                Nick_Name = RFData[6:8]+RFData[4:6]
                # print('Nick_Name:',Nick_Name)
                    
                CMD = RFData[8:10]
                print('CMD:',CMD)
                
                DataLen = RFData[10:12]
                # print('DataLen :0x%s'%DataLen)
                
                length = int(DataLen,16)
                # print('DataLen(Bytes)：%s'%length)
                CurrentTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

                # f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                if CMD =='01':
                    print('\033[1;33m%s获取版本号\033[0m'%Nick_Name[-1])
                    f.write('%s %s获取版本号:\n'%(CurrentTime,Nick_Name[-1]))
                    
                if CMD =='02':
                    print('\033[1;33m%s获取邻居信息\033[0m'%Nick_Name[-1])
                    # f.write('%s %s获取邻居信息:\n'%(CurrentTime,Nick_Name[-1]))
                     
                elif CMD =='08':
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    FwUpdateTxCnt += 1
                    FwTotalLenHead = str(int(RFData[14:16],16) & 0x01)
                    # print('RFData[14:16]:%s FwTotalLenHead_0x08:%s'%(RFData[14:16],FwTotalLenHead))
                    if Nick_Name[-1] == 'A':
                        FwUpdateTxCnt_A += 1
                        NewFwVersion_A = RFData[14:16]+RFData[12:14]
                        FwTotalLen_A = int(FwTotalLenHead+RFData[18:20]+RFData[16:18],16)
                        UpdateOffset_A = int(RFData[22:24]+RFData[20:22],16)
                        print('\033[1;33mA相升级指令:\033[0m FwUpdateTxCnt_A:%s NewFwVersion_A:0x%s FwTotalLen_A(B):%s UpdateOffset_A(B):%s'%(FwUpdateTxCnt_A,NewFwVersion_A,FwTotalLen_A,UpdateOffset_A))
                        f.write('%s FwUpdateTxCnt_A:%s NewFwVersion_A:0x%s FwTotalLen_A(B):%s UpdateOffset_A(B):%s\n'%(CurrentTime,FwUpdateTxCnt_A,NewFwVersion_A,FwTotalLen_A,UpdateOffset_A))
                    if Nick_Name[-1] == 'B':
                        FwUpdateTxCnt_B += 1
                        NewFwVersion_B = RFData[14:16]+RFData[12:14]
                        FwTotalLen_B = int(FwTotalLenHead+RFData[18:20]+RFData[16:18],16)
                        UpdateOffset_B = int(RFData[22:24]+RFData[20:22],16)
                        print('\033[1;33mB相升级指令:\033[0m FwUpdateTxCnt_B:%s NewFwVersion_B:0x%s FwTotalLen_B(B):%s UpdateOffset_B(B):%s'%(FwUpdateTxCnt_B,NewFwVersion_B,FwTotalLen_B,UpdateOffset_B))
                        f.write('%s FwUpdateTxCnt_B:%s NewFwVersion_B:0x%s FwTotalLen_B(B):%s UpdateOffset_B(B):%s\n'%(CurrentTime,FwUpdateTxCnt_B,NewFwVersion_B,FwTotalLen_B,UpdateOffset_B))
                    if Nick_Name[-1] == 'C':
                        FwUpdateTxCnt_C += 1
                        NewFwVersion_C = RFData[14:16]+RFData[12:14]
                        FwTotalLen_C = int(FwTotalLenHead+RFData[18:20]+RFData[16:18],16)
                        UpdateOffset_C = int(RFData[22:24]+RFData[20:22],16)
                        print('\033[1;33mC相升级指令:\033[0m FwUpdateTxCnt_C:%s NewFwVersion_C:0x%s FwTotalLen_C(B):%s UpdateOffset_C(B):%s'%(FwUpdateTxCnt_C,NewFwVersion_C,FwTotalLen_C,UpdateOffset_C))
                        f.write('%s FwUpdateTxCnt_C:%s NewFwVersion_C:0x%s FwTotalLen_C(B):%s UpdateOffset_C(B):%s\n'%(CurrentTime,FwUpdateTxCnt_C,NewFwVersion_C,FwTotalLen_C,UpdateOffset_C))
                    
                    print('升级命令下发总计数:\033[1;33m%s\033[0m A相升级包发送计数:\033[1;33m%s\033[0m B相升级包发送计数:\033[1;32m%s\033[0m C相升级包发送计数:\033[1;31m%s\033[0m'%(FwUpdateTxCnt,FwUpdateTxCnt_A,FwUpdateTxCnt_B,FwUpdateTxCnt_C))
                    f.write('%s 升级命令下发总计数:%s A升级包发送计数:%s B升级包发送计数:%s C升级包发送计数:%s\n'%(CurrentTime,FwUpdateTxCnt,FwUpdateTxCnt_A,FwUpdateTxCnt_B,FwUpdateTxCnt_C))
                    
                    FwTotalLenHead = ''
                    NewFwVersion_A = ''
                    FwTotalLen_A = ''
                    UpdateOffset_A = ''
                    
                    NewFwVersion_B = ''
                    FwTotalLen_B = ''
                    UpdateOffset_B = ''
                    
                    NewFwVersion_C = ''
                    FwTotalLen_C = ''
                    UpdateOffset_C = ''
                    
                elif CMD == '10':
                    print('\033[1;33m0x%s：同步ASN\033[0m'%Nick_Name)
                    # f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    # f.write('%s 0x%s：同步ASN:\n'%(CurrentTime,Nick_Name[-1]))
                    
                elif CMD == '11':
                    # ManualRecordWaveCnt += 1
                    print('\033[1;33m%s手动触发录波\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s手动触发录波计数：%s\n'%(CurrentTime,Nick_Name[-1],ManualRecordWaveCnt))
                    
                    #触发录波可单独发给特定采集单元，也可以发给所有采集单元
                    TRIGGERED_NODE = RFData[14:16]+RFData[12:14]
                    print('触发录波者:',TRIGGERED_NODE)
                    TRIGGERED_ASN = RFData[26:28]+RFData[24:26]+RFData[22:24]+RFData[20:22]+RFData[18:20]+RFData[16:18]
                    print('触发录波的ASN：',TRIGGERED_ASN)
                    f.write('%s 触发录波者:%s 触发录波的ASN:%s\n'%(CurrentTime,TRIGGERED_NODE,TRIGGERED_ASN))
    
                elif CMD == '16':
                    print('\033[1;33m%s取电流录波\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取电流录波:\n'%(CurrentTime,Nick_Name[-1]))
                    
                    RecordWaveBroadcastCnt_I += 1
                    print('取电流录波广播包计数：\033[1;33m%s\033[0m'%RecordWaveBroadcastCnt_I)
                    f.write('%s 取电流录波广播包计数：%s\n'%(CurrentTime,RecordWaveBroadcastCnt_I))
                    
                    N_1 = RFData[12:14]
                    OFFSET_1 = RFData[14:16]
                    SIZE_1 = RFData[16:18]
                    print('X相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_1,OFFSET_1,SIZE_1))
                    f.write('%s X相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_1,OFFSET_1,SIZE_1))
                    if N_1 == 'FF' :
                        print('不希望取X相的录波数据')
                    if (int(OFFSET_1,16) & 0x10) == 0x10 :
                        print('\033[1;33m%s周波数据传输完毕\033[0m'%N_1)
                        f.write('%s %s周波数据传输完毕\n'%(CurrentTime,N_1))
                        # OFFSET_1 = 0
                    
                    N_2 = RFData[18:20]
                    OFFSET_2 = RFData[20:22]
                    SIZE_2 = RFData[22:24]
                    print('A相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_2,OFFSET_2,SIZE_2))
                    f.write('%s A相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_2,OFFSET_2,SIZE_2))
                    if N_2 == 'FF' :
                        print('不希望取A相的录波数据')
                    if N_2 != 'FF' :
                        RecordWaveBroadcastCnt_IA += 1
                    if (int(OFFSET_2,16) & 0x10) == 0x10 :
                        print('A相\033[1;33m%s\033[0m周波数据传输完毕'%N_2)
                        f.write('%s A相%s周波数据传输完毕\n'%(CurrentTime,N_2))
                        # OFFSET_2 = 0
                    
                    N_3 = RFData[24:26]
                    OFFSET_3 = RFData[26:28]
                    SIZE_3 = RFData[28:30]
                    print('B相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_3,OFFSET_3,SIZE_3))
                    f.write('%s B相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_3,OFFSET_3,SIZE_3))
                    if N_3 == 'FF' :
                        print('不希望取B相的录波数据')
                    if N_3 != 'FF' :
                        RecordWaveBroadcastCnt_IB += 1
                    if (int(OFFSET_3,16) & 0x10) == 0x10 :
                        print('B相\033[1;33m%s\033[0m周波数据传输完毕'%N_3)
                        f.write('%s B相%s周波数据传输完毕\n'%(CurrentTime,N_3))
                        # OFFSET_3 = 0
                        
                    N_4 = RFData[30:32]
                    OFFSET_4 = RFData[32:34]
                    SIZE_4 = RFData[34:36]
                    print('C相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_4,OFFSET_4,SIZE_4))
                    f.write('%s C相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_4,OFFSET_4,SIZE_4))
                    if N_4 == 'FF' :
                        print('不希望取C相的录波数据')
                    if N_4 != 'FF' :
                        RecordWaveBroadcastCnt_IC += 1
                    if (int(OFFSET_4,16) & 0x10) == 0x10 :
                        print('C相\033[1;33m%s\033[0m周波数据传输完毕'%N_4)
                        f.write('%s C相%s周波数据传输完毕\n'%(CurrentTime,N_4))
                        # OFFSET_4 = 0
                    print('A相电流录波广播计数：\033[1;33m%s\033[0m B相电流录波广播计数：\033[1;32m%s\033[0m C相电流录波广播计数：\033[1;31m%s\033[0m'%(RecordWaveBroadcastCnt_IA,RecordWaveBroadcastCnt_IB,RecordWaveBroadcastCnt_IC))
                    f.write('%s A相电流录波广播计数：%s B相电流录波广播计数：%s C相电流录波广播计数：%s\n'%(CurrentTime,RecordWaveBroadcastCnt_IA,RecordWaveBroadcastCnt_IB,RecordWaveBroadcastCnt_IC))

                elif CMD == '18':
                    print('\033[1;33m%s取瞬态电流录波\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取瞬态电流录波:\n'%(CurrentTime,Nick_Name[-1]))
                                        
                elif CMD == '19':
                    print('\033[1;33m%s取电场录波\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取电场录波:\n'%(CurrentTime,Nick_Name[-1]))
                    
                    RecordWaveBroadcastCnt_V += 1
                    print('电场录波广播包计数：%s'%RecordWaveBroadcastCnt_V)
                    f.write('%s 电场录波广播包计数：%s\n'%(CurrentTime,RecordWaveBroadcastCnt_V))
                    
                    N_1 = RFData[12:14]
                    OFFSET_1 = RFData[14:16]
                    SIZE_1 = RFData[16:18]
                    print('X相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_1,OFFSET_1,SIZE_1))
                    f.write('%s X相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_1,OFFSET_1,SIZE_1))
                    if N_1 == 'FF' :
                        print('不希望取X相的录波数据')
                    if (int(OFFSET_1,16) & 0x10) == 0x10:
                        print('\033[1;33m%s周波数据传输完毕\033[0m'%N_1)
                        f.write('%s %s周波数据传输完毕\n'%(CurrentTime,N_1))
                        # OFFSET_1 = 0
                    
                    N_2 = RFData[18:20]
                    OFFSET_2 = RFData[20:22]
                    SIZE_2 = RFData[22:24]
                    print('A相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_2,OFFSET_2,SIZE_2))
                    f.write('%s A相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_2,OFFSET_2,SIZE_2))
                    if N_2 == 'FF' :
                        print('不希望取A相的录波数据')
                    if N_2 != 'FF' :
                        RecordWaveBroadcastCnt_VA += 1
                    if (int(OFFSET_2,16) & 0x10) == 0x10:
                        print('\033[1;33m%s周波数据传输完毕\033[0m'%N_2)
                        f.write('%s A相%s周波数据传输完毕\n'%(CurrentTime,N_2))
                        # OFFSET_2 = 0
                    
                    N_3 = RFData[24:26]
                    OFFSET_3 = RFData[26:28]
                    SIZE_3 = RFData[28:30]
                    print('B相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_3,OFFSET_3,SIZE_3))
                    f.write('%s B相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_3,OFFSET_3,SIZE_3))
                    if N_3 == 'FF' :
                        print('不希望取B相的录波数据')
                    if N_3 != 'FF' :
                        RecordWaveBroadcastCnt_VB += 1
                    if (int(OFFSET_3,16) & 0x10) == 0x10:
                        print('\033[1;33m%s周波数据传输完毕\033[0m'%N_3)
                        f.write('%s B相%s周波数据传输完毕\n'%(CurrentTime,N_3))
                        # OFFSET_3 = 0
                        
                    N_4 = RFData[30:32]
                    OFFSET_4 = RFData[32:34]
                    SIZE_4 = RFData[34:36]
                    print('C相周波编号：%s,偏移地址：%s,剩余文件长度：%s'%(N_4,OFFSET_4,SIZE_4))
                    f.write('%s C相周波编号：%s,偏移地址：%s,剩余文件长度：%s\n'%(CurrentTime,N_4,OFFSET_4,SIZE_4))
                    if N_4 == 'FF' :
                        print('不希望取C相的录波数据')
                    if N_4 != 'FF' :
                        RecordWaveBroadcastCnt_VC += 1
                    if (int(OFFSET_4,16) & 0x10) == 0x10:
                        print('\033[1;33m%s周波数据传输完毕\033[0m'%N_4)
                        f.write('%s C相%s周波数据传输完毕\n'%(CurrentTime,N_4))
                        # OFFSET_4 = 0
                    print('A相电场录波广播计数：\033[1;33m%s\033[0m B相电场录波广播计数：\033[1;32m%s\033[0m C相电场录波广播计数：\033[1;31m%s\033[0m'%(RecordWaveBroadcastCnt_VA,RecordWaveBroadcastCnt_VB,RecordWaveBroadcastCnt_VC))
                    f.write('%s A相电场录波广播计数：%s B相电场录波广播计数：%s C相电场录波广播计数：%s\n'%(CurrentTime,RecordWaveBroadcastCnt_VA,RecordWaveBroadcastCnt_VB,RecordWaveBroadcastCnt_VC))
                    
                elif CMD == '1B':
                    print('\033[1;33m%s解除录波锁定状态\033[0m'%Nick_Name[-1])
                    #解除录波锁定状态可单独发给特定采集单元，也可以发给所有采集单元。
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s解除录波锁定状态:\n'%(CurrentTime,Nick_Name[-1]))
                    
                elif CMD == '81':
                    print('\033[1;36m%s获取版本号响应帧:\033[0m'%Nick_Name[-1])

                    SN = binascii.a2b_hex(bytes(RFData[12:44],'utf-8'))
                    print('采集单元序列号:',SN[:-1])
                    APP_TYPE = RFData[46:48]+RFData[44:46]
                    print('应用类型:',APP_TYPE)
                    PROTO_VERSION = RFData[50:52]+RFData[48:50]
                    print('协议类型:',PROTO_VERSION)
                    BACKUP_FW_VER = RFData[54:56]+RFData[52:54]
                    print('备份区固件的版本号:',BACKUP_FW_VER)
                    HW_VER = RFData[58:60]+RFData[56:58]
                    print('硬件版本号:',HW_VER)
                    PARENT_ADDR = RFData[62:64]+RFData[60:62]
                    print('父节点地址（预留）:',PARENT_ADDR)
                    RSSI = RFData[64:66]
                    print('信号值（预留）:',RSSI)
                    FW_OFFSET_HIGH = RFData[66:68]
                    print('升级中固件的偏移值高字节:',FW_OFFSET_HIGH)
                    TIME_ERROR = RFData[70:72]+RFData[68:70]
                    print('时钟偏差（注意，特定bit有特殊含义）:',TIME_ERROR)
                    FW_NEW_VER = RFData[74:76]+RFData[72:74]
                    print('升级中固件的版本号:',FW_NEW_VER)
                    FW_TOTAL = RFData[78:80]+RFData[76:78]
                    print('升级中固件的总长度低16bit:',FW_TOTAL)
                    FW_OFFSET = RFData[82:84]+RFData[80:82]
                    print('升级中固件的偏移值低16bit:',FW_OFFSET)
                    IF_A = RFData[86:88]+RFData[84:86]
                    print('A相定标系数:',IF_A)
                    CURRENT_FW_VER = RFData[90:92]+RFData[88:90]
                    print('当前使用固件的版本号:',CURRENT_FW_VER)
                    CFG_VER = RFData[92:94]
                    print('配置版本号（每配置一次加一）:',CFG_VER)
                    IF_B = RFData[96:98]+RFData[94:96]
                    print('B相定标系数:',IF_B)
                    IF_C = RFData[100:102]+RFData[98:100]
                    print('C相定标系数:',IF_C)

                    f.write('%s %s获取版本号响应帧：%s球序列号：%s 应用类型：%s 协议类型：%s 备份固件版本:%s 硬件版本：%s 升级中固件版本：%s 定标系数:%s 当前使用版本：%s\n'%(CurrentTime,Nick_Name[-1].upper(),Nick_Name[-1].upper(),SN[:-1],APP_TYPE,PROTO_VERSION,BACKUP_FW_VER,HW_VER,FW_NEW_VER,IF_A,CURRENT_FW_VER))
                    SN = ''
                    APP_TYPE = ''
                    PROTO_VERSION = ''
                    BACKUP_FW_VER = ''
                    HW_VER = ''
                    FW_NEW_VER = ''
                    IF_A = ''
                    CURRENT_FW_VER = ''
                     
                elif CMD == '82':
                    print('\033[1;36m%s获取邻居信息响应帧\033[0m'%Nick_Name[-1]) 
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s获取邻居信息响应帧:\n'%(CurrentTime,Nick_Name[-1]))
                    DataLen = int(DataLen,16)
                    if DataLen >= 6 :
                        NetworkID_1 = RFData[12:16]
                        AcqUnitNmae_1 = RFData[16:20]
                        AcqUnitID_1 = RFData[22:24]+RFData[20:22]
                        if AcqUnitNmae_1 == 'A00A' :
                            A_OnLineState = 'OnLine'
                            A_OnLineCount += 1
                        if AcqUnitNmae_1 == 'B00B' :
                            B_OnLineState = 'OnLine'
                            B_OnLineCount += 1
                        if AcqUnitNmae_1 == 'C00C' :
                            C_OnLineState = 'OnLine'
                            C_OnLineCount += 1
                        # f.write('%s %s球：0x%s OnLine\n'%(CurrentTime,AcqUnitNmae_1[-1],AcqUnitID_1))  
                        
                    if DataLen >= 12 :
                        NetworkID_2 = RFData[24:28]
                        AcqUnitNmae_2 = RFData[28:32]
                        AcqUnitID_2 = RFData[34:36]+RFData[32:34]
                        if AcqUnitNmae_2 == 'A00A' :
                            A_OnLineState = 'OnLine'
                            A_OnLineCount += 1
                        if AcqUnitNmae_2 == 'B00B' :
                            B_OnLineState = 'OnLine'
                            B_OnLineCount += 1
                        if AcqUnitNmae_2 == 'C00C' :
                            C_OnLineState = 'OnLine'
                            C_OnLineCount += 1
                        # f.write('%s %s球：0x%s OnLine\n'%(CurrentTime,AcqUnitNmae_2[-1],AcqUnitID_2))
                        
                    if DataLen >= 18 :
                        NetworkID_3 = RFData[36:40]
                        AcqUnitNmae_3 = RFData[40:44]
                        AcqUnitID_3 = RFData[46:48]+RFData[44:46]
                        if AcqUnitNmae_3 == 'A00A' :
                            A_OnLineState = 'OnLine'
                            A_OnLineCount += 1
                        if AcqUnitNmae_3 == 'B00B' :
                            B_OnLineState = 'OnLine'
                            B_OnLineCount += 1
                        if AcqUnitNmae_3 == 'C00C' :
                            C_OnLineState = 'OnLine'
                            C_OnLineCount += 1
                        # f.write('%s %s球：0x%s OnLine\n'%(CurrentTime,AcqUnitNmae_3[-1],AcqUnitID_3))
                        
                    print('\033[1;36m网络号：%s\nA球：%s\nB球：%s\nC球：%s\033[0m'%(NetworkID,A_OnLineState,B_OnLineState,C_OnLineState))
                    f.write('%s 网络号：%s A球：%s B球：%s C球：%s\n'%(CurrentTime,NetworkID,A_OnLineState,B_OnLineState,C_OnLineState))
                    f.write('%s 网络号：%s A球上线次数：%s B球上线次数：%s C球上线次数：%s\n'%(CurrentTime,NetworkID,A_OnLineCount,B_OnLineCount,C_OnLineCount))
                    NetworkID_1 = ''
                    AcqUnitNmae_1 = ''
                    AcqUnitID_1 = ''
                    NetworkID_2 = ''
                    AcqUnitNmae_2 = ''
                    AcqUnitID_2 = ''
                    NetworkID_3 = ''
                    AcqUnitNmae_3 = ''
                    AcqUnitID_3 = ''
                    
                elif CMD =='83':
                    print('\033[1;36m%s邻居下线\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s邻居下线:\n'%(CurrentTime,Nick_Name[-1]))
                    NetworkID = RFData[12:16]
                    AcqUnitNmae = RFData[16:20]
                    AcqUnitID = RFData[22:24]+RFData[20:22]
                    if AcqUnitNmae == 'A00A' :
                        A_OnLineState = 'OffLine'
                        A_OffLineCount += 1
                        # print('A球：0x%s OffLine'%AcqUnitID)
                    if AcqUnitNmae == 'B00B' :
                        B_OnLineState = 'OffLine'
                        B_OffLineCount += 1
                        # print('B球：0x%s OffLine'%AcqUnitID)
                    if AcqUnitNmae == 'C00C' :
                        C_OnLineState = 'OffLine'
                        C_OffLineCount += 1
                        # print('C球：0x%s OffLine'%AcqUnitID)
                    
                    print('\033[1;36m网络号：%s\n A球：%s\n B球：%s\n C球：%s\033[0m'%(NetworkID,A_OnLineState,B_OnLineState,C_OnLineState))
                    f.write('%s 网络号：%s A球：%s B球：%s C球：%s\n'%(CurrentTime,NetworkID,A_OnLineState,B_OnLineState,C_OnLineState))
                    f.write('%s 网络号：%s A球下线次数：%s B球下线次数：%s C球下线次数：%s\n'%(CurrentTime,NetworkID,A_OffLineCount,B_OffLineCount,C_OffLineCount))
                    
                    NetworkID = ''
                    AcqUnitNmae = ''
                    AcqUnitID = ''
                    
                elif CMD == '88':
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    FwUpdateResponseCnt += 1
                    FwTotalLenHead = str(int(RFData[22:24],16) & 0x01)
                    # print('RFData[22:24]:%s FwTotalLenHead_0x88:%s'%(RFData[22:24],FwTotalLenHead))
                    if Nick_Name[-1] == 'A':
                        FwUpdateResponseCnt_A += 1
                        FwUpdateStatet_A = RFData[12:16]
                        if FwUpdateStatet_A == 'F5FF':
                            FwWriteFlashCnt_A += 1
                        elif FwUpdateStatet_A == '0000':
                            FwUpdateResponseOKCnt_A += 1
                        else:
                            FwUpdateResponseErCnt_A += 1
                        if FwUpdateTxCnt_A > 0: 
                            Update_PER_A = abs(FwUpdateTxCnt_A-FwUpdateResponseCnt_A+FwWriteFlashCnt_A+FwUpdateResponseErCnt_A+FwUpdateTimeoutResendCnt_A)/FwUpdateTxCnt_A
                        
                        OldFwVersion_A = RFData[18:20]+RFData[16:18]
                        NewFwVersion_A = RFData[22:24]+RFData[20:22]
                        FwTotalLen_A = int(FwTotalLenHead+RFData[26:28]+RFData[24:26],16)
                        UpdateOffset_A = int(RFData[32:34]+RFData[30:32]+RFData[28:30],16)
                        UpdatePercent_A = (UpdateOffset_A / FwTotalLen_A)*100
                        if RFData[26:28]+RFData[24:26] == RFData[30:32]+RFData[28:30]:
                            UpdatePercent_A = 100.0
                        print('\033[1;36mA相升级响应:\033[0m 升级响应计数:\033[1;33m%s\033[0m OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s Updating_A:\033[1;32m%.2f%%\033[0m'%(FwUpdateResponseCnt_A,OldFwVersion_A,NewFwVersion_A,FwTotalLen_A,UpdateOffset_A,UpdatePercent_A))
                        f.write('%s A相升级响应: 升级响应计数:%s OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s\n'%(CurrentTime,FwUpdateResponseCnt_A,OldFwVersion_A,NewFwVersion_A,FwTotalLen_A,UpdateOffset_A))
                        print('A相发包计数:\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_A,FwUpdateResponseOKCnt_A + FwUpdateResponseErCnt_A,FwUpdateResponseOKCnt_A,FwUpdateResponseErCnt_A,FwWriteFlashCnt_A,FwUpdateTimeoutResendCnt_A))
                        f.write('%s A相发包计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_A,FwUpdateResponseOKCnt_A + FwUpdateResponseErCnt_A,FwUpdateResponseOKCnt_A,FwUpdateResponseErCnt_A,FwWriteFlashCnt_A,FwUpdateTimeoutResendCnt_A))
                    if FwUpdateTxCnt_A == 0 or FwUpdateResponseCnt_A == 0 :
                        Update_PER_A = 1.0
                        
                    if Nick_Name[-1] == 'B':
                        FwUpdateResponseCnt_B += 1
                        FwUpdateStatet_B = RFData[12:16]
                        if FwUpdateStatet_B == 'F5FF':
                            FwWriteFlashCnt_B += 1
                        elif FwUpdateStatet_B == '0000':
                            FwUpdateResponseOKCnt_B += 1
                        else:
                            FwUpdateResponseErCnt_B += 1
                        if FwUpdateTxCnt_B > 0:
                            Update_PER_B = abs(FwUpdateTxCnt_B-FwUpdateResponseCnt_B+FwWriteFlashCnt_B+FwUpdateResponseErCnt_B+FwUpdateTimeoutResendCnt_B)/FwUpdateTxCnt_B
                        
                        OldFwVersion_B = RFData[18:20]+RFData[16:18]
                        NewFwVersion_B = RFData[22:24]+RFData[20:22]
                        FwTotalLen_B = int(FwTotalLenHead+RFData[26:28]+RFData[24:26],16)
                        UpdateOffset_B = int(RFData[32:34]+RFData[30:32]+RFData[28:30],16)
                        UpdatePercent_B = (UpdateOffset_B / FwTotalLen_B)*100
                        if RFData[26:28]+RFData[24:26] == RFData[30:32]+RFData[28:30]:
                            UpdatePercent_B = 100.0
                        print('\033[1;36mB相升级响应:\033[0m 升级响应计数:\033[1;33m%s\033[0m OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s Updating_B:\033[1;32m%.2f%%\033[0m'%(FwUpdateResponseCnt_B,OldFwVersion_B,NewFwVersion_B,FwTotalLen_B,UpdateOffset_B,UpdatePercent_B))
                        f.write('%s B相升级响应: 升级响应计数:%s OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s\n'%(CurrentTime,FwUpdateResponseCnt_B,OldFwVersion_B,NewFwVersion_B,FwTotalLen_B,UpdateOffset_B))
                        print('B相发包计数:\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_B,FwUpdateResponseOKCnt_B + FwUpdateResponseErCnt_B,FwUpdateResponseOKCnt_B,FwUpdateResponseErCnt_B,FwWriteFlashCnt_B,FwUpdateTimeoutResendCnt_B))
                        f.write('%s B相发包计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_B,FwUpdateResponseOKCnt_B + FwUpdateResponseErCnt_B,FwUpdateResponseOKCnt_B,FwUpdateResponseErCnt_B,FwWriteFlashCnt_B,FwUpdateTimeoutResendCnt_B))
                    if FwUpdateTxCnt_B == 0 or FwUpdateResponseCnt_B == 0 :
                        Update_PER_B = 1.0
                        
                    if Nick_Name[-1] == 'C':
                        FwUpdateResponseCnt_C += 1
                        FwUpdateStatet_C = RFData[12:16]
                        if FwUpdateStatet_C == 'F5FF':
                            FwWriteFlashCnt_C += 1
                        elif FwUpdateStatet_C == '0000':
                            FwUpdateResponseOKCnt_C += 1
                        else:
                            FwUpdateResponseErCnt_C += 1
                        if FwUpdateTxCnt_C > 0:
                            Update_PER_C = abs(FwUpdateTxCnt_C-FwUpdateResponseCnt_C+FwWriteFlashCnt_C+FwUpdateResponseErCnt_C+FwUpdateTimeoutResendCnt_C)/FwUpdateTxCnt_C
                        
                        OldFwVersion_C = RFData[18:20]+RFData[16:18]
                        NewFwVersion_C = RFData[22:24]+RFData[20:22]
                        FwTotalLen_C = int(FwTotalLenHead+RFData[26:28]+RFData[24:26],16)
                        UpdateOffset_C = int(RFData[32:34]+RFData[30:32]+RFData[28:30],16)
                        UpdatePercent_C = (UpdateOffset_C / FwTotalLen_C)*100
                        if RFData[26:28]+RFData[24:26] == RFData[30:32]+RFData[28:30]:
                            UpdatePercent_C = 100.0
                        print('\033[1;36mC相升级响应:\033[0m 升级响应计数:\033[1;33m%s\033[0m OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s Updating_C:\033[1;32m%.2f%%\033[0m'%(FwUpdateResponseCnt_C,OldFwVersion_C,NewFwVersion_C,FwTotalLen_C,UpdateOffset_C,UpdatePercent_C))
                        f.write('%s C相升级响应: 升级响应计数:%s OldFwVersion:0x%s NewFwVersion:0x%s FwTotalLen(B):%s UpdateOffset(B):%s\n'%(CurrentTime,FwUpdateResponseCnt_C,OldFwVersion_C,NewFwVersion_C,FwTotalLen_C,UpdateOffset_C)) 
                        print('C相发包计数:\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_C,FwUpdateResponseOKCnt_C + FwUpdateResponseErCnt_C,FwUpdateResponseOKCnt_C,FwUpdateResponseErCnt_C,FwWriteFlashCnt_C,FwUpdateTimeoutResendCnt_C))
                        f.write('%s C相发包计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_C,FwUpdateResponseOKCnt_C + FwUpdateResponseErCnt_C,FwUpdateResponseOKCnt_C,FwUpdateResponseErCnt_C,FwWriteFlashCnt_C,FwUpdateTimeoutResendCnt_C))
                    if FwUpdateTxCnt_C == 0 or FwUpdateResponseCnt_C == 0 :
                        Update_PER_C = 1.0
                    
                    print('\n升级响应帧总计数:\033[1;36m%s\033[0m A相升级响应计数:\033[1;33m%s\033[0m B相升级响应计数:\033[1;32m%s\033[0m C相升级响应计数:\033[1;31m%s\033[0m'%(FwUpdateResponseCnt,FwUpdateResponseCnt_A,FwUpdateResponseCnt_B,FwUpdateResponseCnt_C)) 
                    f.write('%s 升级响应帧总计数:%s A相升级响应计数:%s B相升级响应计数:%s C相升级响应计数:%s\n'%(CurrentTime,FwUpdateResponseCnt,FwUpdateResponseCnt_A,FwUpdateResponseCnt_B,FwUpdateResponseCnt_C))
                    print('A相升级PER:\033[1;33m{:.2%}\033[0m B相升级PER:\033[1;32m{:.2%}\033[0m C相升级PER:\033[1;31m{:.2%}\033[0m'.format(Update_PER_A,Update_PER_B,Update_PER_C))
                    f.write('{0} A相升级PER:{1:.2%} B相升级PER:{2:.2%} C相升级PER:{3:.2%}\n'.format(CurrentTime,Update_PER_A,Update_PER_B,Update_PER_C))
                    
                    FwTotalLenHead = ''
                    FwUpdateStatet_A = ''
                    FwUpdateStatet_B = ''
                    FwUpdateStatet_C = ''
                    
                    OldFwVersion_A = ''
                    NewFwVersion_A = ''
                    FwTotalLen_A = 0
                    UpdateOffset_A = 0
                    
                    OldFwVersion_B = ''
                    NewFwVersion_B = ''
                    FwTotalLen_B = 0
                    UpdateOffset_B = 0
                    
                    OldFwVersion_C = ''
                    NewFwVersion_C = ''
                    FwTotalLen_C = 0
                    UpdateOffset_C = 0
                    
                elif CMD == '90':
                    print('\033[1;36m%s同步ASN响应帧\033[0m'%Nick_Name[-1]) 
                    # f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    # f.write('%s %s同步ASN响应帧:\n'%(CurrentTime,Nick_Name[-1]))
                    
                elif CMD == '91':
                    print('\033[1;36m%s手动触发录波响应帧\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s手动触发录波响应帧:\n'%(CurrentTime,Nick_Name[-1]))
                    
                elif CMD == '92':
                    print('\033[1;36m%s线路状态1上报\033[0m'%Nick_Name[-1])
                    # f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    # f.write('%s %s线路状态1上报:\n'%(CurrentTime,Nick_Name[-1]))

                    if Nick_Name[-1] == 'A' : 
                        # print (time.strftime("A_ReportLineTime: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))
                        if Ai == 0 :
                            A_ReportLineOldTicks = time.time()
                            # print('A_ReportLineOldTicks：%s'%A_ReportLineOldTicks)
                        Ai += 1
                        print('A上报计数:%s'%Ai)
                        A_ReportLineInterval = 0.0
                        if Ai > 1 :
                            A_ReportLineNewTicks = time.time()
                            # print('A_ReportLineNewTicks：%s'%A_ReportLineNewTicks)
                            A_ReportLineInterval = A_ReportLineNewTicks - A_ReportLineOldTicks
                            print('A线路状态1上报间隔(s):%.2f'%A_ReportLineInterval) 
                            # f.write('%s A线路状态1上报间隔(s):%.2f\n'%(CurrentTime,A_ReportLineInterval))
                            A_ReportLineOldTicks = A_ReportLineNewTicks
                            if A_ReportLineInterval < 31.0:
                                print ('A线路状态1上报间隔测试：\033[1;32mPass\033[0m')
                                A_Line_State_Test_Pass_Count += 1
                                # f.write('%s A线路状态1上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('A线路状态1上报间隔测试：\033[1;31mFail\033[0m')
                                A_Line_State_Test_Fail_Count += 1
                                # f.write('%s A线路状态1上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s A线路状态1测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Ai-1,A_Line_State_Test_Pass_Count,A_Line_State_Test_Fail_Count))
                        # f.write('%s A线路状态1上报计数：%s\n'%(CurrentTime,Ai))
                         
                    if Nick_Name[-1] == 'B' :
                        # print (time.strftime("B_ReportLineTime: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))
                        if Bi == 0 :
                            B_ReportLineOldTicks = time.time()
                            # print('B_ReportLineOldTicks：%s'%B_ReportLineOldTicks)
                        Bi += 1
                        print('B上报计数:%s'%Bi)
                        B_ReportLineInterval = 0.0
                        if Bi > 1 :
                            B_ReportLineNewTicks = time.time()
                            # print('B_ReportLineNewTicks：%s'%B_ReportLineNewTicks)
                            B_ReportLineInterval = B_ReportLineNewTicks - B_ReportLineOldTicks
                            print('B线路状态1上报间隔(s):%.2f'%B_ReportLineInterval) 
                            # f.write('%s B线路状态1上报间隔(s):%.2f\n'%(CurrentTime,B_ReportLineInterval))
                            B_ReportLineOldTicks = B_ReportLineNewTicks
                            if B_ReportLineInterval < 31.0:
                                print ('B线路状态1上报间隔测试：\033[1;32mPass\033[0m')
                                B_Line_State_Test_Pass_Count += 1
                                # f.write('%s B线路状态1上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('B线路状态1上报间隔测试：\033[1;31mFail\033[0m')
                                B_Line_State_Test_Fail_Count += 1
                                # f.write('%s B线路状态1上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s B线路状态1测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Bi-1,B_Line_State_Test_Pass_Count,B_Line_State_Test_Fail_Count))
                        # f.write('%s B线路状态1上报计数：%s\n'%(CurrentTime,Bi))
                    
                    if Nick_Name[-1] == 'C' :
                        # print (time.strftime("C_ReportLineTime: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))
                        if Ci == 0 :
                            C_ReportLineOldTicks = time.time()
                            # print('C_ReportLineOldTicks：%s'%C_ReportLineOldTicks)
                        Ci += 1
                        print('C上报计数:%s'%Ci)
                        C_ReportLineInterval = 0.0
                        if Ci > 1 :
                            C_ReportLineNewTicks = time.time()
                            # print('C_ReportLineNewTicks：%s'%C_ReportLineNewTicks)
                            C_ReportLineInterval = C_ReportLineNewTicks - C_ReportLineOldTicks
                            print('C线路状态1上报间隔(s):%.2f'%C_ReportLineInterval) 
                            # f.write('%s C线路状态1上报间隔(s):%.2f\n'%(CurrentTime,C_ReportLineInterval))
                            C_ReportLineOldTicks = C_ReportLineNewTicks
                            if C_ReportLineInterval < 31.0:
                                print ('C线路状态1上报间隔测试：\033[1;32mPass\033[0m')
                                C_Line_State_Test_Pass_Count += 1
                                # f.write('%s C线路状态1上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('C线路状态1上报间隔测试：\033[1;31mFail\033[0m')
                                C_Line_State_Test_Fail_Count += 1
                                # f.write('%s C线路状态上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s C线路状态1测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Ci-1,C_Line_State_Test_Pass_Count,C_Line_State_Test_Fail_Count))
                        # f.write('%s C线路状态1上报计数：%s\n'%(CurrentTime,Ci))
                                                
                    Vef = RFData[14:16]+RFData[12:14]
                    # print('电场Hex:',Vef)
                    Vef = int(Vef,16)
                    print('电场(V):%d'%Vef)
                    
                    I = RFData[18:20]+RFData[16:18]
                    # print('电流Hex:',I)
                    I = int(I,16)/10.0
                    print('电流(A):%.2f'%I)
                    
                    # IC = RFData[22:24]+RFData[20:22]
                    # print('C相电流Hex:',IC)
                    # IC = int(IC,16)
                    # print('C相电流Digit:',IC)
                    
                    # IZ = RFData[26:28]+RFData[24:26]
                    # print('零序电流Hex:',IZ)
                    # IZ = int(IZ,16)
                    # print('零序电流Digit:',IZ)
                    
                    TEMP_LOCAL = RFData[22:24]+RFData[20:22]
                    print('本地温度:0x%s'%TEMP_LOCAL)
                    # Temperature_Digit = int(TEMP_LOCAL,16)
                    # print('本地温度(℃):%s'%Temperature_C)
                    
                    TEMP_LOCAL = ''
                    # Temperature_Digit = 0
                    # Temperature_C = 0
                    
                    VBAT = RFData[26:28]+RFData[24:26]
                    # print('电池电压Hex:',VBAT)
                    VBAT =(int(VBAT,16)/4095)*2.5*3
                    print('电池电压(V):%.2f'%VBAT)
                    
                    VRDC = RFData[30:32]+RFData[28:30]
                    #print('VRDC电压Hex:%s'%VRDC)
                    VRDC = (int(VRDC,16)/4095)*5
                    print('VRDC电压(V):%.2f'%VRDC)
                    
                    # VSCAP = RFData[38:40]+RFData[36:38]
                    # print('超级电容电压Hex:',VSCAP)
                    # VSCAP = int(VSCAP,16)
                    # print('超级电容电压Digit:',VSCAP)
                    
                    STATE_A = RFData[32:34]
                    print('线路状态:',STATE_A)
                    REASON_A = RFData[34:36]
                    print('录波触发原因:',REASON_A)
                    # STATE_B = RFData[44:46]
                    # print('B相线路状态:',STATE_B)
                    # REASON_B = RFData[46:48]
                    # print('B相录波触发原因:',REASON_B)
                    # STATE_C = RFData[48:50]
                    # print('C相线路状态:',STATE_C)
                    # REASON_C = RFData[50:52]
                    # print('C相录波触发原因:',REASON_C)
                    RSSI = RFData[36:38]
                    #print('信号值RSSI:',RSSI)
                    RSSI = int(RSSI,16)-256
                    print('RSSI:%sdBm'%RSSI)
                    f.write('%s %s__RSSI:%sdBm\n'%(CurrentTime,Nick_Name[-1],RSSI))
                    SYS_STATE = RFData[38:40]
                    # print('系统运行状态:',SYS_STATE)
                    if SYS_STATE == '02':
                        SYS_STATE = '正常模式'
                        print('系统运行状态:正常模式[%s]'%RFData[38:40])
                    else :
                        SYS_STATE = '休眠模式'
                        print('系统运行状态:休眠模式') #打印不出来，因为休眠时无输出。
                    
                    # BER = RFData[58:60]+RFData[56:58]
                    # print('误码率:',int(BER,16))
                    # WAVE_ASN = RFData[60:72]
                    # print('录波触发ASN:',WAVE_ASN)
                    
                    SLOTS_PER_JITTER = int(RFData[42:22] +RFData[40:42],16)
                    print('每多少个时隙需要调整一次:',SLOTS_PER_JITTER)
                                       
                    ASN_OR_UPTIME = RFData[44:46]
                    print('时间类型:',ASN_OR_UPTIME)
                    if ASN_OR_UPTIME == '00' :
                        print('后续字段采用ASN逻辑')
                        STOP_ASN_A = RFData[46:58]
                        SHORT_ASN_A = RFData[58:70]
                        SHORT_IPL_A = int(RFData[72:74]+RFData[70:72],16)
                        SHORT_IPL_INIT_A = int(RFData[76:78]+RFData[74:76],16)  
                        SHORT_ASN_INIT_A = RFData[78:90] 
                        print('停电时间:0x%s\n短路时间:0x%s\n短路电流(A):%s\n短路前电流(A):%s\n短路前时间:0x%s'%(STOP_ASN_A,SHORT_ASN_A,SHORT_IPL_A,SHORT_IPL_INIT_A,SHORT_ASN_INIT_A))
                        
                    elif ASN_OR_UPTIME == '01' :
                        print('后续字段采用UPTIME逻辑')
                        STOP_ASN_A = RFData[46:54]
                        SHORT_ASN_A = RFData[54:62]
                        SHORT_IPL_A = int(RFData[64:66]+RFData[62:64],16)
                        SHORT_IPL_INIT_A = int(RFData[68:70]+RFData[66:68],16)
                        # SHORT_ASN_INIT_A = RFData[70:78]
                        SHORT_ASN_INIT_A = RFData[76:78] + RFData[74:76] +RFData[72:74] + RFData[70:72]
                        print('停电时间:0x%s\n短路时间:0x%s\n短路电流(A):%s\n短路前电流(A):%s\n短路前时间:0x%s'%(STOP_ASN_A,SHORT_ASN_A,SHORT_IPL_A,SHORT_IPL_INIT_A,SHORT_ASN_INIT_A))
                    else :
                        print('时间类型:\033[1;31m未定义\033[0m')
                        # f.write(RcvSerialData[0:-2]+'\n')
                        continue
                    
                    # f.write('%s 电场(V):%.2f 电流(A):%.2f 本地温度:%s 电池电压(V):%.2f VRDC电压(V):%.2f 线路状态:%s 录波触发原因:%s 信号值:%sdBm 系统运行状态:%s 时隙调整间隔:%s 时间类型:%s 停电时间:0x%s 短路时间:0x%s 短路电流(A):%s 短路前电流(A):%s 短路前时间:0x%s\n'%(CurrentTime,Vef,I,TEMP_LOCAL,VBAT,VRDC,STATE_A,REASON_A,RSSI,SYS_STATE+'['+RFData[38:40]+']',SLOTS_PER_JITTER,ASN_OR_UPTIME,STOP_ASN_A,SHORT_ASN_A,SHORT_IPL_A,SHORT_IPL_INIT_A,SHORT_ASN_INIT_A))

                    Vef = ''
                    I = ''
                    TEMP_LOCAL = ''
                    VBAT = ''
                    VRDC = ''
                    STATE_A = ''
                    REASON_A = ''
                    RSSI = ''
                    SYS_STATE = ''
                    SLOTS_PER_JITTER = ''
                    ASN_OR_UPTIME = ''
                    STOP_ASN_A = ''
                    SHORT_ASN_A = ''
                    SHORT_IPL_A = ''
                    SHORT_IPL_INIT_A = ''
                    SHORT_ASN_INIT_A = ''
                    
                elif CMD == '96':
                    print('\033[1;36m%s取电流录波响应帧\033[0m'%Nick_Name[-1]) 
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取电流录波响应帧\n'%(CurrentTime,Nick_Name[-1]))
                    
                    TRIGGERED_ASN_L = RFData[14:16]+RFData[12:14]
                    print('触发录波的ASN.l:',TRIGGERED_ASN_L)
                    N = RFData[16:18]
                    print('录波文件的当前周波编号:',N)
                    OFFSET = RFData[18:20]
                    print('录波文件的当前偏移地址:',OFFSET)
                    
                    WAVE_FILE = RFData[20:-6]
                    print('录波文件正文:',WAVE_FILE)
                    f.write('%s 触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s 录波文件正文:%s'%(CurrentTime,TRIGGERED_ASN_L,N,OFFSET,WAVE_FILE))

                elif CMD == '98':
                    print('\033[1;36m%s取瞬态电流录波响应帧\033[0m'%Nick_Name[-1]) 
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取瞬态电流录波响应帧:\n'%(CurrentTime,Nick_Name[-1]))
                      
                elif CMD == '99':
                    print('\033[1;36m%s取电场录波响应帧\033[0m'%Nick_Name[-1]) 
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取电场录波响应帧:\n'%(CurrentTime,Nick_Name[-1]))
                    
                    TRIGGERED_ASN_L = RcvSerialData[64:66]+RcvSerialData[62:64]
                    print('触发录波的ASN.l:',TRIGGERED_ASN_L)
                    N = RcvSerialData[66:68]
                    print('录波文件的当前周波编号:',N)
                    OFFSET = RcvSerialData[68:70]
                    print('录波文件的当前偏移地址:',OFFSET)
                    
                    WAVE_FILE = RcvSerialData[70:-8]
                    print('录波文件正文:',WAVE_FILE)
                    f.write('%s 触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s 录波文件正文:%s'%(CurrentTime,TRIGGERED_ASN_L,N,OFFSET,WAVE_FILE))
                    
                elif CMD == '9D':
                    print('\033[1;36m%s线路状态2上报\033[0m'%Nick_Name[-1])
                    # f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    # f.write('%s %s线路状态2上报:\n'%(CurrentTime,Nick_Name[-1]))
                    
                    if Nick_Name[-1] == 'A' : 
                        # print (time.strftime("A_ReportLine2Time: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))

                        if Aj == 0:
                            A_ReportLine2OldTicks = time.time()
                            # print('A_ReportLine2OldTicks=%s'%A_ReportLine2OldTicks)
                        Aj += 1
                        print('A上报计数:%s'%Ai)
                        A_ReportLine2Interval = 0.0
                        if Aj > 1 :
                            A_ReportLine2NewTicks = time.time()
                            # print('A_ReportLine2NewTicks：%s'%A_ReportLine2NewTicks)
                            A_ReportLine2Interval = A_ReportLine2NewTicks - A_ReportLine2OldTicks
                            print('A线路状态2上报间隔(s):%.2f'%A_ReportLine2Interval) 
                            # f.write('%s A线路状态2上报间隔(s):%.2f\n'%(CurrentTime,A_ReportLine2Interval))
                            A_ReportLine2OldTicks = A_ReportLine2NewTicks
                            if A_ReportLine2Interval < 31.0:
                                print ('A线路状态2上报间隔测试：\033[1;32mPass\033[0m')
                                A_Line2_State_Test_Pass_Count += 1
                                # f.write('%s A线路状态2上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('A线路状态2上报间隔测试:：\033[1;31mFail\033[0m')
                                A_Line2_State_Test_Fail_Count += 1
                                # f.write('%s A线路状态2上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s A线路状态2测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Aj-1,A_Line2_State_Test_Pass_Count,A_Line2_State_Test_Fail_Count))
                        # f.write('%s A线路状态2上报计数：%s\n'%(CurrentTime,Aj))
                    
                    if Nick_Name[-1] == 'B' :
                        # print (time.strftime("B_ReportLine2Time: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))

                        if Bj == 0 :
                            B_ReportLine2OldTicks = time.time()
                            # print('B_ReportLine2OldTicks：%s'%B_ReportLine2OldTicks)
                        Bj += 1
                        print('B上报计数:%s'%Bi)
                        B_ReportLine2Interval = 0.0
                        if Bj > 1:
                            B_ReportLine2NewTicks = time.time()
                            # print('B_ReportLine2NewTicks：%s'%B_ReportLine2NewTicks)
                            B_ReportLine2Interval = B_ReportLine2NewTicks - B_ReportLine2OldTicks
                            print('B线路状态2上报间隔(s):%.2f'%B_ReportLine2Interval) 
                            # f.write('%s B线路状态2上报间隔(s):%.2f\n'%(CurrentTime,B_ReportLine2Interval))
                            B_ReportLine2OldTicks = B_ReportLine2NewTicks
                            if B_ReportLine2Interval < 31.0:
                                print ('B线路状态2上报间隔测试：\033[1;32mPass\033[0m')
                                B_Line2_State_Test_Pass_Count += 1
                                # f.write('%s B线路状态2上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('B线路状态2上报间隔测试：\033[1;31mFail\033[0m')
                                B_Line2_State_Test_Fail_Count += 1
                                # f.write('%s B线路状态2上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s B线路状态2测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Bj-1,B_Line2_State_Test_Pass_Count,B_Line2_State_Test_Fail_Count))
                        # f.write('%s B线路状态2上报计数：%s\n'%(CurrentTime,Bj))
                    
                    if Nick_Name[-1] == 'C' :
                        # print (time.strftime("C_ReportLine2Time: \033[1;32m%Y-%m-%d %H:%M:%S\033[0m",time.localtime()))

                        if Cj == 0 :
                            C_ReportLine2OldTicks = time.time()
                            # print('C_ReportLine2OldTicks：%s'%C_ReportLine2OldTicks)
                        Cj += 1
                        print('C上报计数:%s'%Ci)
                        C_ReportLine2Interval = 0.0
                        if Cj > 1 :
                            C_ReportLine2NewTicks = time.time()
                            # print('C_ReportLine2NewTicks：%s'%C_ReportLine2NewTicks)
                            C_ReportLine2Interval = C_ReportLine2NewTicks - C_ReportLine2OldTicks
                            print('C线路状态2上报间隔(s):%.2f'%C_ReportLine2Interval) 
                            # f.write('%s C线路状态2上报间隔(s):%.2f\n'%(CurrentTime,C_ReportLine2Interval))
                            C_ReportLine2OldTicks = C_ReportLine2NewTicks
                            if C_ReportLine2Interval < 31.0:
                                print ('C线路状态2上报间隔测试：\033[1;32mPass\033[0m')
                                C_Line2_State_Test_Pass_Count += 1
                                # f.write('%s C线路状态2上报间隔测试：Pass\n'%CurrentTime)
                            else:
                                print ('C线路状态2上报间隔测试：\033[1;31mFail\033[0m')
                                C_Line2_State_Test_Fail_Count += 1
                                # f.write('%s C线路状态2上报间隔测试：Fail\n'%CurrentTime)
                        # f.write('%s C线路状态2测试计数：%s, Pass次数：%s, Fail次数：%s\n'%(CurrentTime,Cj-1,C_Line2_State_Test_Pass_Count,C_Line2_State_Test_Fail_Count))
                        # f.write('%s C线路状态2上报计数：%s\n'%(CurrentTime,Cj))
                                               
                    LEN_NORMAL_PARA = RFData[12:14]
                    print('普通变量长度:',LEN_NORMAL_PARA)
                    
                    LINE_STATE2_A = RFData[14:16]
                    print('线路状态2:',LINE_STATE2_A)
                    if LINE_STATE2_A == '00' :
                        LINE_STATE2_A = LINE_STATE2_A+'[4kHz]'
                        print('运行状态:%s'%LINE_STATE2_A)
                    if LINE_STATE2_A == '04' :
                        LINE_STATE2_A = LINE_STATE2_A+'[800Hz]'
                        print('运行状态:%s'%LINE_STATE2_A)
                    LINE_EVENT2_A = RFData[16:18]
                    print('故障状态2:',LINE_EVENT2_A)
                    # LINE_STATE2_B = RFData[18:20]
                    # print('B相线路状态2:',LINE_STATE2_B)
                    # LINE_EVENT2_B = RFData[20:22]
                    # print('B相故障状态2:',LINE_EVENT2_B)
                    # LINE_STATE2_C = RFData[22:24]
                    # print('C相线路状态2:',LINE_STATE2_C)
                    # LINE_EVENT2_C = RFData[24:26]
                    # print('C相故障状态2:',LINE_EVENT2_C)
                    
                    BATT_STATE = RFData[18:20]
                    print('电池状态:',BATT_STATE)
                    BATT_EVENT = RFData[20:22]
                    print('电池事件:',BATT_EVENT)
                    
                    IA = RFData[24:26]+RFData[22:24]
                    # print('电流Hex:',IA)
                    IA = int(IA,16)/10.0
                    print('电流(A):%.2f'%IA)
                    
                    # IB = RFData[36:38]+RFData[34:36]
                    # print('B相电流Hex:',IB)
                    # IB = int(IB,16)
                    # print('B相电流Digit:',IB)
                    
                    # IC = RFData[40:42]+RFData[38:40]
                    # print('C相电流Hex:',IC)
                    # IC = int(IC,16)
                    # print('C相电流Digit:',IC)
                    
                    # IZ = RFData[44:46]+RFData[42:44]
                    # print('零序电流Hex:',IZ)
                    # IZ = int(IZ,16)
                    # print('零序电流Digit:',IZ)
                    
                    Vef = RFData[28:30]+RFData[26:28]
                    # print('电场Hex:',Vef)
                    Vef = int(Vef,16)/10.0
                    print('电场(V):%.2f'%Vef)
                    
                    # I_ASN = RFData[30:42] #6字节
                    I_ASN = RFData[40:42]+RFData[38:40]+RFData[36:38]+RFData[34:36]+RFData[32:34]+RFData[30:32]
                    print('上报电流对应的ASN:0x%s'%I_ASN)
                    # UPTIME = RFData[42:50] #4字节
                    UPTIME = RFData[48:50]+RFData[46:48]+RFData[44:46]+RFData[42:44]
                    UPTIME = int(UPTIME,16)
                    print('系统启动时间(s):',UPTIME)
                    VSCAP = RFData[52:54]+RFData[50:52]
                    VSCAP = (int(VSCAP,16)/4095)*2.5
                    print('超级电容电压(V):%.2f'%VSCAP)
                    
                    # VERSION_1310 = RFData[56:58]+RFData[54:56]
                    # print('1310版本号:',VERSION_1310)
                    RF_VERSION = RFData[56:58]+RFData[54:56]
                    print('1310版本号:0x%s'%RF_VERSION)
                    TEMP_LOCAL = RFData[58:60]
                    # print('本地温度_Hex:',TEMP_LOCAL)
                    Temperature = int(TEMP_LOCAL,16)-64
                    print('本地温度(℃):%.2f'%Temperature)
                    
                    # f.write('%s 线路状态2:%s 故障状态2:%s 电池状态:%s 电池事件:%s 电流(A):%.2f 电场(V):%.2f 上报电流对应的ASN:0x%s 系统启动时间(s):%s 超级电容电压(V):%.2f 1310版本号:0x%s 本地温度(℃):%s \n'%(CurrentTime,LINE_STATE2_A,LINE_EVENT2_A,BATT_STATE,BATT_EVENT,IA,Vef,I_ASN,UPTIME,VSCAP,RF_VERSION,Temperature))
                    
                    LINE_STATE2_A = ''
                    BATT_STATE = ''
                    BATT_EVENT = ''
                    IA = ''
                    Vef = ''
                    I_ASN = ''
                    UPTIME = ''
                    VSCAP = ''
                    RF_VERSION = ''
                    TEMP_LOCAL = ''
                    Temperature = 0 
                    
                elif CMD == '9F':
                    print('\033[1;36m%s零序分量上报\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s零序分量上报:\n'%(CurrentTime,Nick_Name[-1]))
                    ZeroSeqASNInterval_A = 0
                    ZeroSeqASNInterval_B = 0
                    ZeroSeqASNInterval_C = 0
                    if Nick_Name[-1] == 'A' : 
                        ZeroSequenceComponentUploadCnt_IA += 1
                        if ZeroSequenceComponentUploadCnt_IA <= 1:
                            OldASN_ZeroSeq_A = int(RcvSerialData[14:16] + RcvSerialData[12:14],16) 
                        else:
                            ZeroSeqASNInterval_A = 0
                            NewASN_ZeroSeq_A = int(RcvSerialData[14:16] + RcvSerialData[12:14],16)
                            if NewASN_ZeroSeq_A < OldASN_ZeroSeq_A:
                                ZeroSeqASNInterval_A = 65536 - OldASN_ZeroSeq_A + NewASN_ZeroSeq_A
                            else:
                                ZeroSeqASNInterval_A = NewASN_ZeroSeq_A - OldASN_ZeroSeq_A
                            print('NewASN_A:\033[1;32m%s\033[0m OldASN_A:\033[1;33m%s\033[0m ASN间隔:\033[1;36m%s\033[0m'%(NewASN_ZeroSeq_A,OldASN_ZeroSeq_A,ZeroSeqASNInterval_A))
                            
                            if ZeroSeqASNInterval_A == 16:
                                ZeroSeqASNIntervalOKCnt_A += 1
                                # print('A相ASN间隔正常计数:\033[1;32m%s\033[0m'%ZeroSeqASNIntervalOKCnt_A)
                            else:
                                ZeroSeqASNIntervalErCnt_A += 1
                                if math.floor(ZeroSeqASNInterval_A/16.0) < 2 :
                                    ZeroSeqASN_PLC_A += 0
                                if math.floor(ZeroSeqASNInterval_A/16.0) >= 2 and math.floor(ZeroSeqASNInterval_A/16.0) <= 100:
                                    ZeroSeqASN_PLC_A += math.floor(ZeroSeqASNInterval_A/16.0)-1
                                if math.floor(ZeroSeqASNInterval_A/16.0) > 100 and NewASN_ZeroSeq_A < OldASN_ZeroSeq_A :
                                    ZeroSeqASN_PLC_A += 0
                                    ZeroSeqASNRepeatCnt_A += 1

                                f.write('%s NewASN_A:%s OldASN_A:%s ASN间隔:%s A相ASN重发计数:%s\n'%(CurrentTime,NewASN_ZeroSeq_A,OldASN_ZeroSeq_A,ZeroSeqASNInterval_A,ZeroSeqASNRepeatCnt_A))
                                print('A相ASN间隔异常计数:\033[1;31m%s\033[0m A相ASN间隔：\033[1;31m%s\033[0m A相零序丢包计数:\033[1;31m%s\033[0m A相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSeqASNIntervalErCnt_A,ZeroSeqASNInterval_A,ZeroSeqASN_PLC_A,ZeroSeqASNRepeatCnt_A))
                            OldASN_ZeroSeq_A = NewASN_ZeroSeq_A
                                
                    if Nick_Name[-1] == 'B' :
                        ZeroSequenceComponentUploadCnt_IB += 1
                        if ZeroSequenceComponentUploadCnt_IB <= 1:
                            OldASN_ZeroSeq_B = int(RcvSerialData[14:16] + RcvSerialData[12:14],16)
                        else:
                            ZeroSeqASNInterval_B = 0
                            NewASN_ZeroSeq_B = int(RcvSerialData[14:16] + RcvSerialData[12:14],16)
                            if NewASN_ZeroSeq_B < OldASN_ZeroSeq_B:
                                ZeroSeqASNInterval_B = 65536 - OldASN_ZeroSeq_B + NewASN_ZeroSeq_B
                            else:
                                ZeroSeqASNInterval_B = NewASN_ZeroSeq_B - OldASN_ZeroSeq_B
                            print('NewASN_B:\033[1;32m%s\033[0m OldASN_B:\033[1;33m%s\033[0m ASN间隔:\033[1;36m%s\033[0m'%(NewASN_ZeroSeq_B,OldASN_ZeroSeq_B,ZeroSeqASNInterval_B))
                            
                            if ZeroSeqASNInterval_B == 16:
                                ZeroSeqASNIntervalOKCnt_B += 1
                                # print('B相ASN间隔正常计数:\033[1;32m%s\033[0m'%ZeroSeqASNIntervalOKCnt_B)
                            else:
                                ZeroSeqASNIntervalErCnt_B += 1
                                if math.floor(ZeroSeqASNInterval_B/16.0) < 2 :
                                    ZeroSeqASN_PLC_B += 0
                                if math.floor(ZeroSeqASNInterval_B/16.0) >= 2 and math.floor(ZeroSeqASNInterval_B/16.0) <= 100 :
                                    ZeroSeqASN_PLC_B += math.floor(ZeroSeqASNInterval_B/16.0)-1
                                if math.floor(ZeroSeqASNInterval_B/16.0) > 100 and NewASN_ZeroSeq_B < OldASN_ZeroSeq_B :
                                    ZeroSeqASN_PLC_B += 0
                                    ZeroSeqASNRepeatCnt_B += 1
                                    
                                f.write('%s NewASN_B:%s OldASN_B:%s ASN间隔:%s B相ASN重发计数:%s\n'%(CurrentTime,NewASN_ZeroSeq_B,OldASN_ZeroSeq_B,ZeroSeqASNInterval_B,ZeroSeqASNRepeatCnt_B))
                                print('B相ASN间隔异常计数:\033[1;31m%s\033[0m B相ASN间隔：\033[1;31m%s\033[0m B相零序丢包计数:\033[1;31m%s\033[0m B相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSeqASNIntervalErCnt_B,ZeroSeqASNInterval_B,ZeroSeqASN_PLC_B,ZeroSeqASNRepeatCnt_B))
                            OldASN_ZeroSeq_B = NewASN_ZeroSeq_B
                                
                    if Nick_Name[-1] == 'C' :
                        ZeroSequenceComponentUploadCnt_IC += 1
                        if ZeroSequenceComponentUploadCnt_IC <= 1:
                            OldASN_ZeroSeq_C = int(RcvSerialData[14:16] + RcvSerialData[12:14],16)
                        else:
                            ZeroSeqASNInterval_C = 0
                            NewASN_ZeroSeq_C = int(RcvSerialData[14:16] + RcvSerialData[12:14],16)
                            if NewASN_ZeroSeq_C < OldASN_ZeroSeq_C:
                                ZeroSeqASNInterval_C = 65536 - OldASN_ZeroSeq_C + NewASN_ZeroSeq_C
                            else:
                                ZeroSeqASNInterval_C = NewASN_ZeroSeq_C - OldASN_ZeroSeq_C
                            print('NewASN_C:\033[1;32m%s\033[0m OldASN_C:\033[1;33m%s\033[0m ASN间隔:\033[1;36m%s\033[0m'%(NewASN_ZeroSeq_C,OldASN_ZeroSeq_C,ZeroSeqASNInterval_C))
                            
                            if ZeroSeqASNInterval_C == 16:
                                ZeroSeqASNIntervalOKCnt_C += 1
                                # print('C相ASN间隔正常计数:\033[1;32m%s\033[0m'%ZeroSeqASNIntervalOKCnt_C)
                            else:
                                ZeroSeqASNIntervalErCnt_C += 1
                                if math.floor(ZeroSeqASNInterval_C/16.0) < 2 :
                                    ZeroSeqASN_PLC_C += 0
                                if math.floor(ZeroSeqASNInterval_C/16.0) >= 2 and math.floor(ZeroSeqASNInterval_C/16.0) <= 100:
                                    ZeroSeqASN_PLC_C += math.floor(ZeroSeqASNInterval_C/16.0)-1
                                if math.floor(ZeroSeqASNInterval_C/16.0) > 100 and NewASN_ZeroSeq_C < OldASN_ZeroSeq_C :
                                    ZeroSeqASN_PLC_C += 0
                                    ZeroSeqASNRepeatCnt_C += 1
                                    
                                f.write('%s NewASN_C:%s OldASN_C:%s ASN间隔:%s C相ASN重发计数:%s\n'%(CurrentTime,NewASN_ZeroSeq_C,OldASN_ZeroSeq_C,ZeroSeqASNInterval_C,ZeroSeqASNRepeatCnt_C))
                                print('C相ASN间隔异常计数:\033[1;31m%s\033[0m C相ASN间隔：\033[1;31m%s\033[0m C相零序丢包计数:\033[1;31m%s\033[0m C相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSeqASNIntervalErCnt_C,ZeroSeqASNInterval_C,ZeroSeqASN_PLC_C,ZeroSeqASNRepeatCnt_C)) 
                                
                            OldASN_ZeroSeq_C = NewASN_ZeroSeq_C
                    
                    print('\nA相零序分量上报计数:\033[1;33m%s\033[0m ASN间隔正常计数:\033[1;32m%s\033[0m ASN间隔异常计数:\033[1;31m%s\033[0m 零序丢包计数:\033[1;35m%s\033[0m A相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSequenceComponentUploadCnt_IA,ZeroSeqASNIntervalOKCnt_A,ZeroSeqASNIntervalErCnt_A,ZeroSeqASN_PLC_A,ZeroSeqASNRepeatCnt_A))
                    f.write('\n%s A相零序分量上报计数:%s ASN间隔正常计数:%s ASN间隔异常计数:%s 零序丢包计数:%s A相ASN重发计数:%s\n'%(CurrentTime,ZeroSequenceComponentUploadCnt_IA,ZeroSeqASNIntervalOKCnt_A,ZeroSeqASNIntervalErCnt_A,ZeroSeqASN_PLC_A,ZeroSeqASNRepeatCnt_A))
                    
                    print('B相零序分量上报计数:\033[1;33m%s\033[0m ASN间隔正常计数:\033[1;32m%s\033[0m ASN间隔异常计数:\033[1;31m%s\033[0m 零序丢包计数:\033[1;35m%s\033[0m B相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSequenceComponentUploadCnt_IB,ZeroSeqASNIntervalOKCnt_B,ZeroSeqASNIntervalErCnt_B,ZeroSeqASN_PLC_B,ZeroSeqASNRepeatCnt_B))
                    f.write('%s B相零序分量上报计数:%s ASN间隔正常计数:%s ASN间隔异常计数:%s 零序丢包计数:%s B相ASN重发计数:%s\n'%(CurrentTime,ZeroSequenceComponentUploadCnt_IB,ZeroSeqASNIntervalOKCnt_B,ZeroSeqASNIntervalErCnt_B,ZeroSeqASN_PLC_B,ZeroSeqASNRepeatCnt_B))
                    
                    print('C相零序分量上报计数:\033[1;33m%s\033[0m ASN间隔正常计数:\033[1;32m%s\033[0m ASN间隔异常计数:\033[1;31m%s\033[0m 零序丢包计数:\033[1;35m%s\033[0m C相ASN重发计数:\033[1;31m%s\033[0m'%(ZeroSequenceComponentUploadCnt_IC,ZeroSeqASNIntervalOKCnt_C,ZeroSeqASNIntervalErCnt_C,ZeroSeqASN_PLC_C,ZeroSeqASNRepeatCnt_C))
                    f.write('%s C相零序分量上报计数:%s ASN间隔正常计数:%s ASN间隔异常计数:%s 零序丢包计数:%s C相ASN重发计数:%s\n'%(CurrentTime,ZeroSequenceComponentUploadCnt_IC,ZeroSeqASNIntervalOKCnt_C,ZeroSeqASNIntervalErCnt_C,ZeroSeqASN_PLC_C,ZeroSeqASNRepeatCnt_C))
                    
                    print('\nRF CRC Error计数:\033[1;31m%s\033[0m'%RF_CRC_Error_Count)
                    f.write('\n%s RF CRC Error计数:%s\n'%(CurrentTime,RF_CRC_Error_Count))
                   
                elif CMD == 'B6':
                    print('\033[1;36m%s取256点电流录波响应帧\033[0m'%Nick_Name[-1]) 
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取256点电流录波响应帧:\n'%(CurrentTime,Nick_Name[-1]))

                    TRIGGERED_ASN_L = RFData[14:16]+RFData[12:14]
                    # print('触发录波的 ASN.l:',TRIGGERED_ASN_L)
                    N = RFData[16:18]
                    # print('录波文件的当前周波编号:',N)
                    OFFSET = RFData[18:20]
                    # print('录波文件的当前偏移地址:',OFFSET)
                    WAVE_FILE = RFData[20:-4]
                    # print('录波文件正文:',WAVE_FILE)
                    
                    print('触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s'%(TRIGGERED_ASN_L,N,OFFSET))
                    # print('录波文件正文:',WAVE_FILE)
                    f.write('%s 触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s\n'%(CurrentTime,TRIGGERED_ASN_L,N,OFFSET))
                    # f.write('%s 录波文件正文:%s\n'%(CurrentTime,WAVE_FILE))
                    
                    if (int(OFFSET,16) & 0x10) == 0x10 :
                        print('%s相第\033[1;33m%s\033[0m周波数据传输完毕'%(Nick_Name[-1],int(N,16)+1))
                        f.write('%s %s相第%s周波：数据传输完毕\n'%(CurrentTime,Nick_Name[-1],int(N,16)+1))
                    
                    RecordWaveResponseCnt_I += 1
                    if Nick_Name[-1] == 'A' :
                        RecordWaveResponseCnt_IA += 1
                        if RecordWaveBroadcastCnt_IA != 0:
                            RecordWave_PER_IA = (RecordWaveBroadcastCnt_IA-RecordWaveResponseCnt_IA)/RecordWaveBroadcastCnt_IA
                    if RecordWaveBroadcastCnt_IA == 0 or RecordWaveResponseCnt_IA == 0 :
                        RecordWave_PER_IA = 1.0
                    if Nick_Name[-1] == 'B' :
                        RecordWaveResponseCnt_IB += 1   
                        if RecordWaveBroadcastCnt_IB != 0:
                            RecordWave_PER_IB = (RecordWaveBroadcastCnt_IB-RecordWaveResponseCnt_IB)/RecordWaveBroadcastCnt_IB 
                    if RecordWaveBroadcastCnt_IB == 0 or RecordWaveResponseCnt_IB == 0 :
                        RecordWave_PER_IB = 1.0
                    if Nick_Name[-1] == 'C' :
                        RecordWaveResponseCnt_IC += 1  
                        if RecordWaveBroadcastCnt_IC != 0:
                            RecordWave_PER_IC = (RecordWaveBroadcastCnt_IC-RecordWaveResponseCnt_IC)/RecordWaveBroadcastCnt_IC
                    if RecordWaveBroadcastCnt_IC == 0 or RecordWaveResponseCnt_IC == 0 :
                        RecordWave_PER_IC = 1.0
                     
                    print('电流录波响应总计数：\033[1;36m%s\033[0m A相电流录波响应计数：\033[1;33m%s\033[0m B相电流录波响应计数：\033[1;32m%s\033[0m C相电流录波响应计数：\033[1;31m%s\033[0m'%(RecordWaveResponseCnt_I,RecordWaveResponseCnt_IA,RecordWaveResponseCnt_IB,RecordWaveResponseCnt_IC))
                    f.write('%s 电流录波响应总计数：%s A相电流录波响应计数：%s B相电流录波响应计数：%s C相电流录波响应计数：%s\n'%(CurrentTime,RecordWaveResponseCnt_I,RecordWaveResponseCnt_IA,RecordWaveResponseCnt_IB,RecordWaveResponseCnt_IC))
                    
                    # print('A相电流录波PER:\033[1;33m{:.2%}\033[0m B相电流录波PER:\033[1;32m{:.2%}\033[0m C相电流录波PER:\033[1;31m{:.2%}\033[0m'.format(RecordWave_PER_IA,RecordWave_PER_IB,RecordWave_PER_IC))
                    # f.write('{0} A相电流录波PER:{1:.2%} B相电流录波PER:{2:.2%} C相电流录波PER:{3:.2%}\n'.format(CurrentTime,RecordWave_PER_IA,RecordWave_PER_IB,RecordWave_PER_IC))
                    
                    CurrentTime = ''   
                    TRIGGERED_ASN_L = ''
                    N = ''
                    OFFSET = ''
                    WAVE_FILE = ''
                    
                elif CMD == 'B9':
                    print('\033[1;36m%s取256点电场录波响应帧\033[0m'%Nick_Name[-1])
                    f.write('\n%s %s'%(CurrentTime,RcvSerialData[0:-2]+'\n'))
                    f.write('%s %s取256点电场录波响应帧:\n'%(CurrentTime,Nick_Name[-1]))

                    TRIGGERED_ASN_L = RFData[14:16]+RFData[12:14]
                    # print('触发录波的ASN.l:',TRIGGERED_ASN_L)
                    N = RFData[16:18]
                    # print('录波文件的当前周波编号:',N)
                    OFFSET = RFData[18:20]
                    # print('录波文件的当前偏移地址:',OFFSET)
                    WAVE_FILE = RFData[20:-4]
                    # print('录波文件正文:',WAVE_FILE)
                    
                    print('触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s'%(TRIGGERED_ASN_L,N,OFFSET))
                    # print('录波文件正文:%s'%(WAVE_FILE))
                    f.write('%s 触发录波的ASN.l:%s 当前周波号:%s 当前偏移地址:%s\n'%(CurrentTime,TRIGGERED_ASN_L,N,OFFSET))
                    # f.write('%s 录波文件正文:%s\n'%(CurrentTime,WAVE_FILE))
                    
                    if (int(OFFSET,16) & 0x10) == 0x10 :
                        print('%s相第\033[1;33m%s\033[0m周波：数据传输完毕'%(Nick_Name[-1],int(N,16)+1))
                        f.write('%s %s相第%s周波数据传输完毕\n'%(CurrentTime,Nick_Name[-1],int(N,16)+1))
                    
                    RecordWaveResponseCnt_V += 1
                    if Nick_Name[-1] == 'A' :
                        RecordWaveResponseCnt_VA += 1
                        if RecordWaveBroadcastCnt_VA != 0:
                            RecordWave_PER_VA = (RecordWaveBroadcastCnt_VA-RecordWaveResponseCnt_VA)/RecordWaveBroadcastCnt_VA
                    if RecordWaveBroadcastCnt_VA == 0 or RecordWaveResponseCnt_VA == 0 :
                        RecordWave_PER_VA = 1.0
                    if Nick_Name[-1] == 'B' :
                        RecordWaveResponseCnt_VB += 1 
                        if RecordWaveBroadcastCnt_VB != 0:
                            RecordWave_PER_VB = (RecordWaveBroadcastCnt_VB-RecordWaveResponseCnt_VB)/RecordWaveBroadcastCnt_VB
                    if RecordWaveBroadcastCnt_VB == 0 or RecordWaveResponseCnt_VB == 0 :
                        RecordWave_PER_VB = 1.0
                    if Nick_Name[-1] == 'C' :
                        RecordWaveResponseCnt_VC += 1 
                        if RecordWaveBroadcastCnt_VC != 0:
                            RecordWave_PER_VC = (RecordWaveBroadcastCnt_VC-RecordWaveResponseCnt_VC)/RecordWaveBroadcastCnt_VC
                    if RecordWaveBroadcastCnt_VC == 0 or RecordWaveResponseCnt_VC == 0 :
                        RecordWave_PER_VC = 1.0
                    
                    print('电场录波响应总计数：\033[1;36m%s\033[0m A相电场录波响应计数：\033[1;33m%s\033[0m B相电场录波响应计数：\033[1;32m%s\033[0m C相电场录波响应计数：\033[1;31m%s\033[0m'%(RecordWaveResponseCnt_V,RecordWaveResponseCnt_VA,RecordWaveResponseCnt_VB,RecordWaveResponseCnt_VC))
                    f.write('%s 电场录波响应总计数：%s A相电场录波响应计数：%s B相电场录波响应计数：%s C相电场录波响应计数：%s\n'%(CurrentTime,RecordWaveResponseCnt_V,RecordWaveResponseCnt_VA,RecordWaveResponseCnt_VB,RecordWaveResponseCnt_VC))
                    
                    # print('A相电场录波PER:\033[1;33m{:.2%}\033[0m B相电场录波PER:\033[1;32m{:.2%}\033[0m C相电场录波PER:\033[1;31m{:.2%}\033[0m'.format(RecordWave_PER_VA,RecordWave_PER_VB,RecordWave_PER_VC))
                    # f.write('{0} A相电场录波PER:{1:.2%} B相电场录波PER:{2:.2%} C相电场录波PER:{3:.2%}\n'.format(CurrentTime,RecordWave_PER_VA,RecordWave_PER_VB,RecordWave_PER_VC))

                    TRIGGERED_ASN_L = ''
                    N = ''
                    OFFSET = ''
                    WAVE_FILE = ''
                    
                # else:
                    # print('\033[1;31mUndefined CMD Field\033[0m')
                    # f.write('%s 未定义的数据:\n'%CurrentTime)
                    
                CurrentTime = ''
                f.close()
                
            DataLen = ''   
            RcvSerialData = ''
            RFData = ''


def str_to_hexStr(string):
    str_bin = string.encode('utf-8')
    return binascii.hexlify(str_bin).decode('utf-8')  

   
def Get_OC_RSSI(RcvSerialData,f,CurrentTime):
    OC_RSSI = 0
    # RcvSerialData = RcvSerialData[0:-2]
    if re.search(r"RF:crc 0 rssi",RcvSerialData) != None :
        OC_RSSI = int(RcvSerialData.split(' ')[-1][:-2],10) - 256
        if OC_RSSI != -256:
            print('\nOC_RSSI:\033[1;33m%s\033[0mdBm'%OC_RSSI)
            f.write('%s OC_RSSI:%sdBm\n'%(CurrentTime,OC_RSSI))


def GPS_Fix_State(RcvSerialData,f,CurrentTime):
    if re.search(r"GPRMC",RcvSerialData) != None:
        if RcvSerialData.split(',')[2] == 'A':
            # print('\nGPS定位状态:%s'%re.search(r"GPRMC(.*)A", RcvSerialData))
            print('\nGPS定位\033[1;32m成功\033[0m')
            UTCTime = RcvSerialData.split(',')[1] #hhmmss.sss格式
            LocalTimeHH = str(int(UTCTime[0:2])+8)
            LocalTime = LocalTimeHH + ':'+ UTCTime[2:4] + ':'+ UTCTime[4:6]
            
            latitude = RcvSerialData.split(',')[3] #ddmm.mmmm，度分格式
            latitudeType = RcvSerialData.split(',')[4] #纬度N（北纬）或S（南纬）
            longitude = RcvSerialData.split(',')[5] #dddmm.mmmm，度分格式
            longitudeType = RcvSerialData.split(',')[6] #经度E（东经）或W（西经）
            if re.search(r"$GPTXT",RcvSerialData.split(',')[7]) != None:
                print('\n\033[1;31mGPS Data Invalid\033[0m')
                f.write('\n%s GPS帧格式错误: \n'%(CurrentTime,RcvSerialData))
                return False

            Speed = float(RcvSerialData.split(',')[7])*1.852 #节，Knots（1节=1.852km/h）
            # AzimuthAngle = RcvSerialData.split(',')[8] #方位角，度
            Date = RcvSerialData.split(',')[9] #日期 DDMMYY格式
            Date = Date[4:6]+Date[2:4]+Date[0:2]
            MagneticDeclination = RcvSerialData.split(',')[10] #磁偏角
            # OrientationOfMagneticDeclination = RcvSerialData.split(',')[11] #磁偏角方向
            GPSMode = RcvSerialData.split(',')[12][0] #模式指示，A=自动，D=差分，E=估测，N=数据无效（NMEA 0183 V3.0协议内容）
            if GPSMode == 'A':
                GPSMode = '自动'
            elif GPSMode == 'D':
                GPSMode = '差分'
            elif GPSMode == 'E':
                GPSMode = '估测'
            elif GPSMode == 'N':
                GPSMode = '数据无效'
            else :
                GPSMode = '未定义的模式'

            print('UTC时间:%s 本地时间:%s 纬度:%s(%s) 经度:%s(%s) 速度:%.2f(km/h) 日期:20%s 模式:%s'%(UTCTime,LocalTime,latitude,latitudeType,longitude,longitudeType,Speed,Date,GPSMode))
            f.write('\n%s GPS定位成功\n'%CurrentTime)
            f.write('%s UTC时间:%s 纬度:%s(%s) 经度:%s(%s) 速度:%.2f(km/h) 日期:20%s 模式:%s\n'%(CurrentTime,UTCTime,latitude,latitudeType,longitude,longitudeType,Speed,Date,GPSMode))
            
            UTCTime = ''
            LocalTimeHH = ''
            LocalTime = ''
            latitude = ''
            latitudeType = ''
            longitude = ''
            longitudeType = ''
            Speed = ''
            Date = ''
            GPSMode = ''
        elif RcvSerialData.split(',')[2] == 'V' :
        # elif re.search(r",V,",RcvSerialData) != None :
            print('\nGPS\033[1;31m未定位\033[0m')
            f.write('\n%s GPS未定位\n'%CurrentTime)
        else:
            print('\n\033[1;31m GPS Data Invalid\033[0m')
 
 
def GPS_Lock_State(RcvSerialData,f,CurrentTime):
    if re.search(r"lock:",RcvSerialData) != None :
        if re.search(r"lock:1",RcvSerialData) != None :
            print('GPS锁定\033[1;32m成功\033[0m') 
            f.write('%s GPS已锁定\n'%CurrentTime)
        elif re.search(r"lock:0",RcvSerialData) != None :
            print('GPS\033[1;31m未锁定\033[0m')
            f.write('%s GPS未锁定\n'%CurrentTime)
        else:
            print('\n\033[1;31mData Invalid\033[0m')
 
 
def DM_Communication_State(RcvSerialData,f,CurrentTime):  
    global OC_Send_Data_to_DM_Flg
    global OC_Rcv_Data_to_DM_Flg
    global n
    global ReportDMOldTicks
    
    if re.search(r"DIAL  :Dail OK",RcvSerialData) != None :
        print('拨号\033[1;32m成功\033[0m')
    if re.search(r"TCPIP :local IP address",RcvSerialData) != None or re.search(r"DIAL  :Host IP=",RcvSerialData) != None :
        print('连接基站\033[1;32m成功\033[0m')

    if re.search(r"Send to DM:",RcvSerialData) != None :
        OC_Send_Data_to_DM_Flg = True
        print('\nSend Data to DM: OK')
        f.write('\n%s OC发送数据至DM正常\n'%CurrentTime)
    if re.search(r"Rcv DM data, len:",RcvSerialData) != None :
        OC_Rcv_Data_to_DM_Flg = True
        print('Rcv DM  Data: OK')
        f.write('%s OC接收DM数据正常\n'%CurrentTime)
    if re.search(r"DM    :os",RcvSerialData) != None :
        IPAdrStartPostion = RcvSerialData.index('to:')
        # print('IPAdrStartPostion:%s'%IPAdrStartPostion) 
        IPAdrNetPort = RcvSerialData[IPAdrStartPostion+3:-2]
        print('IPAdrNetPort:%s'%IPAdrNetPort)
        f.write('%s DM IP地址及端口:%s\n'%(CurrentTime,IPAdrNetPort))
        IPAdrNetPort = ''
        IPAdrStartPostion = ''
    if re.search(r"DM    :csq:",RcvSerialData) != None :
            length = len(RcvSerialData)-4
            CsqStartPostion = RcvSerialData.index('csq:')
            CsqNumber = int(RcvSerialData[CsqStartPostion+4:-2])
            RSSI = -113 + CsqNumber*2
            if CsqNumber >= 10 and CsqNumber <= 31 :
                print('\n4G模块信号值正常 csq:\033[1;32m%s\033[0m 接收信号强度:\033[1;32m%s\033[0m(dBm)'%(CsqNumber,RSSI))
                f.write('\n%s 4G模块信号值正常 csq:%s 接收信号强度:%s(dBm)\n'%(CurrentTime,CsqNumber,RSSI))
            elif CsqNumber == 99 :
                print('\n4G模块\033[1;31m无信号\033[0m csq:\033[1;31m%s\033[0m'%(CsqNumber,CsqNumber))
                f.write('\n%s 4G模块无信号 csq:%s\n'%(CurrentTime,CsqNumber))
            else :
                print('\n4G模块信号值\033[1;31m异常\033[0m csq:\033[1;31m%s\033[0m 接收信号强度:\033[1;31m%s\033[0m(dBm)'%(CsqNumber,RSSI))
                f.write('\n%s 4G模块信号值异常 csq:%s 接收信号强度:%s(dBm)\n'%(CurrentTime,CsqNumber,RSSI))
            
            CsqStartPostion = ''
            CsqNumber = ''   
            length = 0
            RSSI = ''

    if OC_Send_Data_to_DM_Flg == True and OC_Rcv_Data_to_DM_Flg == True :
        n += 1
        print('DM Test Count:%s'%n)
        if n == 1 :
            ReportDMOldTicks = time.time()
            # print('ReportDMOldTicks:%s'%ReportDMOldTicks)
        if n >= 2 :
            ReportDMNewTicks = time.time()
            # print('ReportDMNewTicks:%s'%ReportDMNewTicks)
            ReportDMInterval = ReportDMNewTicks - ReportDMOldTicks
            ReportDMOldTicks = ReportDMNewTicks
            print('OC与DM通信间隔(s):%.2f'%ReportDMInterval)
            f.write('%s OC与DM通信间隔(s):%.2f\n'%(CurrentTime,ReportDMInterval))
            if ReportDMInterval < 46.5 :
                print('\033[1;32mOC与DM通信间隔正常\033[0m')
                f.write('%s OC与DM通信间隔正常\n'%CurrentTime)
            else : 
                print('\033[1;31mOC与DM通信间隔异常\033[0m')
                f.write('%s OC与DM通信间隔异常\n'%CurrentTime)
        OC_Send_Data_to_DM_Flg = False
        OC_Rcv_Data_to_DM_Flg = False


def IEC10X_Communication_State(RcvSerialData,f,CurrentTime):  
    global IEC10X_Reade_Flg
    global IEC10X_Write_Flg
    global k
    global ReportIEC10XOldTicks
    
    
    if re.search(r"IEC10X:Connecting",RcvSerialData) != None :
        IEC10XIPPortPostion = RcvSerialData.index('Connecting ')
        IEC10XIPPort = RcvSerialData[IEC10XIPPortPostion+11:-2]
        print('101主站IP/端口:%s'%IEC10XIPPort)
        
        IEC10XIPPortPostion = ''
        IEC10XIPPort = ''
        
    if re.search(r"IEC10X:connect ok",RcvSerialData) != None :
        print('连接101主站\033[1;32m成功\033[0m')
    
    if re.search(r"IEC10X:101 net read",RcvSerialData) != None :
        IEC10X_Reade_Flg = True
        print('\nIEC10x net read:\033[1;32mOK\033[0m')
        f.write('\n%s IEC10x网络数据读取正常\n'%CurrentTime)
        
    if re.search(r"IEC10X:101 net write",RcvSerialData) != None :
        IEC10X_Write_Flg = True
        print('\nIEC10x net write:\033[1;32m OK\033[0m')
        f.write('\n%s IEC10x网络数据写入正常\n'%CurrentTime)

    if IEC10X_Reade_Flg == True and IEC10X_Write_Flg == True :
        k += 1
        print('IEC10x Test Count:%s'%k)
        if k == 1 :
            ReportIEC10XOldTicks = time.time()
            # print('ReportIEC10xOldTicks:%s'%ReportIEC10XOldTicks)
        if k >= 2 :
            ReportIEC10XNewTicks = time.time()
            # print('ReportIEC10XNewTicks:%s'%ReportIEC10XNewTicks)
            ReportIEC10XInterval = ReportIEC10XNewTicks - ReportIEC10XOldTicks
            ReportIEC10XOldTicks = ReportIEC10XNewTicks
            print('IEC10x通信间隔(s):%.2f'%ReportIEC10XInterval)
            f.write('%s IEC10x通信间隔(s):%.2f\n'%(CurrentTime,ReportIEC10XInterval))
            if ReportIEC10XInterval < 180.5 :
                print('\033[1;32mIEC10x通信间隔正常\033[0m')
                f.write('%s IEC10x通信间隔正常\n'%CurrentTime)
            else : 
                print('\033[1;31mIEC10x通信间隔异常\033[0m')
                f.write('%s IEC10x通信间隔异常\n'%CurrentTime)
        IEC10X_Reade_Flg = False
        IEC10X_Write_Flg = False

CheckSumPassCount = 0
CheckSumFailCount = 0
def word_checksum(strs):
    global CheckSumPassCount
    global CheckSumFailCount
    CheckSum = 0x1234
    CheckDataLen = 0
    CheckSumState = ''
    
    CheckData = strs[4:-4]
    # print(CheckData)
    CheckDataLen = len(CheckData)
    #print('CheckDataLen(Bytes) = %s'%(CheckDataLen/2))
    for i in range(0,CheckDataLen,4):
        CheckWord = CheckData[i+2:i+4]+CheckData[i:i+2]
        # print('CheckWord:%s'%CheckWord)
        CheckSum += int(CheckWord,16)
        # print('i=%s CheckData[%s:%s]=%s'%(i,i,i+4,CheckData[i:i+4]))
        CheckSum &= 0xFFFF
    CheckSumSrcData = strs[-2:]+strs[-4:-2]
    # print('CheckSumSrcData:0x%s CheckSum:0x%s'%(CheckSumSrcData,hex(CheckSum).upper()[2:]))
    if CheckSum == int(strs[-2:]+strs[-4:-2],16) :
        CheckSumPassCount += 1
        CheckSumState = 'Pass'
        CheckSum = hex(CheckSum).upper()[2:]
        print('CheckSum:\033[1;33m0x%s\033[0m CheckResult:\033[1;32mPass\033[0m CheckPassCount:\033[1;33m%s\033[0m CheckFailCount:\033[1;31m%s\033[0m'%(CheckSum,CheckSumPassCount,CheckSumFailCount))
    else :
        CheckSumFailCount += 1
        CheckSumState = 'Fail'
        CheckSum = hex(CheckSum).upper()[2:]
        print('CheckSum:\033[1;33m0x%s\033[0m \033[1;31mFail\033[0m CheckPassCount:\033[1;33m%s\033[0m CheckFailCount:\033[1;31m%s\033[0m'%(CheckSum,CheckSumPassCount,CheckSumFailCount))
    
    return CheckSum,CheckSumState


FwUpdate_PER_A = 0.0
FwUpdate_PER_B = 0.0
FwUpdate_PER_C = 0.0
FwUpdateTimeoutResendCnt_A = 0
FwUpdateTimeoutResendCnt_B = 0
FwUpdateTimeoutResendCnt_C = 0
def AcquUnitFwUpdate_PER(RcvSerialData,f,CurrentTime): 
    global FwUpdateResponseCnt
    global FwUpdateResponseCnt_A
    global FwUpdateResponseCnt_B
    global FwUpdateResponseCnt_C
    
    global FwUpdateResponseOKCnt_A
    global FwUpdateResponseOKCnt_B
    global FwUpdateResponseOKCnt_C
    
    global FwUpdateResponseErCnt_A
    global FwUpdateResponseErCnt_B
    global FwUpdateResponseErCnt_C
    
    global FwWriteFlashCnt
    global FwWriteFlashCnt_A
    global FwWriteFlashCnt_B
    global FwWriteFlashCnt_C   

    global FwUpdate_PER_A
    global FwUpdate_PER_B
    global FwUpdate_PER_C

    global FwUpdateTxCnt
    global FwUpdateTxCnt_A
    global FwUpdateTxCnt_B
    global FwUpdateTxCnt_C
    
    global FwUpdateTimeoutResendCnt_A
    global FwUpdateTimeoutResendCnt_B
    global FwUpdateTimeoutResendCnt_C
    
    if re.search(r"'A' fw update Begin",RcvSerialData) != None :
        print('A相开始升级固件')
        f.write('%s A相开始升级固件\n'%CurrentTime)
    if re.search(r"'B' fw update Begin",RcvSerialData) != None :
        print('B相开始升级固件')
        f.write('%s B相开始升级固件\n'%CurrentTime)
    if re.search(r"'C' fw update Begin",RcvSerialData) != None :
        print('C相开始升级固件')
        f.write('%s C相开始升级固件\n'%CurrentTime)
    
    if re.search(r"update failure:0xfffffff5",RcvSerialData) != None : 
        FwWriteFlashCnt += 1
        print('\n三相累计写Flash计数:%s'%FwWriteFlashCnt)
        f.write('\n%s 三相累计写Flash计数:%s'%(CurrentTime,FwWriteFlashCnt))
        
    if re.search(r"'A' timeout,resend",RcvSerialData) != None :
        FwUpdateTimeoutResendCnt_A += 1
        print('\nA相升级响应超时重发计数:\033[1;33m%s\033[0m'%FwUpdateTimeoutResendCnt_A) 
    if re.search(r"'B' timeout,resend",RcvSerialData) != None :
        FwUpdateTimeoutResendCnt_B += 1
        print('\nB相升级响应超时重发计数:\033[1;32m%s\033[0m'%FwUpdateTimeoutResendCnt_B) 
    if re.search(r"'C' timeout,resend",RcvSerialData) != None :
        FwUpdateTimeoutResendCnt_C += 1
        print('\nC相升级响应超时重发计数:\033[1;31m%s\033[0m'%FwUpdateTimeoutResendCnt_C)
    
    if re.search(r"'A' Update Finish",RcvSerialData) != None :
        print('\nA相完成固件升级')
        f.write('\n%s A相完成固件升级:\n'%CurrentTime)
        print('A相发包计数:\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_A,FwUpdateResponseOKCnt_A + FwUpdateResponseErCnt_A,FwUpdateResponseOKCnt_A,FwUpdateResponseErCnt_A,FwWriteFlashCnt_A,FwUpdateTimeoutResendCnt_A))
        f.write('%s A相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_A,FwUpdateResponseOKCnt_A + FwUpdateResponseErCnt_A,FwUpdateResponseOKCnt_A,FwUpdateResponseErCnt_A,FwWriteFlashCnt_A,FwUpdateTimeoutResendCnt_A))
        if FwUpdateTxCnt_A > 0:
            FwUpdate_PER_A = (FwUpdateTxCnt_A - (FwUpdateResponseCnt_A - FwWriteFlashCnt_A) + FwUpdateTimeoutResendCnt_A + FwUpdateResponseErCnt_A) / FwUpdateTxCnt_A
            print('A相升级PER:\033[1;33m{:.2%}\033[0m\n'.format(FwUpdate_PER_A)) 
            f.write('{0} A相升级PER:{1:.2%}\n'.format(CurrentTime,FwUpdate_PER_A))
    if re.search(r"'B' Update Finish",RcvSerialData) != None :
        print('\nB相完成固件升级')
        f.write('\n%s B相完成固件升级:\n'%CurrentTime)
        print('B相发包计数\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_B,FwUpdateResponseOKCnt_B + FwUpdateResponseErCnt_B,FwUpdateResponseOKCnt_B,FwUpdateResponseErCnt_B,FwWriteFlashCnt_B,FwUpdateTimeoutResendCnt_B))
        f.write('%s B相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_B,FwUpdateResponseOKCnt_B + FwUpdateResponseErCnt_B,FwUpdateResponseOKCnt_B,FwUpdateResponseErCnt_B,FwWriteFlashCnt_B,FwUpdateTimeoutResendCnt_B))
        if FwUpdateTxCnt_B > 0:
            FwUpdate_PER_B = (FwUpdateTxCnt_B - (FwUpdateResponseCnt_B - FwWriteFlashCnt_B) + FwUpdateTimeoutResendCnt_B + FwUpdateResponseErCnt_B) / FwUpdateTxCnt_B 
            print('B相升级PER:\033[1;32m{:.2%}\033[0m\n'.format(FwUpdate_PER_B))
            f.write('{0} B相升级PER:{1:.2%}\n'.format(CurrentTime,FwUpdate_PER_B))
    if re.search(r"'C' Update Finish",RcvSerialData) != None :
        print('\nC完成固件升级') 
        f.write('\n%s C相完成固件升级:\n'%CurrentTime)
        print('C相发包计数:\033[1;32m%s\033[0m 响应计数:\033[1;33m%s\033[0m 正确响应计数:\033[1;32m%s\033[0m 错误响应计数:\033[1;31m%s\033[0m 写Flash计数:\033[1;35m%s\033[0m 响应超时重发计数:\033[1;33m%s\033[0m'%(FwUpdateTxCnt_C,FwUpdateResponseOKCnt_C + FwUpdateResponseErCnt_C,FwUpdateResponseOKCnt_C,FwUpdateResponseErCnt_C,FwWriteFlashCnt_C,FwUpdateTimeoutResendCnt_C))
        f.write('%s C相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_C,FwUpdateResponseOKCnt_C + FwUpdateResponseErCnt_C,FwUpdateResponseOKCnt_C,FwUpdateResponseErCnt_C,FwWriteFlashCnt_C,FwUpdateTimeoutResendCnt_C))
        if FwUpdateTxCnt_C > 0:
            FwUpdate_PER_C = (FwUpdateTxCnt_C - (FwUpdateResponseCnt_C - FwWriteFlashCnt_C) + FwUpdateTimeoutResendCnt_C + FwUpdateResponseErCnt_C) / FwUpdateTxCnt_C
            print('C相升级PER:\033[1;31m{:.2%}\033[0m\n'.format(FwUpdate_PER_C))
            f.write('{0} C相升级PER:{1:.2%}\n'.format(CurrentTime,FwUpdate_PER_C))  
        
    if re.search(r"Update Finish, goto CONFIG",RcvSerialData) != None :
        f.write('\n%s A相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_A,FwUpdateResponseOKCnt_A + FwUpdateResponseErCnt_A,FwUpdateResponseOKCnt_A,FwUpdateResponseErCnt_A,FwWriteFlashCnt_A,FwUpdateTimeoutResendCnt_A))
        f.write('%s B相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_B,FwUpdateResponseOKCnt_B + FwUpdateResponseErCnt_B,FwUpdateResponseOKCnt_B,FwUpdateResponseErCnt_B,FwWriteFlashCnt_B,FwUpdateTimeoutResendCnt_B))
        f.write('%s C相升级包发送计数:%s 响应计数:%s 正确响应计数:%s 错误响应计数:%s 写Flash计数:%s 响应超时重发计数:%s\n'%(CurrentTime,FwUpdateTxCnt_C,FwUpdateResponseOKCnt_C + FwUpdateResponseErCnt_C,FwUpdateResponseOKCnt_C,FwUpdateResponseErCnt_C,FwWriteFlashCnt_C,FwUpdateTimeoutResendCnt_C))
        
        print('A相升级PER:\033[1;33m{0:.2%}\033[0m B相升级PER:\033[1;32m{1:.2%}\033[0m C相升级PER:\033[1;31m{2:.2%}\033[0m\n'.format(FwUpdate_PER_A,FwUpdate_PER_B,FwUpdate_PER_C))
        f.write('{0} A相升级PER:{1:.2%} B相升级PER:{2:.2%} C相升级PER:{3:.2%}\n'.format(CurrentTime,FwUpdate_PER_A,FwUpdate_PER_B,FwUpdate_PER_C))  

UploadWaveTimeoutCnt_A = 0
UploadWaveTimeoutCnt_B = 0
UploadWaveTimeoutCnt_C = 0
UploadWaveTimeoutCnt = 0

GiveUpWave_A = 0
GiveUpWave_B = 0
GiveUpWave_C = 0

RecordWaveOKCnt_IA = 0
RecordWaveOKCnt_IB = 0
RecordWaveOKCnt_IC = 0
RecordWaveOKCnt_VA = 0
RecordWaveOKCnt_VB = 0
RecordWaveOKCnt_VC = 0
RecordWaveOKCnt_ABC = 0

def UploadWave_PER(RcvSerialData,f,CurrentTime): 
    RecordWaveBroadcastCnt_A = 0
    RecordWaveBroadcastCnt_B = 0
    RecordWaveBroadcastCnt_C = 0
    
    RecordWaveResponseCnt_A = 0
    RecordWaveResponseCnt_B = 0
    RecordWaveResponseCnt_C = 0
    
    RecordWave_PER_A = 0.0
    RecordWave_PER_B = 0.0
    RecordWave_PER_C = 0.0

    global UploadWaveTimeoutCnt_A
    global UploadWaveTimeoutCnt_B
    global UploadWaveTimeoutCnt_C
    global UploadWaveTimeoutCnt
    
    global RecordWaveBroadcastCnt_I
    global RecordWaveBroadcastCnt_V
    global RecordWaveResponseCnt_I
    global RecordWaveResponseCnt_V
    
    global GiveUpWave_A
    global GiveUpWave_B
    global GiveUpWave_C
    
    global RecordWaveOKCnt_IA
    global RecordWaveOKCnt_IB
    global RecordWaveOKCnt_IC
    global RecordWaveOKCnt_VA
    global RecordWaveOKCnt_VB
    global RecordWaveOKCnt_VC 
    global RecordWaveOKCnt_ABC
    
    if re.search(r"wave",RcvSerialData) != None :
        f.write('\n')
        if re.search(r"'A' wave begin",RcvSerialData) != None :
            print('A相开始上传录波数据')
            f.write('%s A相开始上传录波数据\n'%CurrentTime)
        if re.search(r"'B' wave begin",RcvSerialData) != None :
            print('B相开始上传录波数据')
            f.write('%s B相开始上传录波数据\n'%CurrentTime)
        if re.search(r"'C' wave begin",RcvSerialData) != None :
            print('C相开始上传录波数据')
            f.write('%s C相开始上传录波数据\n'%CurrentTime)
        
        if re.search(r"'A' wave timeout",RcvSerialData) != None :
            UploadWaveTimeoutCnt_A += 1
        if re.search(r"'B' wave timeout",RcvSerialData) != None :
            UploadWaveTimeoutCnt_B += 1
        if re.search(r"'C' wave timeout",RcvSerialData) != None :
            UploadWaveTimeoutCnt_C += 1
        if re.search(r"wave timeout",RcvSerialData) != None :
            UploadWaveTimeoutCnt += 1
            print('录波数据上传超时总计数:\033[1;33m{0}\033[0m 录波上传PER:\033[1;31m{1:.2%}\033[0m'.format(UploadWaveTimeoutCnt,UploadWaveTimeoutCnt/RecordWaveBroadcastCnt_I))
            f.write('{0} 录波数据上传超时总计数:{1} 录波上传PER:{2:.2%}\n'.format(CurrentTime,UploadWaveTimeoutCnt,UploadWaveTimeoutCnt/(RecordWaveBroadcastCnt_I+RecordWaveBroadcastCnt_V)))

        if re.search(r"'A' give up wave",RcvSerialData) != None :
            GiveUpWave_A += 1
            print('A相放弃上传录波数据: %s'%GiveUpWave_A)
            f.write('%s A相放弃上传录波数据: %s\n'%(CurrentTime,GiveUpWave_A))
        if re.search(r"'B' give up wave",RcvSerialData) != None :
            GiveUpWave_B += 1
            print('B相放弃上传录波数据: %s'%GiveUpWave_B)
            f.write('%s B相放弃上传录波数据: %s\n'%(CurrentTime,GiveUpWave_B))
        if re.search(r"'C' give up wave",RcvSerialData) != None :
            GiveUpWave_C += 1
            print('C相放弃上传录波数据 :%s'%GiveUpWave_C)
            f.write('%s C相放弃上传录波数据: %s\n'%(CurrentTime,GiveUpWave_C))
            
        if RecordWaveBroadcastCnt_I + RecordWaveBroadcastCnt_V >= 1 :
            if RecordWaveBroadcastCnt_IA + RecordWaveBroadcastCnt_VA >= 1 :
                RecordWave_PER_A = UploadWaveTimeoutCnt_A / (RecordWaveBroadcastCnt_IA + RecordWaveBroadcastCnt_VA)
            if RecordWaveBroadcastCnt_IB + RecordWaveBroadcastCnt_VB >= 1 :
                RecordWave_PER_B = UploadWaveTimeoutCnt_B / (RecordWaveBroadcastCnt_IB + RecordWaveBroadcastCnt_VB)
            if RecordWaveBroadcastCnt_IC + RecordWaveBroadcastCnt_VC >= 1 :
                RecordWave_PER_C = UploadWaveTimeoutCnt_C / (RecordWaveBroadcastCnt_IC + RecordWaveBroadcastCnt_VC)
            
            RecordWaveBroadcastCnt_A = RecordWaveBroadcastCnt_IA + RecordWaveBroadcastCnt_VA
            RecordWaveBroadcastCnt_B = RecordWaveBroadcastCnt_IB + RecordWaveBroadcastCnt_VB
            RecordWaveBroadcastCnt_C = RecordWaveBroadcastCnt_IC + RecordWaveBroadcastCnt_VC
            
            RecordWaveResponseCnt_A = RecordWaveResponseCnt_IA + RecordWaveResponseCnt_VA
            RecordWaveResponseCnt_B = RecordWaveResponseCnt_IB + RecordWaveResponseCnt_VB
            RecordWaveResponseCnt_C = RecordWaveResponseCnt_IC + RecordWaveResponseCnt_VC
            
            if RecordWaveBroadcastCnt_A == 0 or RecordWaveResponseCnt_A == 0 : 
                RecordWave_PER_A = 1.0
            if RecordWaveBroadcastCnt_B == 0 or RecordWaveResponseCnt_B == 0 : 
                RecordWave_PER_B = 1.0
            if RecordWaveBroadcastCnt_C == 0 or RecordWaveResponseCnt_C == 0 : 
                RecordWave_PER_C = 1.0

            print('\nA相录波数据上传超时计数:\033[1;33m{0}[PER={1:.2%}]\033[0m B相录波数据上传超时计数:\033[1;32m{2}[PER={3:.2%}]\033[0m C相录波数据上传超时计数:\033[1;31m{4}[PER={5:.2%}]\033[0m'.format(UploadWaveTimeoutCnt_A,RecordWave_PER_A,UploadWaveTimeoutCnt_B,RecordWave_PER_B,UploadWaveTimeoutCnt_C,RecordWave_PER_C))
            
            f.write('{0} A相录波数据上传超时计数:{1}[PER={2:.2%}] B相录波数据上传超时计数:{3}[PER={4:.2%}] C相录波数据上传超时计数:{5}[PER={6:.2%}]\n'.format(CurrentTime,UploadWaveTimeoutCnt_A,RecordWave_PER_A,UploadWaveTimeoutCnt_B,RecordWave_PER_B,UploadWaveTimeoutCnt_C,RecordWave_PER_C))
            
            print('取电流录波广播包计数：\033[1;33m%s\033[0m 取电场录波广播包计数：\033[1;36m%s\033[0m'%(RecordWaveBroadcastCnt_I,RecordWaveBroadcastCnt_V))
            f.write('%s 取电流录波广播包计数：%s 取电场录波广播包计数：%s\n'%(CurrentTime,RecordWaveBroadcastCnt_I,RecordWaveBroadcastCnt_V))
            
            print('取电流录波响应包计数：\033[1;33m%s\033[0m 取电场录波响应包计数：\033[1;36m%s\033[0m'%(RecordWaveResponseCnt_I,RecordWaveResponseCnt_V))
            f.write('%s 取电流录波响应包计数：%s 取电场录波响应包计数：%s\n'%(CurrentTime,RecordWaveResponseCnt_I,RecordWaveResponseCnt_V))
            
    if re.search(r"I OK",RcvSerialData) != None or re.search(r"VEF OK",RcvSerialData) != None :  
        f.write('\n')
        if re.search(r"'A' I OK",RcvSerialData) != None :
            RecordWaveOKCnt_IA += 1
            print('A相电流录波数据：\033[1;32mOK\033[0m')
            f.write('%s A相电流录波数据：OK\n'%CurrentTime)
        if re.search(r"'B' I OK",RcvSerialData) != None :
            RecordWaveOKCnt_IB += 1
            print('B相电流录波数据：\033[1;32mOK\033[0m')
            f.write('%s B相电流录波数据：OK\n'%CurrentTime)
        if re.search(r"'C' I OK",RcvSerialData) != None :
            RecordWaveOKCnt_IC += 1
            print('C相电流录波数据：\033[1;32mOK\033[0m')
            f.write('%s C相电流录波数据：OK\n'%CurrentTime)
            
        if re.search(r"'A' VEF OK",RcvSerialData) != None :
            RecordWaveOKCnt_VA += 1
            print('A相电场录波数据：\033[1;32mOK\033[0m')
            f.write('%s A相电场录波数据：OK\n'%CurrentTime)
        if re.search(r"'B' VEF OK",RcvSerialData) != None :
            RecordWaveOKCnt_VB += 1
            print('B相电场录波数据：\033[1;32mOK\033[0m')
            f.write('%s B相电场录波数据：OK\n'%CurrentTime)
        if re.search(r"'C' VEF OK",RcvSerialData) != None :
            RecordWaveOKCnt_VC += 1
            print('C相电场录波数据：\033[1;32mOK\033[0m')
            f.write('%s C相电场录波数据：OK\n'%CurrentTime)
        
        print('\n手动触发录波计数：\033[1;36m%s\033[0m A相电流录波正常计数：\033[1;33m%s\033[0m B相电流录波正常计数：\033[1;32m%s\033[0m C相电流录波正常计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,RecordWaveOKCnt_IA,RecordWaveOKCnt_IB,RecordWaveOKCnt_IC))
        print('手动触发录波计数：\033[1;36m%s\033[0m A相电场录波正常计数：\033[1;33m%s\033[0m B相电场录波正常计数：\033[1;32m%s\033[0m C相电场录波正常计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,RecordWaveOKCnt_VA,RecordWaveOKCnt_VB,RecordWaveOKCnt_VC))
        print('手动触发录波计数：\033[1;36m%s\033[0m A相放弃上传录波计数：\033[1;33m%s\033[0m B相放弃上传录波计数：\033[1;32m%s\033[0m C相放弃上传录波计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,GiveUpWave_A,GiveUpWave_B,GiveUpWave_C))
        
        f.write('%s 手动触发录波计数：%s A相电流录波正常计数：%s B相电流录波正常计数：%s C相电流录波正常计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,RecordWaveOKCnt_IA,RecordWaveOKCnt_IB,RecordWaveOKCnt_IC))
        f.write('%s 手动触发录波计数：%s A相电场录波正常计数：%s B相电场录波正常计数：%s C相电场录波正常计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,RecordWaveOKCnt_VA,RecordWaveOKCnt_VB,RecordWaveOKCnt_VC))
        f.write('%s 手动触发录波计数：%s A相放弃上传录波计数：%s B相放弃上传录波计数：%s C相放弃上传录波计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,GiveUpWave_A,GiveUpWave_B,GiveUpWave_C))
        
    if re.search(r"All nodes finished, check ground",RcvSerialData) != None :
            RecordWaveOKCnt_ABC += 1
            print('\nABC三相电流电场录波数据：\033[1;32mOK\033[0m 正常计数:\033[1;33m%s\033[0m'%RecordWaveOKCnt_ABC)
            f.write('\n%s ABC三相电流电场录波数据：OK 正常计数:%s\n'%(CurrentTime,RecordWaveOKCnt_ABC))
            
            print('\n手动触发录波计数：\033[1;36m%s\033[0m A相电流录波正常计数：\033[1;33m%s\033[0m B相电流录波正常计数：\033[1;32m%s\033[0m C相电流录波正常计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,RecordWaveOKCnt_IA,RecordWaveOKCnt_IB,RecordWaveOKCnt_IC))
            print('手动触发录波计数：\033[1;36m%s\033[0m A相电场录波正常计数：\033[1;33m%s\033[0m B相电场录波正常计数：\033[1;32m%s\033[0m C相电场录波正常计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,RecordWaveOKCnt_VA,RecordWaveOKCnt_VB,RecordWaveOKCnt_VC))
            print('手动触发录波计数：\033[1;36m%s\033[0m A相放弃上传录波计数：\033[1;33m%s\033[0m B相放弃上传录波计数：\033[1;32m%s\033[0m C相放弃上传录波计数：\033[1;31m%s\033[0m'%(ManualRecordWaveCnt,GiveUpWave_A,GiveUpWave_B,GiveUpWave_C))
            
            f.write('%s 手动触发录波计数：%s A相电流录波正常计数：%s B相电流录波正常计数：%s C相电流录波正常计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,RecordWaveOKCnt_IA,RecordWaveOKCnt_IB,RecordWaveOKCnt_IC))
            f.write('%s 手动触发录波计数：%s A相电场录波正常计数：%s B相电场录波正常计数：%s C相电场录波正常计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,RecordWaveOKCnt_VA,RecordWaveOKCnt_VB,RecordWaveOKCnt_VC))
            f.write('%s 手动触发录波计数：%s A相放弃上传录波计数：%s B相放弃上传录波计数：%s C相放弃上传录波计数：%s\n'%(CurrentTime,ManualRecordWaveCnt,GiveUpWave_A,GiveUpWave_B,GiveUpWave_C))

def RF_CRC_Error_Cnt(RcvSerialData,f,CurrentTime): 
    global RF_CRC_Error_Count
    if re.search(r"RF frame, crc error",RcvSerialData) != None :
        RF_CRC_Error_Count += 1
        print('\nRF CRC Error计数:\033[1;31m%s\033[0m'%RF_CRC_Error_Count)
        f.write('%s \nRF CRC Error计数:%s\n'%(CurrentTime,RF_CRC_Error_Count))

def TestExit():
    import os 
    print('\033[1;31m终止测试\033[0m')
    sys.exit(1)
    # os.system('"taskkill /F /IM python.exe"') 

if __name__ == '__main__':
    t1 = threading.Thread(target=sends, name='sends')
    t2 = threading.Thread(target=reads, name='reads')
    
    t1.start()
    t2.start()
    keyboard.add_hotkey('ctrl+c', TestExit)
