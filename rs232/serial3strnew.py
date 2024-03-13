import serial  
import time  
  
# 设置串行通信参数  
ser = serial.Serial(  
    port="/dev/serial0",  # 树莓派上的串行端口  
    baudrate=9600,        # 波特率  
    parity=serial.PARITY_NONE,  
    stopbits=serial.STOPBITS_ONE,  
    bytesize=serial.EIGHTBITS,  
    timeout=1             # 读取超时时间（秒）  
)  
  
# 无限循环以接收数据  
while True:  
    try:  
        # 尝试从串行端口读取一行数据  
        received_data = ser.readline().decode("utf-8").strip()  
  
        # 如果收到数据，打印出来  
        if received_data:  
            print("Received data:", received_data)  
  
    except Exception as e:  
        print("Error:", e)  
  
    # 休眠一段时间，以降低CPU占用率  
    time.sleep(0.1)  
