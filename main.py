import time

import csv
import serial
import serial.tools.list_ports
from consolemenu import SelectionMenu

obdList = []
namesList = []

try:
    with open("file.csv") as fileH:
        reader = csv.DictReader(fileH, delimiter=';')
        for line in reader:
            obdList.append(line)
            namesList.append(line["Name"])
except:
    print("Cant found settings file")
    exit()

TIMEOUT = 0.1

def polish_eval(expression, number):
    elements = expression.split()
    pile = []
    while elements:
        e = elements.pop(0)
        if e in ["+", "-", "*", "/"]:
            b = pile.pop()
            a = pile.pop()
            if e == "+":
                pile.append(a + b)
            elif e == "-":
                pile.append(a - b)
            elif e == "*":
                pile.append(a * b)
            elif e == "/":
                pile.append(a / b)
        else:
            if (e == "A"):
                pile.append(number)
            else:
                pile.append(int(e))
    return pile[0]

print("Searching COM ports...")
ports = serial.tools.list_ports.comports()
ports_name = []
for x in ports:
    ports_name.append(x.device)
selectionCOM = SelectionMenu.get_selection(ports_name, "Choose COM port")
if selectionCOM == len(ports_name):
    exit()

bauds = [9600, 19200, 38400, 57600, 115200, 230400]
selectionBAUD = SelectionMenu.get_selection(bauds, "Choose baudrate")
if selectionBAUD == len(bauds):
    exit()
    
try:
    connect = serial.Serial(ports_name[selectionCOM], bauds[selectionBAUD], timeout=TIMEOUT)
except OSError as err:
    print("OS error: {0}".format(err))
    exit()
try:
    connect.write(b"atz\r")
except:
    print("INIT FAIL")
    exit()
time.sleep(1)
msg = connect.read(1024)
msg = msg.replace(b'\r', b'').decode("utf-8")
print("Connected with " + msg[:-1])
try:
    connect.write(b"ate0\r")
except:
    print("INIT FAIL")
    exit()
time.sleep(1)
connect.flushInput()
try:
    connect.write(b"atdp\r")
except:
    print("INIT FAIL")
    exit()
msg = connect.read(1024)
msg = msg.replace(b'\r', b'').decode("utf-8")
print("Selected protocol " + msg[:-1])
try:
    connect.write(b"0100\r")
except:
    print("INIT FAIL")
    exit()
time.sleep(1)
msg = connect.read(1024)
msg = msg.decode("utf-8")
if "BUS INIT: OK" in msg:
    print("Car connected")
else:
    print("Car not connected")
    exit()

answerMsg = ""
while True:
    selectionMenu = SelectionMenu.get_selection(namesList, "Выберите опцию" + answerMsg)
    if selectionMenu == len(namesList):
        break
    msgToSend = obdList[selectionMenu]["PID"]
    try:
        connect.write(msgToSend.encode() + b"\r")
    except:
        print("FAIL TO SEND")
        connect.close()
        exit()
    time.sleep(1)
    answer = connect.read(1024)
    answer = answer[6:-4]
    answer = answer.decode("utf-8")
    answer = answer.replace(" ", "")
    answer = int(answer, 16)
    answer = polish_eval(obdList[selectionMenu]["Formula"], answer)
    answerMsg = "                       Ответ - " + str(answer) + " " + obdList[selectionMenu]["Unit"]

connect.close()