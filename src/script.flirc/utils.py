#       Copyright (C) 2013
#       Written on behalf of Flirc
#       by Sean Poyser (seanpoyser@gmail.com)
#

import xbmc
import xbmcaddon
import xbmcgui
import os

ADDON = xbmcaddon.Addon()

CLOSED  = 100
RUNNING = 200

MINIMAL = 1000
XBMC    = 2000

FLIRC_OK        = 1

RECORD_OK       = 200
BUTTON_EXISTS   = 201
NO_FLIRC        = 202
RECORD_CANCELED = 203
ERASE_OK        = 204
ERASE_NOT_FOUND = 205
ERASE_CANCELED  = 206
FORMATTED       = 207
TRANSFER_ERROR  = 208
INVALID         = 209
NO_SPACE        = 210
NO_LIBRARY      = 211
LOAD_OK         = 212
SAVE_OK         = 213
UPGRADE_OK      = 214
UPGRADE_FAILED  = 215

RECORD_TEXT   = 300
AUTO_TEXT     = 301
AUTO_OK       = 302
FIRMWARE_TEXT = 303


OFFSETS      = { XBMC : 'xbmc', MINIMAL : 'minimal' } 
ARCHITECTURE = ['armv6l', 'armv7l']


def getStyle(style):
    try:
        return OFFSETS[style]
    except:
        log("STYLE = %s" % str(style))
        

def getString(id):
     return ADDON.getLocalizedString(id)  


def switchController(style):
    if style == XBMC:
        return MINIMAL
    if style == MINIMAL:
        return XBMC
    return XBMC


def getRecordCommandString(id):
    cmd = ADDON.getLocalizedString(id+10000)
    if cmd == '':
        cmd = ADDON.getLocalizedString(id)
    return cmd


def getFirmwareString(version):
    if version == 0:
        return ' '
    return ADDON.getLocalizedString(FIRMWARE_TEXT) % str(version)


def log(text):
    xbmc.log("[FLIRC] : %s" % str(text), xbmc.LOGDEBUG)
    #xbmc.log("[FLIRC] : %s" % str(text))

def getSystem():
    system            = dict()
    processor         = 'Unknown'
    system['machine'] = 'unknown'

    try:        
        if hasattr(os, 'uname'):
            #unix
            (sysname, nodename, release, version, machine) = os.uname()
        else:
            #Windows (and others?)
            import platform
            (sysname, nodename, release, version, machine, processor) = platform.uname()

        system['nodename']  = nodename
        system['sysname']   = sysname
        system['release']   = release
        system['version']   = version
        system['machine']   = machine
        system['processor'] = processor
    except Exception as ex:
        import sys
        system['sysname']   = sys.platform
        system['exception'] = str(ex)

    return system


def getAddonPath():
    return ADDON.getAddonInfo('path')


def getUserdataPath():
    return xbmc.translatePath(ADDON.getAddonInfo('profile'))


def getFlircLibrary():    
    system  = getSystem()

    sysname = system['sysname']
    machine = system['machine']

    path = xbmc.translatePath(ADDON.getAddonInfo('path')) 
    path = os.path.join(path, 'libraries', sysname, machine, 'libflirc')
    log('library path = %s' % path)
    return path


def getRestoreFW():
    path = xbmc.translatePath(ADDON.getAddonInfo('path')) 
    path = os.path.join(path, 'firmware', 'fw_1.0.bin')
    return path


def setSetting(setting, value):
    xbmcaddon.Addon(id = 'script.flirc').setSetting(setting, value)


def getSetting(setting):
    return xbmcaddon.Addon(id = 'script.flirc').getSetting(setting)


def hideCancelButton():
    #xbmc.sleep(250)
    WINDOW_PROGRESS = xbmcgui.Window(10101)
    CANCEL_BUTTON   = WINDOW_PROGRESS.getControl(10)
    CANCEL_BUTTON.setVisible(False)


def ok(title, line1, line2 = 0, line3 = 0):
    dlg = xbmcgui.Dialog()
    dlg.ok(getString(title), getString(line1), getString(line2), getString(line3))


def progress(title, line1 = 0, line2 = 0, line3 = 0, hide = True):
    dp = xbmcgui.DialogProgress()
    dp.create(getString(title), getString(line1), getString(line2), getString(line3))
    dp.update(0)
    if hide:
        hideCancelButton()
    return dp


def yesno(title, line1, line2 = 0, line3 = 0, no = 3, yes = 2):
    dlg = xbmcgui.Dialog()
    return dlg.yesno(getString(title), getString(line1), getString(line2), getString(line3), getString(no), getString(yes)) == 1


def fileBrowse(title, ext):
    default  = 'c:/'
    dlg      = xbmcgui.Dialog()
    filename = dlg.browse(1, getString(title), 'files', '.'+ext, False, False, default)

    if filename == default:
        return None

    return filename


def folderBrowse(title):
    default  = 'c:/'
    dlg      = xbmcgui.Dialog()
    folder   = dlg.browse(3, getString(title), 'files', '', False, False, default)

    return folder