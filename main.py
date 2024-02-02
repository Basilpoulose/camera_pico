import uos
import machine
import utime
import ubinascii

recv_buf="" # receive buffer global variable

print()
print("Machine: \t" + uos.uname()[4])
print("MicroPython: \t" + uos.uname()[3])

uart0 = machine.UART(0, baudrate=115200)
print(uart0)

def Rx_ESP_Data():
    recv=bytes()
    while uart0.any()>0:
        recv+=uart0.read(1)
    res=recv.decode('utf-8')
    return res

def Connect_WiFi(cmd, uart=uart0, timeout=3000):
    print("CMD: " + cmd)
    uart.write(cmd)
    utime.sleep(7.0)
    Wait_ESP_Rsp(uart, timeout)
    print()

def Send_AT_Cmd(cmd, uart=uart0, timeout=3000):
    print("CMD: " + cmd)
    uart.write(cmd)
    Wait_ESP_Rsp(uart, timeout)
    print()
    
def Wait_ESP_Rsp(uart=uart0, timeout=3000):
    prvMills = utime.ticks_ms()
    resp = b""
    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])
    print("resp:")
    try:
        print(resp.decode())
    except UnicodeError:
        print(resp)
        
base64_image = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAADAFBMVEUAAAAAADMAAGYAAJkAAMwAAP8zAAAzADMzAGYzAJkzAMwzAP9mAABmADNmAGZmAJlmAMxmAP+ZAACZADOZAGaZAJmZAMyZAP/MAADMADPMAGbMAJnMAMzMAP//AAD/ADP/AGb/AJn/AMz/AP8AMwAAMzMAM2YAM5kAM8wAM/8zMwAzMzMzM2YzM5kzM8wzM/9mMwBmMzNmM2ZmM5lmM8xmM/+ZMwCZMzOZM2aZM5mZM8yZM//MMwDMMzPMM2bMM5nMM8zMM///MwD/MzP/M2b/M5n/M8z/M/8AZgAAZjMAZmYAZpkAZswAZv8zZgAzZjMzZmYzZpkzZswzZv9mZgBmZjNmZmZmZplmZsxmZv+ZZgCZZjOZZmaZZpmZZsyZZv/MZgDMZjPMZmbMZpnMZszMZv//ZgD/ZjP/Zmb/Zpn/Zsz/Zv8AmQAAmTMAmWYAmZkAmcwAmf8zmQAzmTMzmWYzmZkzmcwzmf9mmQBmmTNmmWZmmZlmmcxmmf+ZmQCZmTOZmWaZmZmZmcyZmf/MmQDMmTPMmWbMmZnMmczMmf//mQD/mTP/mWb/mZn/mcz/mf8AzAAAzDMAzGYAzJkAzMwAzP8zzAAzzDMzzGYzzJkzzMwzzP9mzABmzDNmzGZmzJlmzMxmzP+ZzACZzDOZzGaZzJmZzMyZzP/MzADMzDPMzGbMzJnMzMzMzP//zAD/zDP/zGb/zJn/zMz/zP8A/wAA/zMA/2YA/5kA/8wA//8z/wAz/zMz/2Yz/5kz/8wz//9m/wBm/zNm/2Zm/5lm/8xm//+Z/wCZ/zOZ/2aZ/5mZ/8yZ///M/wDM/zPM/2bM/5nM/8zM/////wD//zP//2b//5n//8z///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWa2QxAAAAeHRSTlP//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wB8VxiMAAAAhklEQVR42q3T0Q2AMAgEUMZhQ0ZlHf2w9u5KU0zkS3tPUy1YJlbcRQtpHI4qQEgpiNgI28QvMcndRbQA5SpseV5EAywbYIFgJCgaoPpCFBbVKlz3Ae0d7n4ACUu+gvwGwivAwiXH06z+JDWMz7OYL+CW86fm89qTnEe/7c+D0xi98/Duxv8CwEAbMJxWnN4AAAAASUVORK5CYII='
    
Send_AT_Cmd('AT\r\n')          #Test AT startup
Send_AT_Cmd('AT+GMR\r\n')      #Check version information
Send_AT_Cmd('AT+CIPSERVER=0\r\n')      #Check version information
Send_AT_Cmd('AT+RST\r\n')      #Check version information
utime.sleep(5.0)
Send_AT_Cmd('AT+RESTORE\r\n')  #Restore Factory Default Settings
Send_AT_Cmd('AT+CWMODE?\r\n')  #Query the WiFi mode
Send_AT_Cmd('AT+CWMODE=1\r\n') #Set the WiFi mode = Station mode
Send_AT_Cmd('AT+CWMODE?\r\n')  #Query the WiFi mode again
#Send_AT_Cmd('AT+CWLAP\r\n', timeout=10000) #List available APs
Connect_WiFi('AT+CWJAP="hictros_wifi","hictros@2024"\r\n', timeout=5000) #Connect to AP
Send_AT_Cmd('AT+CIFSR\r\n')    #Obtain the Local IP Address
utime.sleep(5.0)
Send_AT_Cmd('AT+CWJAP?\r\n')
Send_AT_Cmd('AT+CIPMUX=1\r\n')    #Obtain the Local IP Address
utime.sleep(1.0)
Send_AT_Cmd('AT+CIPSERVER=1,80\r\n')    #Obtain the Local IP Address
utime.sleep(1.0)
print ('Starting connection to ESP8266...')

while True:
    res =""
    res=Rx_ESP_Data()
    utime.sleep(2.0)
    if '+IPD' in res: # if the buffer contains IPD(a connection), then respond with HTML handshake
        id_index = res.find('+IPD')
        print("resp:")
        print(res)
        connection_id =  res[id_index+5]
        print("connectionId:" + connection_id)
        print ('! Incoming connection - sending webpage')
        html_content = """\
HTTP/1.1 200 OK\r\n\
Content-Type: text/html\r\n\
Connection: close\r\n\
\r\n\
<!DOCTYPE html>\r\n\
<html>\r\n\
<head>\r\n\
    <title>Welcome To My Webpage</title>\r\n\
</head>\r\n\
<body>\r\n\
    <h2>My Webpage</h2>\r\n\
    <p>This is a demo of the &lt;img&gt; tag.</p>\r\n\
    <img src="data:image/jpeg;base64,{}" alt="Pre-converted Image" />\r\n\
</body>\r\n\
</html>\r\n\
""".format(base64_image)

        uart0.write('AT+CIPSEND=' + connection_id + ',' + str(len(html_content)) + '\r\n')  #Send a HTTP response then a webpage as bytes the 108 is the amount of bytes you are sending, change this if you change the data sent below
        utime.sleep(1.0)
        uart0.write(html_content)
        utime.sleep(4.0)
        Send_AT_Cmd('AT+CIPCLOSE='+ connection_id+'\r\n') # once file sent, close connection
        utime.sleep(2.0)
        recv_buf="" #reset buffer
        print ('Waiting For connection...')

