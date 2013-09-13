#       Copyright (C) 2013
#       Written on behalf of Flirc
#       by Sean Poyser (seanpoyser@gmail.com)
#


import application
import utils


def main(style = utils.XBMC, auto = False):
    app = None
    try:    
        app = application.Application()
        app.run(style, auto)
    except Exception, e:
        utils.log("******************* ERROR IN MAIN *******************")
        utils.log(e)
        raise

    if app:
        del app

if __name__ == '__main__': 
    main()