#       Copyright (C) 2013
#       Written on behalf of Flirc
#       by Sean Poyser (seanpoyser@gmail.com)
#

import utils
import keyboard


class Application(object):
    def __init__(self):
        pass


    def run(self, style, auto):
        utils.createKeymap()

        bkgnd = keyboard.Background()
        bkgnd.show()

        while style != utils.CLOSED:  
            kb    = keyboard.Keyboard(style)
            style = kb.run(auto)
            auto  = False
            del kb

        del bkgnd

        utils.deleteKeymap()