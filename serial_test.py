import serial
import math


def imuData():
    aix = None
    aiy = None
    aiz = None
    vectors = [None, None, None, None]

    with serial.Serial('COM3', 115200, timeout=1) as ser: # this is for windows (Lavindu)
    # with serial.Serial('/dev/tty.usbmodem14201', 115200, timeout=1) as ser: # this is for Arushi
        line = str(ser.readline())   # read a '\n' terminated line
        line = line.rstrip('\n')
        (parts) = line.split(',')
        if ("imu" in parts[0]):
            print("\n{0}:{1:>3}".format(parts[1], parts[2]))
            thing = "{0}:{1:>3}".format(parts[1], parts[2])

            ax = float(parts[3])
            ay = float(parts[4])
            az = float(parts[5])
            magnitude = float(parts[6])

            if (aix == None or aiy == None or aiz == None):
                aix = float(parts[3])
                aiy = float(parts[4])
                aiz = float(parts[5])

            afx = ax - aix
            afy = ay - aiy
            afz = az - aiz

            magnitude = float(parts[6])
            mag2 = (afx ** 2 + afy ** 2 + afz ** 2) ** .5

            vectors = [afx, afy, afz, mag2, thing]

    return vectors


imuData()
'''
# U is our summative vector
print("AX {0:12} AY {1:12} AZ {2:12}".format(afx, afy, afz))
print("MAG {0:7}".format(magnitude))
print("MAG2 {0:7}".format(mag2))

# alpha is the angle between U and the x-axis.
# beta is the angle between U and the y-axis.
# gamma is the angle between U and the z-axis.
alpha = 0
beta = 0
gamma = 0
if (afx != 0):
    alpha = math.atan(afy/afx)*180/math.pi
if (afy != 0):
    beta = math.atan(afz/afy)*180/math.pi
if (afz != 0):
    gamma = math.atan(afx / afz) * 180 / math.pi

print("A {0:7} B {1:7} G {2:7}".format(alpha, beta, gamma))

roll = float(parts[7])*180/math.pi
pitch = float(parts[8])*180/math.pi
yaw = float(parts[9])*180/math.pi

print("OR {0:12} OP {1:12} OY {2:12}".format(roll, pitch, yaw))

if (roll > 3):
    print("Roll  : Positive {:05.2f}".format(roll))
elif (roll < -3):
    print("Roll  : Negative {:05.2f}".format(roll))
else:
    print("Roll  : Stable")

if (pitch > 3):
    print("Pitch : Positive {:05.2f}".format(pitch))
elif(pitch < -3):
    print("Pitch : Negative {:05.2f}".format(pitch))
else:
    print("Pitch : Stable")

if (yaw > 3):
    print("Yaw   : Positive {:05.2f}".format(yaw))
elif(yaw < -3):
    print("Yaw   : Negative {:05.2f}".format(yaw))
else:
    print("Yaw   : Stable ")

print("G {}".format(parts[10]))
elif ("gps" in parts[0]):
pass'''
