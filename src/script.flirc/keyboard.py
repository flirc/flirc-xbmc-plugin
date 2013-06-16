#       Copyright (C) 2013
#       Written on behalf of Flirc
#       by Sean Poyser (seanpoyser@gmail.com)
#

import xbmc
import xbmcgui

import time
import os

from threading import Timer 

import utils
import flirc

ACTION_LEFT  = 1
ACTION_RIGHT = 2
ACTION_UP    = 3
ACTION_DOWN  = 4

ACTION_SELECT_ITEM   = 7
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_BACK          = 92

MOUSE_MOVE  = 107
MOUSE_LDOWN = 100
MOUSE_LUP   = 103

INFOBOX    = 200
FIRMWARE   = 300

INFOSECS  = 1000
COUNTDOWN = 5

ERASE       = 1
ERASE_STOP  = 2
GO          = 3
GO_STOP     = 4
CONNECTED   = 5

SWITCH      = 105
SAVE        = 106
LOAD        = 107
CLEAR       = 108
UPGRADE     = 109

# -----------------------------------------------------------------------------------------


class Keyboard(xbmcgui.WindowXML):
    def __new__(cls, style):
        return super(Keyboard, cls).__new__(cls, utils.getStyle(style)+'.xml', utils.getAddonPath())


    def __init__(self, style):        
        super(Keyboard, self).__init__()
        self.style             = style
        self.buttonMin         = self.style + 1

        self.cancelCountdown   = 5
        self.cancelSleep       = 2

        self.firmware = 0

        self.autoModeOn        = False

        self.lockInfobox = False
        self.isConnected = False
        self.infoText    = ''


    def onInit(self):
        #utils.log("onInit")
        #utils.log(dir(self))

        self.flirc = flirc.Flirc()  
        self.timer = Timer(0, self.checkFlirc)
        self.timer.start()

        self.nmrControls = self.getNmrControls()
        self.buttonMax   = self.buttonMin + self.nmrControls - 1

        self.exitMode      = utils.CLOSED
        self.currentButton = 0
        self.showAll()
        self.loseFocus()

        if self.auto:
            autoTimer = Timer(1, self.autoMode)
            autoTimer.start()


    def run(self, auto):
        self.auto = auto
        self.doModal()
        return self.exitMode

              
    def close(self, mode):
        utils.log("Close mode = %d" % mode)

        self.timerOff()
        self.cancelRecording()
        self.cancelErasing()
        self.exitMode = mode
        del self.flirc
        xbmcgui.WindowXML.close(self)


    def switchController(self):
        self.close(utils.switchController(self.style))


    def sleep(self, span):
        xbmc.sleep(250)
        span -= 250
        self.cancelSleep = 2
        while span > 0 and self.cancelSleep > 0:
            #self.cancelSleep = 2
            span -= 50
            xbmc.sleep(50)


    def loseFocus(self):
        self._setFocus(self.style)


    def _setFocus(self, controlId): 
        if self.autoModeOn:
            if controlId <= self.buttonMax:
                controlId += 1000

        if controlId == 0:
            return

        try:            
            self.setFocus(self.getControl(controlId)) 
        except:
            self.setFocus(self.getControl(self.buttonMin+10))

        xbmc.sleep(50)


    def onFocus(self, controlId): 
        #updates text in the infobox for the current focused key 
        if self.lockInfobox:
            return
        
        if controlId > self.buttonMax:
            controlId -= 1000  

        if controlId == SWITCH:
            controlId += self.style
  
        self.setInfoBox(utils.getString(controlId))


    def setInfoBox(self, text):
        #if text is the same then don't update
        if self.infoText == text:
            return 

        self.infoText = text
        self.getControl(INFOBOX).setLabel(text)
        xbmc.sleep(50)


    def doCountdown(self):        
        self.cancelCountdown = 5
        count = COUNTDOWN 
        text  = utils.getString(utils.AUTO_TEXT)
        
        self.lockInfobox = True

        #self.timerOff()
        while count > 0 and self.cancelCountdown > 0:
            self.setInfoBox(text % count)
            self.cancelCountdown = 5
            count -= 1
            xbmc.sleep(1000)
        #self.timerOn()

        self.lockInfobox = False

        #was the coundtdown canceled?
        if self.cancelCountdown < 1:
            self.loseFocus()
            return False

        return True
        

    def autoMode(self):
        if not self.doCountdown():
            return

        self.doAutoMode()

    def doAutoMode(self):        
        
        self.showAll()
        failed = False

        self.autoModeOn = True

        self.timerOff()
        self.flirc.format()

        for i in range(self.buttonMin+10, self.buttonMax+1): #+10 ignore 'Functional' Buttons
            if not self._onClick(i):             
                failed = True
                break 
        self.timerOn()            

        self.autoModeOn = False
        self.getControl(self.style + GO_STOP + 1000).setVisible(False)

        self.showAll()
        self.currentButton = 0
        self.loseFocus()

        if failed:
            return

        utils.setSetting('autoStart', 'false')

        self.lockInfobox = True
        self._setFocus(self.style + GO)
        self.lockInfobox = False

        self.setInfoBox(utils.getString(utils.AUTO_OK))
        self.sleep(10*INFOSECS)
                    

    def onAction(self, action):
        actionId = action.getId()
        buttonId = action.getButtonCode()

        #utils.log("******************* onAction *******************")
        #utils.log(actionId)
        #utils.log(buttonId)

        if self.autoModeOn:
            return

        if actionId == MOUSE_MOVE:
            self.cancelCountdown -= 1
            self.cancelSleep     -= 1
        else:
            self.cancelCountdown = 0
            self.cancelSleep     = 0

        #Handle in onClick
        if actionId == MOUSE_LDOWN:
            return
       
        #Handle cancel/back/esc
        if actionId in [ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_BACK]:
            self.cancelRecording()
            self.cancelErasing()
            if self.currentButton > 0:
                self.showAll()
                self.currentButton = 0
            else:
                self.close(utils.CLOSED)

        #Handle cursor keys
        if actionId in [ACTION_LEFT, ACTION_RIGHT, ACTION_UP, ACTION_DOWN]: 
            if self.currentButton > 0:
                self._setFocus(self.currentButton+1000)
            elif self.getFocusId() == 0 or self.getFocusId() == self.style:
                self._setFocus(self.buttonMin+10)

        #Handle when not over any keys
        if (actionId == MOUSE_MOVE) and (self.getFocusId() == 0) and (self.currentButton == 0):
            self.loseFocus()
            
                                 
    def onClick(self, controlId):
        #utils.log("******************* onClick *******************")
        #utils.log(controlId)

        if self.autoModeOn:
            return

        if controlId == self.style + GO:
            self.freeRemote()
            self.doAutoMode()
            return

        if controlId == SWITCH:
            self.switchController()
            return

        if controlId == UPGRADE:
            self.upgradeFW()
            return

        if controlId == LOAD:
            self.loadConfig()
            return

        if controlId == SAVE:
            self.saveConfig()
            return

        if controlId == CLEAR:
            self.format()
            return

        if controlId == self.style + ERASE:
            self.erase()
            return

        if controlId == self.style + ERASE_STOP + 1000:
            self.cancelErasing()
            return

        if controlId == self.style + GO_STOP + 1000:
            self.cancelAutomode()
            return

        self.freeRemote()

        self.timerOff()        
        self._onClick(controlId)
        self.timerOn()

        self.showAll()
        self._setFocus(self.currentButton)
        self.currentButton = 0


    def _onClick(self, controlId):
        #utils.log('******************* _onClick *******************')
        #utils.log('controId = % d' % controlId)

        if controlId > self.buttonMax:
            controlId -= 1000

        #Handle currently clicked button
        if controlId == self.currentButton:
            self.cancelRecording()
            self.cancelErasing()
            self.showAll()
            return

        return self.startRecording(controlId)


    def checkFlirc(self):
        try:
            if self.flirc.lib == None:
                self.close(utils.CLOSED)    
                return

            self.isConnected = self.flirc.checkConnect()
            self.getControl(self.style + CONNECTED).setVisible(self.isConnected)
            self.getControl(FIRMWARE).setLabel(utils.getFirmwareString(self.flirc.version))            
            self.timerOn()
        except:
            pass


    def timerOn(self):
        self.timerOff()
        self.timer = Timer(1, self.checkFlirc)
        self.timer.start()


    def timerOff(self):
        self.timer.cancel()


    def cancelRecording(self):
        #utils.log("******************* cancelRecording *******************")
        self.flirc.cancelRecording()


    def cancelErasing(self):
        #utils.log("******************* cancelErasing *******************")
        self.flirc.cancelErasing()


    def cancelAutomode(self):
        #utils.log("******************* cancelAutomode *******************")
        #canceling recording will cause automode to be canceled
        self.cancelRecording()


    def erase(self):
        self.showOnly(self.style + ERASE)

        #Not implemented yet
        #if self.flirc.version > 1:
        #    self.getControl(self.style + ERASE_STOP + 1000).setVisible(True)

        self.freeRemote()
        self.timerOff()

        self.lockInfobox = True
        self.setInfoBox(utils.getString(self.style + ERASE_STOP))
        
        response = self.flirc.erase()
        self.timerOn()        
        
        self.setInfoBox(utils.getString(response))        

        self.sleep(INFOSECS) #1 second

        self.showAll()

        self.getControl(self.style + ERASE_STOP + 1000).setVisible(False)

        self.lockInfobox = False
        self._setFocus(self.style + ERASE)


    def format(self):
        #utils.log("******************* format *******************")
        if not utils.yesno(1, 7, 0, 8):
            self.setInfoBox(utils.getString(4))
            return

        self.timerOff()
        self.setInfoBox(utils.getString(9))
        self.sleep(INFOSECS) #1 second   
        response = self.flirc.format()
        self.timerOn()        
        self.setInfoBox(utils.getString(response))
        self.sleep(INFOSECS) #1 second


    def upgradeFW(self):
        utils.log("******************* upgrade *******************")


        filename = utils.fileBrowse(10, 'bin')
        if not filename:
            return

        self.timerOff()
        self.setInfoBox(utils.getString(11))
        self.sleep(INFOSECS) #1 second   
        response = self.flirc.upgradeFW(filename)
        self.timerOn()        
        self.setInfoBox(utils.getString(response))
        self.sleep(INFOSECS) #1 second


    def loadConfig(self):
        utils.log("******************* load *******************")

        filename = utils.fileBrowse(14, 'fcfg')
        if not filename:
            return

        self.timerOff()
        self.setInfoBox(utils.getString(15))
        self.sleep(INFOSECS) #1 second   
        response = self.flirc.loadConfig(filename)
        self.timerOn()        
        self.setInfoBox(utils.getString(response))
        self.sleep(INFOSECS) #1 second


    def saveConfig(self):
        utils.log("******************* save *******************")

        folder = utils.folderBrowse(12)

        filename = 'my_flirc_config.fcfg'
        filename = os.path.join(folder, filename)

        self.timerOff()
        self.setInfoBox(utils.getString(13))
        self.sleep(INFOSECS) #1 second   
        response = self.flirc.saveConfig(filename)
        self.timerOn()        
        self.setInfoBox(utils.getString(response))
        self.sleep(INFOSECS) #1 second


    def startRecording(self, controlId):
        #utils.log("******************* startRecording *******************")
        #utils.log(controlId)
        self.currentButton = controlId

        if self.currentButton == 0:
            return

        self.lockInfobox = True

        self.showOnly(self.currentButton)       

        cmd  = utils.getRecordCommandString(controlId)
        text = utils.getString(utils.RECORD_TEXT) % utils.getString(controlId).lower()

        self.setInfoBox(text)

        response = self.flirc.recordKey(cmd)

        self.setInfoBox(utils.getString(response))

        ret = True
        
        if response == utils.RECORD_OK:
            self.sleep(INFOSECS) #1 second
        else:
            self.sleep(2*INFOSECS) #2 seconds
            ret = False

        #self._setFocus(controlId)

        self.lockInfobox = False

        return ret


    def freeRemote(self):
        #give user time to release 'enter' on remote
        time.sleep(.5)


    def showOnly(self, controlId):
        #utils.log('showOnly %d' % controlId)
        self.hideAll()
        self.getControl(controlId+1000).setVisible(True)

        #Not implemented yet
        #if self.autoModeOn and self.flirc.version > 1: 
        #    self.getControl(self.style + GO_STOP + 1000).setVisible(True)


    def hideAll(self):
        #utils.log('hideAll')
        for i in range(self.buttonMin, self.buttonMax+1):
            self.getControl(i).setVisible(False)
            try:
                self.getControl(i+1000).setVisible(False)  
            except:
                pass
        self.getControl(self.style + CONNECTED).setVisible(self.isConnected)            


    def showAll(self):
        #utils.log('showAll')
        self.hideAll()
        for i in range(self.buttonMin, self.buttonMax+1):
            self.getControl(i).setVisible(True)
        self.getControl(self.style + CONNECTED).setVisible(self.isConnected)            


    def getNmrControls(self):
        utils.log('Count number of keys by \'getting\' each control until EXCEPTION: Non-Existent Control')
        count = 0
        try:
            for i in range(self.buttonMin, self.buttonMin+10000):
                self.getControl(i)
                count += 1
        except:
            pass
        return count