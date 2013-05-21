#       Copyright (C) 2013
#       Written on behalf of Flirc
#       by Sean Poyser (seanpoyser@gmail.com)
#

import utils

utils.log("Service Starting")


#import default
#default.main('minimal', True)

try:
    if utils.getSetting('autoStart') == 'true':
        utils.log("Initialising Automatic Programming Mode")

        import default
        default.main(utils.MINIMAL, True)

except Exception, e:
    utils.log("******************* ERROR IN SERVICE *******************")
    utils.log(e)