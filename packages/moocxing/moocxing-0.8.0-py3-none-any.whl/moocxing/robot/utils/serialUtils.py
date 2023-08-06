import serial.tools.list_ports


def getCom(num=None):
    ComPorts = []
    for comPort in serial.tools.list_ports.comports():
        ComPorts.append(str(comPort).split(" - ")[0].replace('/dev/cu.', '/dev/tty.'))
    try:
        return ComPorts[num]
    except:
        return ComPorts