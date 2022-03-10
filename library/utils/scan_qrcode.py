'''
    功能: 扫描二维码
    软件环境: JDK-8
    使用详情: https://github.com/ChenjieXu/pyzxing
    测试结果:
        二维码正常返回(list)：
        [
            {
                'filename': b'file:///D:/Desktop/nsk1178.jpg', 
                'format': b'QR_CODE', 
                'type': b'URI', 
                'raw': b'http://libzwxt.ahnu.edu.cn/seatwx/ScanQrcode.aspx?qrcode=F4A2E0A4-AC49-43C0-8887-DB0FCC73CFC5', 
                'parsed': b'http://libzwxt.ahnu.edu.cn/seatwx/ScanQrcode.aspx?qrcode=F4A2E0A4-AC49-43C0-8887-DB0FCC73CFC5', 
                'points': [(60.0, 355.6111), (38.5, 92.5), (303.5, 72.5), (312.75, 324.5)]
            }
            ,
        ]
        二维码识别错误返回：
        [
            {
                'filename': b'file:///D:/Desktop/213.jpg:'
            }
        ]
'''
import os
from pyzxing import BarCodeReader

def scan_qrcode(file_path):
    '''
        功能: 扫描二维码
        参数: 二维码文件的路径,file_path
        返回: 一个字典
            result = {
                "status":True,                      扫描结果,True为解析完毕,False为错误
                "url":"http://libzwx...C73CFC5"     解析结果,只有解析完毕才有效
                "message:""                         错误信息,只要解析错误才有效
            }
    '''
    result = {
        "status":True,
        "url":"",
        "message":""
    }
    try:
        reader = BarCodeReader()
        barcode = reader.decode(file_path)
        os.remove(file_path)                    # 保证服务器空间充足,每次扫描都会删除二维码

        if len(barcode) == 1:
            barcode = barcode[0]
            check = barcode.get("format",b"None").decode('utf-8','ignore')
            if check == "QR_CODE":
                url = barcode.get("parsed",b"None").decode('utf-8','ignore')
                if "http://libzwxt.ahnu.edu.cn/seatwx/ScanQrcode.aspx?qrcode=" in url:
                    result = {
                        "status":True,
                        "url":url,
                        "message":"二维码上传成功"
                    }
                else:
                    result = {
                        "status":False,
                        "url":"",
                        "message":"二维码识别结果不符合签到规则"
                    }
            else:
                result = {
                    "status":False,
                    "url":"",
                    "message":"无法识别该二维码"
                }
        else:
            result = {
                "status":False,
                "url":"",
                "message":"二维码扫描错误"
            }

    except Exception as E:
        result = {
                "status":False,
                "url":"",
                "message":str(E)
            }

    finally:
        return result

