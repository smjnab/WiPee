import time
import json
import machine
import os
from network import WLAN
from machine import Pin
from MQTTLib import AWSIoTMQTTClient


###################################################################################################
# CONFIG NETWORK
###################################################################################################

ip = 'EDIT_ME'              # IP to set for wipy.
subnet = '255.255.255.0'    # Subnet, most likely leave as is.
router = 'EDIT_ME'          # Router of network, usually x.x.x.1
dns = '8.8.8.8'             # IP of dns to use, 8.8.8.8 is a google dns.
wlanName = 'EDIT_ME'        # Name of WLAN to connect to.
wlanPass = 'EDIT_ME'        # Pass of WLAN to connect to.
wlanType = WLAN.WPA2        # Type of network security.
wlanAntType = WLAN.EXT_ANT  # Specify ext or int antenna of the wipy. WLAN.INT_ANT


###################################################################################################
# CONFIG AWS IOT
###################################################################################################

awsPort = 8883                                    # Port of AWS IoT endpoint.
awsHost = 'EDIT_ME'                     # Your x.iot.eu-west-1.amazonaws.com
awsRootCA = '/flash/cert/ca.pem'                  # Root CA file.
awsClientCert = '/flash/cert/certificate.pem.crt' # Certificate.
awsPrivateKey = '/flash/cert/private.pem.key'     # Private key.

clientID = 'EDIT_ME'            # ID used when sending messages to AWS IoT.
topic = 'EDIT_ME'               # Name of the topic to send messages to.
offlineQueueSize = 0            # 0 disabled.
connectDisconnectTimeout = 10   # After 10 seconds from connecting, disconnect.


###################################################################################################
# CONFIG WATER MONITORING
###################################################################################################

# Setup pins used for water detection.
pinCricital = Pin('P12', mode=Pin.IN, pull=Pin.PULL_UP)
pinWarning = Pin('P11', mode=Pin.IN, pull=Pin.PULL_UP)

# Every .5 sec cNormal, cWarning or cCritical goes up 1, when reaching 10 water level confirmed.
monitorTick = 0.5

# How long in ms device should sleep between meassure runs.
deepSleepTime = 300000  # 300000 = 5 min

############################
### No edit needed below ###
############################

# Count how many loops water has been at a level.
cNormal = 0
cWarning = 0
cCritical = 0

# Track time when water reaches different levels.
timeNormal = time.time()        # only for init
timeWarning = time.time()       # only for init
timeCritical = time.time()      # only for init
timeDiff = time.time()          # only for init
timeDiffCritical = time.time()  # only for init
timeWeeklyMail = time.time()    # only for init


###################################################################################################
# CONVERT SECONDS INTO HOURS, MINUTES AND SECONDS
###################################################################################################

def TimeStr(timeDiff):
    hours = 0
    minutes = 0
    seconds = 0

    # More than an hour, get full hours and deduct from timeDiff.
    if timeDiff > 3600:
        hours = int(timeDiff / 3600)
        timeDiff = timeDiff - (3600 * hours)

    # More than a minute left, get full minute(s) and deduct from timeDiff.
    if timeDiff > 60:
        minutes = int(timeDiff / 60)
        timeDiff = timeDiff - (60 * minutes)

    # timeDiff left is seconds left.
    seconds = timeDiff

    # Return string H:M:S
    return str(hours) + ":" + str(minutes) + ":" + str(seconds)


###################################################################################################
# PUBLISH MESSAGE TO MQTT TOPIC
###################################################################################################

def PublishMQTT(mailType, timeString="", timeStringCritical=""):

    ConnectWLAN(True)

    # Config MQTT
    mqttClient = AWSIoTMQTTClient(clientID)
    mqttClient.configureEndpoint(awsHost, awsPort)
    mqttClient.configureCredentials(awsRootCA, awsPrivateKey, awsClientCert)
    mqttClient.configureOfflinePublishQueueing(offlineQueueSize)
    mqttClient.configureConnectDisconnectTimeout(connectDisconnectTimeout)

    # Connect
    if mqttClient.connect():
        print("MQTT connected")

    # Publish topic, AWS Lambda Python code uses the json to create mail title and body.
    mqttClient.publish(topic, json.dumps(
        {
            "mailType": str(mailType),
            "timeString": timeString,
            "timeStringCritical": timeStringCritical
        }), 0)

    # Disconnect
    if mqttClient.disconnect():
        print("MQTT disconnected")

    ConnectWLAN(False)

    # Save variables to be loaded when waking up from deep sleep.
    Save()

    machine.deepsleep(deepSleepTime)


###################################################################################################
# WLAN CONNECT / DISCONNECT
###################################################################################################

def ConnectWLAN(onOff):
    wlan = WLAN()

    # Connect to wlan
    if onOff:
        wlan.antenna(wlanAntType)

        if machine.reset_cause() != machine.SOFT_RESET:
            wlan.init(mode=WLAN.STA)
            wlan.ifconfig(config=(ip, subnet, router, dns))

        if not wlan.isconnected():
            wlan.connect(wlanName, auth=(wlanType, wlanPass), timeout=5000)

            while not wlan.isconnected():
                machine.idle()

    # Disconnect from wlan
    else:
        wlan.disconnect()

        while wlan.isconnected():
            machine.idle()


###################################################################################################
# SAVE AND LOAD
###################################################################################################

# Save int variables to text files as strings.
def Save():
    global cNormal
    global cWarning
    global cCritical
    global timeNormal
    global timeWarning
    global timeCritical
    global timeWeeklyMail

    f = open('cNormal.txt', 'w')
    f.write(str(cNormal))
    f.close()

    f = open('cWarning.txt', 'w')
    f.write(str(cWarning))
    f.close()

    f = open('cCritical.txt', 'w')
    f.write(str(cCritical))
    f.close()

    f = open('timeNormal.txt', 'w')
    f.write(str(timeNormal))
    f.close()

    f = open('timeWarning.txt', 'w')
    f.write(str(timeWarning))
    f.close()

    f = open('timeCritical.txt', 'w')
    f.write(str(timeCritical))
    f.close()

    f = open('timeWeeklyMail.txt', 'w')
    f.write(str(timeWeeklyMail))
    f.close()


# Read string values from text files and update variables as int.
def Load():

    # If machine was reset or booted first time, make sure there are no saved variables and don't load anything.
    if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        try:
            os.remove('cNormal.txt')
            os.remove('cWarning.txt')
            os.remove('cCritical.txt')
            os.remove('timeNormal.txt')
            os.remove('timeWarning.txt')
            os.remove('timeCritical.txt')
            os.remove('timeWeeklyMail.txt')
        except:
            pass
        return

    global cNormal
    global cWarning
    global cCritical
    global timeNormal
    global timeWarning
    global timeCritical
    global timeWeeklyMail

    f = open('cNormal.txt')
    cNormal = int(f.read())
    f.close()

    f = open('cWarning.txt')
    cWarning = int(f.read())
    f.close()

    f = open('cCritical.txt')
    cCritical = int(f.read())
    f.close()

    f = open('timeNormal.txt')
    timeNormal = int(f.read())
    f.close()

    f = open('timeWarning.txt')
    timeWarning = int(f.read())
    f.close()

    f = open('timeCritical.txt')
    timeCritical = int(f.read())
    f.close()

    f = open('timeWeeklyMail.txt')
    timeWeeklyMail = int(f.read())
    f.close()


###################################################################################################
# MONITOR WATER LEVELS LOOP.
###################################################################################################

# Check and load variables.
Load()

while True:

    ###################################################################################################
    # SEND WEEKLY CHECKIN MAIL
    ###################################################################################################

    if time.time() - timeWeeklyMail > 604800:  # 604800 sec = 7 days
        timeWeeklyMail = time.time()
        PublishMQTT(5)
        break

    ###################################################################################################
    # GET PIN STATUS
    ###################################################################################################

    critical = pinCricital()
    warning = pinWarning()

    ###################################################################################################
    # WATER LEVEL CRITICAL
    ###################################################################################################

    if critical == False:
        cCritical += 1

        # Reset other counters to make sure they are always 0.
        cWarning = 0
        cNormal = 0

        # Set time when reached critical and calculate how long it has been since normal.
        if cCritical == 10:
            timeCritical = time.time()
            timeDiff = timeCritical - timeWarning
            timeDiffCritical = timeCritical - timeNormal

            PublishMQTT(4, TimeStr(timeDiff), TimeStr(timeDiffCritical))
            break

        if cCritical >= 10:
            machine.deepsleep(deepSleepTime)

    ###################################################################################################
    # WATER LEVEL ELEVATED
    ###################################################################################################

    elif warning == False:
        cWarning += 1

        # Set time when reached elevated.
        if cWarning == 10:
            timeWarning = time.time()

        # Send dropped from critical to elevated message.
        if cCritical >= 10 and cWarning >= 10:
            timeDiff = timeWarning - timeCritical
            cCritical = 0
            PublishMQTT(2, TimeStr(timeDiff))
            break

        # Send reached elevated from normal message.
        if cNormal >= 10 and cWarning >= 10:
            timeDiff = timeWarning - timeNormal
            cNormal = 0
            PublishMQTT(3, TimeStr(timeDiff))
            break

        if cWarning >= 10:
            machine.deepsleep(deepSleepTime)

    ###################################################################################################
    # WATER LEVEL NORMAL
    ###################################################################################################

    else:
        cNormal += 1

        # Set time level reached normal and calculate how long it took to go from elevated to normal.
        if cNormal == 10:
            timeNormal = time.time()
            timeDiff = timeNormal - timeWarning

            # Reset counters.
            cCritical = 0
            cWarning = 0

            # Send message level been normal since start of app.
            if machine.reset_cause() != machine.DEEPSLEEP_RESET:
                PublishMQTT(0, TimeStr(timeDiff))

            # Send message level back to normal from elevated.
            else:
                PublishMQTT(1, TimeStr(timeDiff))
            break

        if cNormal >= 10:
            machine.deepsleep(deepSleepTime)

    print("Monitor Update")
    time.sleep(monitorTick)
