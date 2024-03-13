import RPi.GPIO as GPIO  
import time  
  
GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号  
GPIO.setup(8, GPIO.IN)  # 将物理引脚8（GPIO15）设置为输入模式  
  
def read_data(pin):  
    data = ''  
    while True:  
        if GPIO.input(pin):  
            data += '1'  
        else:  
            data += '0'  
        time.sleep(0.1)  
        if len(data) >= 8:  # 当接收到8位数据时跳出循环  
            break  
    return data  
  
while True:  
    binary_data = read_data(8)  
    print 'Received binary data:', binary_data  
    decimal_data = int(binary_data, 2)  
    print 'Received decimal data:', decimal_data  
    print 'Received character data:', chr(decimal_data)  
