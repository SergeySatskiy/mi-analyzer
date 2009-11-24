#!/bin/env python
#
# File:   mi.py
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
mi - mutex instrumentation
"""

import sys, os, os.path, tempfile
from traceback import format_tb
from subprocess import Popen, PIPE

__version__ = "0.0.1"



def miMain():
    """ The mi driver """

    if len( sys.argv ) < 2:
        printUsage()
        return 1

    verbose = False

    index = 1
    while index < len( sys.argv ):
        if sys.argv[ index ] == "--":
            index = index + 1
            break
        if not sys.argv[ index ].startswith( "-" ):
            break
        if sys.argv[ index ] in [ "-h", "--help" ]:
            printUsage()
            return 0
        if sys.argv[ index ] in [ "-v", "--verbose" ]:
            verbose = True
            index = index + 1
            continue
        print "Not recognised option key: " + sys.argv[ index ]
        print "Abort. Type: " + sys.argv[0] + " --help for usage."
        return 1

    # Check that there is still a name of the executable to start
    if index >= len( sys.argv ):
        print "Program to analyse is not specified."
        print "Abort. Type: " + sys.argv[0] + " --help for usage."
        return 1

    # Check the substitution library path
    if verbose:
        print "Looking for the libmi.so..."

    base = os.path.abspath( sys.argv[0] )
    while os.path.islink( base ):
        base = os.path.abspath( base + os.readlink( base ) )
    base = os.path.dirname( base )

    libmiPath = base + "/libmi.so"
    if not os.path.exists( libmiPath ):
        print "libmi.so is not found. It must be located at " + \
              libmiPath + ". Abort."
        return 2
    if verbose:
        print "Found at " + libmiPath

    # Check the executable presence
    if verbose:
        print "Checking path to the program to test..."

    elfPath = os.path.abspath( sys.argv[ index ] )
    if not os.path.exists( elfPath ):
        print "The program " + sys.argv[ index ] + " is not found. Abort."
        return 2

    if verbose:
        print "Found at " + elfPath
    index = index + 1   # points to the first program argument if so

    # Check for the log file name
    logFilePath = os.environ.get( 'MI_LOGFILE', '' )
    if logFilePath == "":
        logFilePath = os.getcwd() + "/mi.log"

    # Check the libpthread
    libpthreadPath = os.environ.get( 'MI_LIBPTHREAD', '' )
    if libpthreadPath != "":
        if not os.path.exists( libpthreadPath ):
            print "The MI_LIBPTHREAD variable is set to " + libpthreadPath + \
                  " however this file is not found. Abort."
            return 2
        if verbose:
            print "The MI_LIBPTHREAD variable is set. " \
                  "Use it as path to libpthread.so"
    else:
        # The variable is not set i.e. the libpthread.so path must be guessed
        # by the ldd output
        if verbose:
            print "The MI_LIBPTHREAD is not set. Search for it in the given " \
                  "program dynamically linked libraries..."
        libpthreadPath = getLibpthreadPath( elfPath, verbose )
        if libpthreadPath == "":
            print "The " + elfPath + " is not linked with libpthread. Abort."
            return 2
        if verbose:
            print "Found at " + libpthreadPath


    # Form the executable command line
    cmdLine = 'LD_PRELOAD="' + libmiPath + '" '
    cmdLine += 'MI_LIBPTHREAD="' + libpthreadPath + '" '
    cmdLine += 'MI_LOGFILE="' + logFilePath + '" '
    if ' ' in elfPath:
        cmdLine += '"' + elfPath + '" '
    else:
        cmdLine += elfPath + ' '

    while index < len( sys.argv ):
        if ' ' in sys.argv[index]:
            cmdLine += '"' + sys.argv[index] + '" '
        else:
            cmdLine += sys.argv[index] + ' '
        index += 1

    if verbose:
        print "Command line: " + cmdLine

    retCode = os.system( cmdLine )
    if verbose:
        print "Exit code: " + str( retCode )

    return 0


def getLibpthreadPath( elfPath, verbose ):
    """ provides absolute path to libpthread via ldd output """

    try:
        if verbose:
            print "Checking for ldd..."
        safeRun( [ 'which', 'ldd' ] )
    except:
        raise Exception( "ldd is not available in PATH" )

    return findLibpthread( elfPath )


def findLibpthread( elfPath ):
    """ analyses ldd output to get libpthread path """

    command = [ "ldd", elfPath ]
    for line in safeRun( command ).split( '\n' ):
        line = line.strip()
        if line == "":
            continue

        parts = line.split()
        if parts[0].strip().startswith( "libpthread.so" ):
            return parts[2].strip()

        if parts[0].strip().startswith( "linux-gate.so" ) or \
           parts[0].strip().startswith( "linux-vdso.so" ):
            continue

        if parts[0].strip().startswith( "statically" ):
            continue

        if parts[0].strip().startswith( "/" ):
            path = findLibpthread( parts[0].strip() )
            if path != "":
                return path

        if len( parts ) == 4 and parts[2] == "not" and parts[3] == "found":
            raise Exception( "One of the libraries in the program to " \
                             "analyse is not found: " + line )

        path = findLibpthread( parts[2].strip() )
        if path != "":
            return path

    return ""


def printUsage():
    """ prints how to use mi """

    print "mi version " + __version__ + \
          """
mi is a mutex instrumenting package. It provides the following:
- analysis of mutex locking sequenses in all the threads and
  detection of [potential] dead locks
- statistics of success and failures
- time spent on mutex lock operations

mi can be controlled by the following environment variables:
MI_LIBPTHREAD - path to the system pthread library. If the variable is not set
                then mi will look for the path to the library using ldd on the
                given program to be analysed
MI_LOGFILE    - path to the log file where the collected information is stored
MI_OPTIONS    - accepted values:
                stack - accompany each operation with a stack trace (slow)

Usage:
mi [me option keys] [--] <program to analyse> [program option keys]
mi option keys:
--help, -h      prints this message
--verbose, -v   be verbose
--              explicitly separates mi option keys from the program
                to be analysed
          """
    return


def safeRun( commandArgs ):
    """ Runs the given command and reads the output """

    errTmp = tempfile.mkstemp()
    errStream = os.fdopen( errTmp[0] )
    process = Popen( commandArgs, stdin = PIPE,
                     stdout = PIPE, stderr = errStream )
    process.stdin.close()
    processStdout = process.stdout.read()
    process.stdout.close()
    errStream.seek( 0 )
    err = errStream.read()
    errStream.close()
    os.unlink( errTmp[1] )
    process.wait()
    if process.returncode != 0:
        raise Exception( "Error in '%s' invocation: %s" % \
                         (commandArgs[0], err) )
    return processStdout


def getExceptionInfo():
    """
    The function formats the exception and returns the string which
    could be then printed or logged
    """

    excType, value, tback = sys.exc_info()
    msg = str( value )

    if len( msg ) == 0:
        msg = "There is no message associated with the exception."
    if msg.startswith( '(' ) and msg.endswith( ')' ):
        msg = msg[1:-1]

    try:
        tbInfo = format_tb( tback )
        tracebackInfoMsg = "Traceback information:\n" + "".join( tbInfo )
    except:
        tracebackInfoMsg = "No traceback information available"

    return "Exception is cought. " + msg + "\n" + tracebackInfoMsg




# The script execution entry point
if __name__ == "__main__":
    returnCode = 0
    try:
        returnCode = miMain()
    except:
        message = getExceptionInfo()
        if message.startswith( "Exception is cought. 0" ):
            returnCode = 0
        else:
            print >> sys.stderr, message
            returnCode = 107
    sys.exit( returnCode )

