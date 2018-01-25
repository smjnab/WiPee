# WiPee
Run code on a WiPy and with two cables connected to port 11 and 12 the WiPy will notice connection and trigger an email using AWS services. 

## Dependencies
* https://pycom.io/hardware/wipy-3-0-specs/ with latest firmware.
* Pycoms AWSIoTPythonSDK, https://github.com/pycom/aws-pycom/tree/master/AWSIoTPythonSDK
* AWS account https://aws.amazon.com to use IoT, Lambda and SES.
* Various cables, a box and what not you might have at home or can obtain easily.

## Configuring WiPy
* Connect to the WiPy. https://docs.pycom.io/chapter/gettingstarted/ I use Visual Studio Code with the Pymakr plugin.
* Update to latest firmware, contains dependencies for Pycoms AWSIoTPythonSDK. https://docs.pycom.io/chapter/gettingstarted/installation/firmwaretool.html
* Download https://github.com/pycom/aws-pycom/tree/master/AWSIoTPythonSDK and put the files info flash/lib/. For example use FTP as described https://docs.pycom.io/chapter/toolsandfeatures/FTP.html
* Get certificates for AWS IoT and using FTP upload to flash/cert/ and name them ca.pem, certificate.pem.crt and private.pem.key. You can have other names, but remember to update main.py.
* Open main.py and edit the following:
```
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
wlanAntType = WLAN.EXT_ANT # Specify ext or int antenna of the wipy. WLAN.INT_ANT
```
and
```
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

```
and optionally 
```
###################################################################################################
# CONFIG WATER MONITORING
###################################################################################################

# Setup pins used for water detection.
pinCricital = Pin('P12', mode=Pin.IN, pull=Pin.PULL_UP)
pinWarning = Pin('P11', mode=Pin.IN, pull=Pin.PULL_UP)

# Every .5 sec cNormal, cWarning or cCritical goes up 1, when reaching 10 water level confirmed.
monitorTick = 0.5

# How long in ms device should sleep between meassure runs.
deepSleepTime = 300000 # 300000 = 5 min
```
If we assume you have the certificates for AWS and done all the above, then uploading the edited main.py and resetting the device is all that is needed for it to begin monitoring. 

If we assume you have IoT and Lambda configured, then in a few seconds a mail should come letting you know WiPee is up and running.

If we assume you have connected two cables, one to pin 11 and ground and one to pin 12 and ground, then dipping them in water, will send you a new mail at the next monitoring run.


## Configuring AWS
Links to tutorials/documentation as too much for here.

## Configuring Hardware
Images + descriptions of power, ground, 11 and 12 pins.
