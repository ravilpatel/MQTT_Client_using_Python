# MQTT Client using Python3 for IoT with Local Broker 

A simple Python-based MQTT Client that demonstrates how to connect to an MQTT broker, publish messages, subscribe to topics, and receive real-time data. This project is suitable for beginners learning MQTT as well as developers testing IoT devices.

## Features
- Connect to any MQTT Broker
- Publish messages to MQTT topics
- Subscribe to one or more MQTT topics
- Real-time message reception
- Easy to configure
- Lightweight and beginner friendly
- Built using the Eclipse Paho MQTT Python library

## LIMITATION:
Currently this DOES NOT support ENCRYPTION and certificates

## Steps for running MQTT Local Broker with Client
### Step 0: Check for Python installation
``` shell
python3
```
```python3
print("Everything is working if this is printed properly in terminal")
```

### Step 1: Download Dependency
``` shell
pip install paho-mqtt
pip install paho-mqtt amqtt
```

### Step 2: Run the GUI
``` shell
python3 main.py
```



## NOTE for Broker Name

If you are connecting within the same computer you can use 
``` shell
localhost
```

For external device within same WiFi network you will require to use inet of the device
 **On Windows:** Open Command Prompt and type & look for the "IPv4 Address" under your Wi-Fi adapter [something like wlp0s20***] (e.g., 192.168.1.105).
 ``` shell
ipconfig
```

 **On Mac/Linux:** Open Terminal and type & look for the inet address under your Wi-Fi interface (e.g., 192.168.1.105).
 ``` shell
ifconfig
```
or
``` shell
ip a
```
<img width="902" height="451" alt="image" src="https://github.com/user-attachments/assets/7c4a2413-4948-4f81-b089-2b66a30acbd3" />


## Image Gallery
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/27cee535-e9a4-4eda-a58e-6ce34b48d301" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/974a2bb5-21e1-4613-a7b7-7191bb35047a" />


## Quick Test to check if it works!
- Open the Local Broker tab.
- Ensure the port is set to 1884 (or any port you prefer) and click Start Broker. The status will change to green, and logs will start showing internal broker events.
- Switch back to the MQTT Client tab. 
- The default Broker is already set to localhost and Port 1884 to match the local broker.
- Click Connect, subscribe to test/topic, and publish a message. You will see it echo back in the Received Messages box, and you will see the connection and publishing events logging in real-time on the Local Broker tab.

## How to test with mobile phone if it is working on other device

- Start the broker in the app on Port 1884.
- Download an MQTT app on your smartphone (e.g., MQTT Explorer or MyMQTT, download any MQTT supporting app).
- In your phone's MQTT app, enter your computer's IP address (e.g., 192.168.1.105) and Port 1884.
- Connect! You should see the connection instantly logged in the "Local Broker" tab of your Python GUI, and you can start publishing/subscribe to topics between your phone and your computer.

## Beware of Firewalls

### This is the #1 reason external connections fail. Your computer's firewall will likely block incoming connections to port 1884 by default.

**Windows:** When you run the app, a Windows Defender Firewall prompt might appear. Click Allow access for private networks. 
If you don't see a prompt, you may need to manually go to "Windows Defender Firewall" -> "Advanced Settings" -> "Inbound Rules" and create a rule allowing TCP port 1884.

**Mac:** Go to System Settings -> Network -> Firewall. You may need to disable the firewall temporarily or add a specific rule to allow Python to accept incoming connections.

**Linux (UFW):** You might need to run sudo ufw allow 1884/tcp in your terminal.
