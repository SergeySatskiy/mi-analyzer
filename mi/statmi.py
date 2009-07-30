#!/bin/env python
#
# File:   statmi.py
#
# Author: Sergey Satskiy, copyright (c) 2009
#
# Date:   July 19, 2009
#
# $Id$
#
# Permission to copy, use, modify, sell and distribute this software
# is granted provided this copyright notice appears in all copies.
# This software is provided "as is" without express or implied
# warranty, and with no claim as to its suitability for any purpose.
#


"""
statmi - statistics of mutex instrumentation
"""

import sys, os, os.path
from optparse import OptionParser
from mi       import getExceptionInfo

__version__ = "0.0.1"


class Env:
    """ Env: statements from the log file """

    def __init__( self, string ):
        self.string = string

class Op:
    """ Single operation """

    def __init__( self, op, obj, th, ret, cl ):
        self.operation = op
        self.object    = obj
        self.thread    = th
        self.ret       = ret
        self.clocks    = cl
        self.bt        = []

    def addBt( self, line ):
        """ Adds a back trace line """
        self.bt.append( line )

    def printOp( self ):
        """ prints the operation """
        print "Operation: " + self.operation + " Object: " + self.object + \
              " Thread: " + self.thread + " Return code: " + self.ret +    \
              " Clocks: " + self.clocks
        print "Backtrace:"
        for item in self.bt:
            print "    " + item


def statmiMain():
    """ The ststmi driver """

    parser = OptionParser(
    """
    %prog [options] [fileName]
    Statistics collection in a log file produced by mi
    """ )

    parser.add_option( "-v", "--verbose",
                       action="store_true", dest="verbose", default=False,
                       help="be verbose (default: False)" )

    options, args = parser.parse_args()
    if not len( args ) in [ 0, 1 ]:
        sys.stdout = sys.stderr
        parser.print_help()
        return 1

    verbose = options.verbose

    logFileName = os.environ.get( 'MI_LOGFILE', 'mi.log' )
    if len( args ) == 1:
        logFileName = args[0]

    if not os.path.exists( logFileName ):
        print "Cannot find log file '" + logFileName + "'"
        return 1

    environment = []
    operations = []

    parseLogFile( logFileName, environment, operations, verbose )
    if len( environment ) > 0:
        print "Execution environment:"
        for item in environment:
            print "    " + item.string

    if len( operations ) == 0:
        print "No mutex operations detected"
        return 0

    print "Collected " + str( len(operations) ) + " operations."
    #for item in operations:
    #    item.printOp()

    mutexLegend = {}
    threadLegend = {}
    chains = {}
    mostConsumingOps = {}

    print "Collecting chains and statistics..."
    collectChains( operations, chains,
                   mutexLegend, threadLegend, mostConsumingOps )
    print "Number of threads: " + str( len(threadLegend) )
    print "Number of mutexes: " + str( len(mutexLegend) )

    analyse( operations, verbose )
    return 0


def collectChains( operations, chains,
                   mutexLegend, threadLegend, mostConsumingOps ):
    """ Collects statistics and operations chains """

    currentChains = {}
    for op in operations:
        mutexShortName = getMutexName( mutexLegend, op.object )
        threadShortName = getThreadName( threadLegend, op.thread )


def getMutexName( legend, id ):
    """ returns an existed or a newly created short mutex name """
    if legend.has_key( id ):
        return legend[ id ]
    name = "m" + str( len( legend ) )
    legend[ id ] = name
    return name


def getThreadName( legend, id ):
    """ returns an existed or a newly created short thread name """
    if legend.has_key( id ):
        return legend[ id ]
    name = "t" + str( len( legend ) )
    legend[ id ] = name
    return name


def analyse( operations, verbose ):
    """ analyses the collected operations """

    return

def parseLogFile( logFileName, environment, operations, verbose ):
    """ reads and parses log file """

    f = open( logFileName )
    line = f.readline()
    while line:
        line = line.strip()
        if line == "":
            line = f.readline()
            continue
        if line.startswith( "Env: " ):
            environment.append( Env( line.replace( "Env: ", "" ).strip() ) )
            line = f.readline()
            continue
        if line.startswith( "Op: " ):
            parts = line.split()
            if len(parts) != 10:
                raise Exception( "Unexpected Op: statement format in " \
                                 "line '" + line + "'" )
            op = Op( parts[1].strip(), parts[3].strip(), parts[5].strip(),
                     parts[7].strip(), parts[9].strip()  )
            line = f.readline()
            while line:
                if not line.startswith( "Bt: " ):
                    break
                op.addBt( line.replace( "Bt: ", "" ).strip() )
                line = f.readline()
            operations.append( op )
            continue
        print "Warning: unrecognised log file line: '" + line + "'. Ignoring."
        line = f.readline()
        continue
    f.close()

    return



# The script execution entry point
if __name__ == "__main__":
    returnCode = 0
    try:
        returnCode = statmiMain()
    except:
        message = getExceptionInfo()
        if message.startswith( "Exception is cought. 0" ):
            returnCode = 0
        else:
            print >> sys.stderr, message
            returnCode = 107
    sys.exit( returnCode )

