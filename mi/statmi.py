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
__author__  = "Sergey Satskiy <sergey.satskiy@gmail.com>"


warningsCount = 0
errorsCount = 0


class Env:
    """ Env: statements from the log file """

    def __init__( self, string ):
        self.string = string
    def __str__( self ):
        return self.string
    def __repr__( self ):
        return self.__str__()

class Op:
    """ Single operation """

    def __init__( self, op, obj, th, ret, cl ):
        self.operation   = op
        self.object      = obj
        self.thread      = th
        self.ret         = ret
        self.clocks      = int(cl)
        self.backtrace   = []
        self.shortObj    = ""
        self.shortThread = ""

    def addBt( self, line ):
        """ Adds a back trace line """
        self.backtrace.append( line )

    def __str__( self ):
        retVal = "Operation: " + self.operation + " Object: " + self.object
        if self.shortObj != "":
            retVal += "(" + self.shortObj + ")"

        retVal += " Thread: " + self.thread
        if self.shortThread != "":
            retVal += "(" + self.shortThread + ")"

        retVal += " Return code: " + self.ret + " Clocks: " + str(self.clocks)
        if len( self.backtrace ) == 0:
            return retVal

        return retVal + "\nBacktrace:\n    " + "\n    ".join( self.backtrace )

    def __repr__( self ):
        return self.__str__()

    def __eq__( self, other ):
        return self.operation == other.operation and \
               self.object    == other.object and \
               self.thread    == other.thread and \
               self.backtrace == other.backtrace

    def __ne__( self, other ):
        return not self.__eq__( other )


class MostConsumingOperations:
    """ Holds information about the most consuming operations """

    def __init__( self, lim ):
        self.limit = lim
        self.operations = []

    def addOperation( self, oper ):
        """ Adds a single operation to the list if required """

        if oper.clocks == 0:
            return

        if len( self.operations ) == self.limit:
            if oper.clocks < self.operations[ self.limit - 1 ]:
                return

        for index in range( 0, len( self.operations ) ):
            if oper.clocks > self.operations[index].clocks:
                self.operations.insert( index, oper )
                if len( self.operations ) > self.limit:
                    self.operations = self.operations[ :-1 ]
                return
        if len( self.operations ) < self.limit:
            self.operations.append( oper )
        return



def statmiMain():
    """ The ststmi driver """

    parser = OptionParser(
    """
    %prog [options] [fileName]
    Statistics collection in a log file produced by mi
    Return code: 0 - no problems identified
                 1 - there are warnings
                 2 - there are errors
                 >= 3 - errors in the script
    """ )

    parser.add_option( "-v", "--verbose",
                       action="store_true", dest="verbose", default=False,
                       help="be verbose (default: False)" )
    parser.add_option( "-f", "--print-failed",
                       action="store_true", dest="printFailed", default=False,
                       help="print available information about failed " \
                            "operations (default: False)" )
    parser.add_option( "-u", "--ignore-unknown",
                       action="store_true", dest="ignoreUnknown",
                       default=False,
                       help="ignore unknown operations in the mi log file " \
                            "(default: False)" )
    parser.add_option( "-l", "--tco-limit", dest="tcoLimit", default=10,
                       type="int", help="Number of the most time consuming " \
                                   "operations to be memorised (default: 10)" )

    options, args = parser.parse_args()
    if not len( args ) in [ 0, 1 ]:
        sys.stdout = sys.stderr
        parser.print_help()
        return 3

    verbose = options.verbose
    printFailed = options.printFailed

    logFileName = os.environ.get( 'MI_LOGFILE', 'mi.log' )
    if len( args ) == 1:
        logFileName = args[0]

    if not os.path.exists( logFileName ):
        print >> sys.stderr, "Cannot find log file '" + logFileName + "'"
        return 3

    environment      = []
    operations       = []
    failedOperations = []
    mutexLegend      = {}   # 0xZZZZZZZZZZZ -> mZZZ
    threadLegend     = {}   # ULZZZZZZZZZZZ -> tZZZ

    mostConsumingOps = MostConsumingOperations( options.tcoLimit )

    parseLogFile( logFileName,
                  environment, operations, failedOperations, mostConsumingOps,
                  mutexLegend, threadLegend )
    if len( environment ) > 0:
        print "Execution environment:"
        for item in environment:
            print "    " + item.string

    if len( operations ) == 0:
        print "No mutex operations detected"
        return 0

    print "Number of threads: " + str( len(threadLegend) )
    print "Number of mutexes: " + str( len(mutexLegend) )
    print "Successfull operations: " + str( len(operations) )
    print "Failed operations: " + str( len(failedOperations) )

    if printFailed and len(failedOperations) > 0:
        for item in failedOperations:
            print "Failed: " + item

    if len( mostConsumingOps.operations ) > 0:
        print "The most time consuming operations:"
        for item in mostConsumingOps.operations:
            print item


    if verbose:
        print "Collected operations:"
        for item in operations:
            print item

    chains = {}                 # tZZZ -> [ [opx, opy, opz], [opx, opz], ... ]

    print "Collecting chains and statistics..."
    collectChains( operations, chains, threadLegend,
                   options.ignoreUnknown )

    if verbose:
        print "Collected chains:"
        print chains

    if len( operations ) == 0:
        print "The program has not locked any mutexes. No analysis required."
        return 0

    print "Threads legend:"
    for key in threadLegend.keys():
        print threadLegend[ key ] + " -> " + key
    print "Mutexes legend:"
    for key in mutexLegend.keys():
        print mutexLegend[ key ] + " -> " + key

    analyse( chains, verbose )
    return 0


def collectChains( operations, chains, threadLegend, ignoreUnknown ):
    """ Collects statistics and operations chains """

    # Initialise the initial chains
    currentChains = {}
    for key, value in threadLegend.iteritems():
        currentChains[ value ] = [ False, [] ]      # False - should not be
                                                    # added to the chains list

    # process all the operation. The failed operations were excluded
    # at the stage of the reading log file
    for op in operations:

        if op.operation == "lock" or op.operation == "trylock":
            # add the operation and mark as should be added to the chains list
            currentChains[ op.shortThread ][ 0 ] = True
            currentChains[ op.shortThread ][ 1 ].append( op )
            continue

        if op.operation == "unlock":
            lockedMutexIndex = getMutexIndexInChain( op,
                                   currentChains[ op.shortThread ][ 1 ] )
            if lockedMutexIndex == -1:
                printUnlockingNonLockedError( op,
                                              currentChains[op.shortThread][1] )
                continue

            if lockedMutexIndex != len(currentChains[op.shortThread][1]) - 1:
                printUnlockingOrderWarning( op,
                                            currentChains[op.shortThread][1] )

            # Register the chain if required
            if currentChains[ op.shortThread ][ 0 ] == True and \
               len(currentChains[op.shortThread][1]) > 1:
                # Chains of length == 1 are not interesting
                addChain( chains, currentChains[op.shortThread][1] )

            # Delete the operation from the current chain
            del( currentChains[ op.shortThread ][ 1 ][ lockedMutexIndex ] )

            # Reset the chain flag
            currentChains[ op.shortThread ][ 0 ] = False
            continue

        if ignoreUnknown:
            print >> sys.stderr, "WARNING: Unknown operation:\n " + \
                                 str(op) + "\nSkipping."
        else:
            raise Exception( "Unknown operation " + str(op) )

    # Post analysis: there should not be still locked mutexes
    for key, value in currentChains.iteritems():
        if len( value[ 1 ] ) > 0:
            printLeftUnlockedError( value[ 1 ] )
    return


def printUnlockingNonLockedError( unlockOperation, lockChain ):
    """ Prints the error message that a non-locked mutex is unlocked """

    global  errorsCount

    errorsCount += 1
    print >> sys.stderr, "----------------------------\n" \
             "ERROR: Unlocking mutex which is not previously locked.\n" + \
             str(unlockOperation) + "\nCurrently locked mutexes in the thread:"
    if len( lockChain ) == 0:
        print >> sys.stderr, "None"
    else:
        for operation in lockChain:
            print >> sys.stderr, operation
    print >> sys.stderr, "----------------------------"
    return


def printUnlockingOrderWarning( unlockOperation, lockChain ):
    """ Prints the warning message that not the last mutex unlocked """

    global warningsCount

    warningsCount += 1
    print >> sys.stderr, "----------------------------\n" \
             "WARNING: Unlocking not the last locked mutex in the thread\n" + \
             str(unlockOperation) + "\nCurrently locked mutexes in the thread:"
    for operation in lockChain:
        print >> sys.stderr, operation
    print >> sys.stderr, "----------------------------"
    return


def printLeftUnlockedError( chain ):
    """ Prints the error message that some mutexes are left unlocked """

    global errorsCount

    errorsCount += 1
    print >> sys.stderr, "----------------------------\n" \
             "ERROR: Some mutex[es] left locked in the thread:"
    for operation in chain:
        print >> sys.stderr, operation
    print >> sys.stderr, "----------------------------"
    return



def addChain( chains, chain ):
    """ Adds a chain to the collected chains if required """

    shortThread = chain[0].shortThread
    if not chains.has_key( shortThread ):
        chains[ shortThread ] = []

    # check if there is the same or longer chain
    for index in range( 0, len( chains[ shortThread ] ) ):
        compareResult = compareChains( chain, chains[ shortThread ][ index ] )
        if compareResult == 0:
            # Matched or shorter
            return
        if compareResult == 1:
            # Should replace the existed
            chains[ shortThread ][ index ] = chain
            return

    # No such a chain - add it
    chains[ shortThread ].append( list(chain) )
    return


def compareChains( inputChain, existedChain ):
    """ Return value: -1 inputChain differs to the existedChain
                       0 inputChain is the same or shorter than existedChain
                      +1 inputChain covers existed and is longer """

    minLength = min( len(inputChain), len(existedChain) )
    for index in range( 0, minLength ):
        if inputChain[index] != existedChain[index]:
            return -1

    # Here: the common length part of the chains matches

    if len(inputChain) <= len(existedChain):
        return 0

    # Here: input chain is longer and the common part matches

    return 1


def getMutexIndexInChain( operation, chain ):
    """ Searches for the locked mutex in the given chain.
        Returns: -1 if not found """

    for index in range( 0, len( chain ) ):
        if operation.shortObj == chain[ index ].shortObj:
            return index
    return -1


def getMutexName( legend, mutexID ):
    """ returns an existed or a newly created short mutex name """
    if legend.has_key( mutexID ):
        return legend[ mutexID ]
    name = "m" + str( len( legend ) )
    legend[ mutexID ] = name
    return name


def getThreadName( legend, threadID ):
    """ returns an existed or a newly created short thread name """
    if legend.has_key( threadID ):
        return legend[ threadID ]
    name = "t" + str( len( legend ) )
    legend[ threadID ] = name
    return name


def analyse( operations, verbose ):
    """ analyses the collected operations """

    threads = operations.keys()
    for firstThreadIndex in range( 0, len( threads ) - 1 ):
        for secondThreadIndex in range( firstThreadIndex + 1, len( threads ) ):
            if verbose:
                print "Checking threads " + threads[firstThreadIndex] + \
                      " and " + threads[secondThreadIndex] + "..."
            checkLockChains( operations[ threads[firstThreadIndex] ],
                             operations[ threads[secondThreadIndex] ] )
    return

def checkLockChains( firstThreadChains, secondThreadChains ):
    """ check two threads chains"""

    for firstThreadChain in firstThreadChains:
        for secondThreadChain in secondThreadChains:
            checkLockOrder( firstThreadChain, secondThreadChain )
    return


def buildLockPairs( chain ):
    """ builds a list of mutex lock pairs """

    lockPairs = []
    for firstIndex in range( 0, len(chain) - 1 ):
        for secondIndex in range( firstIndex + 1, len(chain) ):
            lockPairs.append( [ chain[firstIndex], chain[secondIndex] ] )
    return lockPairs


def printWrongLockOrderError( firstChain, secondChain,
                              firstPair, secondPair ):
    """ Prints error message that two threads lock
        mutexes in opposite order """

    global errorsCount
    errorsCount += 1

    firstThread = firstChain[0].shortThread
    secondThread = secondChain[0].shortThread

    print >> sys.stderr, "----------------------------\n" \
             "ERROR: potential dead lock detected\n" \
             "Thread " + firstThread + " lock stack:"
    for operation in firstChain:
        print >> sys.stderr, operation
    print >> sys.stderr, "Thread " + secondThread + " lock stack:"
    for operation in secondChain:
        print >> sys.stderr, operation
    print >> sys.stderr, "Thread " + firstThread + " detected pair:\n" + \
             str(firstPair[0]) + "\n" + str(firstPair[1]) + "\n" + \
             "Thread " + secondThread + " detected pair:\n" + \
             str(secondPair[0]) + "\n" + str(secondPair[1]) + "\n" + \
             "----------------------------"
    return



def checkLockOrder( firstChain, secondChain ):
    """ Checks of there are any conflicts in mutex locking order """
    firstLockPairs = buildLockPairs( firstChain )
    secondLockPairs = buildLockPairs( secondChain )

    for firstPair in firstLockPairs:
        for secondPair in secondLockPairs:
            if isLockPairOpposite( firstPair, secondPair ):
                printWrongLockOrderError( firstChain, secondChain,
                                          firstPair, secondPair )
    return


def isLockPairOpposite( first, second ):
    """ Checks if the pairs lock mutexes in opposite order """

    # It considers the case when a chain is a recursive mutex lock
    return first[0].shortObj == second[1].shortObj and \
           first[1].shortObj == second[0].shortObj and \
           first[0].shortObj != first[1].shortObj and \
           second[0].shortObj != second[1].shortObj


def parseLogFile( logFileName,
                  environment, operations, failedOperations, mostConsumingOps,
                  mutexLegend, threadLegend ):
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

            op.shortObj = getMutexName( mutexLegend, op.object )
            op.shortThread = getThreadName( threadLegend, op.thread )

            # Memorise the operation time if needed
            if op.clocks > 0:
                mostConsumingOps.addOperation( op )

            # Check the operation return code
            if int(op.ret) == 0:
                operations.append( op )
            else:
                failedOperations.append( op )
            continue

        raise Exception( "Unrecognised log file line: '" + line + "'." )

    f.close()
    return



# The script execution entry point
if __name__ == "__main__":
    returnCode = 0
    try:
        returnCode = statmiMain()
        if returnCode == 0:
            if errorsCount > 0:
                returnCode = 2
            elif warningsCount > 0:
                returnCode = 1
    except:
        message = getExceptionInfo()
        if message.startswith( "Exception is cought. 0" ):
            returnCode = 0
        else:
            print >> sys.stderr, message
            returnCode = 3
    sys.exit( returnCode )

