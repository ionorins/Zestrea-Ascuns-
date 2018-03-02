#!/usr/bin/python
import MFRC522
import signal
import ConfigParser
import os
import pygame

Config = ConfigParser.ConfigParser()
Config.read("/home/pi/MFRC522-python/rfidconfig.txt")

# From https://wiki.python.org/moin/ConfigParserExamples
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

#initialising music player
pygame.init()
pygame.mixer.init()
music = pygame.mixer.music

#play song
def TagToMplayer (strTag, arg=0):
    try:
        strLocation = ConfigSectionMap(strTag)['location']
        print(strLocation)
        music.load(strLocation)
        music.play(loops=-1)
    except:
        pass

continue_reading = True
MIFAREReader = MFRC522.MFRC522()

#stop function
def end_read(signal, frame):
    global continue_reading
    continue_reading = False
    print("Ctrl+C captured, ending read.")
    MIFAREReader.GPIO_CLEEN()

signal.signal(signal.SIGINT, end_read)

def to_string(backData):
    return str(backData).replace(']','').replace('[','').replace(' ', '')

#setting vars
currently_playing = ""
i = 0
detected = False

#never stop reading
while continue_reading:
    #get tag status
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        i = 0
    else:
        i += 1
    if i > 1:
        music.pause()
        detected = False

    (status,backData) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        #tag detected decision tree
        strbackData = to_string(backData)
        if strbackData != currently_playing:
            currently_playing = strbackData
            TagToMplayer(strbackData)
        elif not detected:
            music.unpause()
        detected = True
