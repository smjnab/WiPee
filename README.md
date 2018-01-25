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
* Upload/Sync main.py and boot.py to the WiPy. All done!

If we assume you have the certificates for AWS and done all the above, then after resetting the device, it will begin monitoring. 

If we assume you have IoT and Lambda configured, then in a few seconds a mail should come letting you know WiPee is up and running.

If we assume you have connected two cables, one to pin 11 and ground and one to pin 12 and ground, then dipping them in water, will send you a new mail at the next monitoring run.


## Configuring AWS
There is too much to write about the AWS bits so I'll link relevant and useful tutorials/documentation for each bit. If completely new to AWS, check out https://aws.amazon.com/ and prepared to be confused, there is a ton of stuff. A good place to start for quick peeks at what you can do, and how to do it, is https://aws.amazon.com/getting-started/tutorials/.

If you have an AWS account or have a new one created (most, maybe even all, will be free tier) then here are the general things needed to be done:

* AWS SES, https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html is a quick start guide. You also get examples and step-by-step in the AWS Lambda articles below.

* AWS Lambda, https://docs.aws.amazon.com/lambda/latest/dg/get-started-create-function.html This is a good place to start trying to set up a Lambda function. This is a way to execute code, as if you had a server but without having to setup a server. You call the Lambda function, it does its thing and then goes back to sleep. To specifically work with sending email, https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html, this guide can be used in combination with setting up a Python Lambda. I'm using Python here, as the rest of the project is Python. But you could as well use, for example, C# or nodejs for this part.

* AWS IoT, https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html I used this guide, followed the steps but instead of using the AWS IoT button I used my WiPy. When uncertain I also used this guide https://docs.pycom.io/chapter/tutorials/all/aws.html You should only look at the section "Creating the message broker (Amazon website)", the rest is already setup and configured with the WiPee script.

My rule in IoT is ```"SELECT mailType, timeString, timeStringCritical FROM 'wipeeMail' WHERE mailType < 10"``` where wipeeMail is the topic I publish messages to. From the add action option, you can select "Invoke a Lambda function passing the message data". There you select the lambda function you created earlier. After doing this, if you go back to Lambda you should see a graphic showing input from IoT to the Lambda function. If you tested and verified that each part works, and updated the main.py with the IoT url and topic, then restarting the WiPy should publish the "I'm up and running" message to your inbox.


## Configuring Hardware
How it is connected and when both cables are "in water".
![breadboard](https://github.com/smjnab/WiPee/blob/master/bread.jpg)

From left to right:
* Blue ground connected to WiPy ground.
* White VIN connected to (THIS IS ERROR, BRAIN FREEZE) 3v3, should have been VIN which is the first pin to the left of the blue ground. Sorry about this. If using 3v3 make sure source is 3v3!
* Yellow is pin 11, connected with ground (blue) and this means water level is elevated.
* White is pin 12, connected with ground (blue) and this means water level is critical.

Add power source and by breaking/making connection for pin 11 and 12 you can simulate the WiPee monitoring changes in water level.


## The final device
Half the stuff I had home and half the stuff (box, antenna) I bought for the project.

![box](https://github.com/smjnab/WiPee/blob/master/box.jpg)

![inside](https://github.com/smjnab/WiPee/blob/master/inside.jpg)

