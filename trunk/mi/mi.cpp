//
// File:   mi.cpp
//
// Author: Sergey Satskiy, copyright (c) 2009
//
// Date:   July 22, 2009
//
// $Id$
//
// Permission to copy, use, modify, sell and distribute this software
// is granted provided this copyright notice appears in all copies.
// This software is provided "as is" without express or implied
// warranty, and with no claim as to its suitability for any purpose.
//


#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdarg.h>
#include <string.h>
#include <execinfo.h>
#include <cxxabi.h>

#include <vector>
#include <algorithm>
using namespace std;


#include <pthread.h>

#include "mitime.hpp"

typedef int (*mutex_function)( pthread_mutex_t * );


static const char *    defaultLibpthreadPath = "/lib/libpthread.so.0";
static const char *    defaultLogfile = "mi.log";


static pthread_mutex_t     outputLock = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t     inLock = PTHREAD_MUTEX_INITIALIZER;



class PthreadWrapper
{
    private:
        void *              handle;             // libpthread.so handle
        FILE *              outputFile;         // log file
        mutex_function      lockFunction;       // pthread_mutex_lock()
        mutex_function      unlockFunction;     // pthread_mutex_unlock()
        mutex_function      trylockFunction;    // pthread_mutex_trylock()
        bool                putStackTrace;      // log the stack trace?
        vector<pthread_t>   inProcess;          // The backtrace() locks a
                                                // mutex internally so keep a
                                                // track of what is processed

    public:
        // Checks if the process is in pthread_mutex_XXXlock() call
        bool  isProcessed( void ) const
        {
            bool found;
            this->lockFunction( &inLock );
            found = inProcess.end() != find( inProcess.begin(), inProcess.end(),
                                             pthread_self() );
            this->unlockFunction( &inLock );
            return found;
        }

        // Registers the process which is in pthread_mutex_XXXlock() call
        void  registerThread( void )
        {
            this->lockFunction( &inLock );
            inProcess.push_back( pthread_self() );
            this->unlockFunction( &inLock );
        }

        // Unregisters the process from the pthread_mutex_XXXlock() call
        void  unregisterThread( void )
        {
            this->lockFunction( &inLock );
            vector<pthread_t>::iterator     candidate( find( inProcess.begin(),
                                                             inProcess.end(),
                                                             pthread_self() ) );
            if ( candidate != inProcess.end() ) inProcess.erase( candidate );
            this->unlockFunction( &inLock );
        }

        PthreadWrapper() :
            handle( 0 ), outputFile( 0 ), putStackTrace( false )
        {
            char *          libpthreadPath( getenv( "MI_LIBPTHREAD" ) );
            char *          logfilePath( getenv( "MI_LOGFILE" ) );
            char *          options( getenv( "MI_OPTIONS" ) );
            char *          elf( getenv( "MI_ELF" ) );
            const char *    err;

            if ( libpthreadPath == 0 )
                handle = dlopen( defaultLibpthreadPath, RTLD_LAZY );
            else
                handle = dlopen( libpthreadPath, RTLD_LAZY );

            if ( !handle )
            {
                fprintf( stderr,
                         "Cannot get libpthread.so handle. dlopen: %s\n",
                         dlerror() );
                exit( 1 );
            }

            dlerror();
            lockFunction = (mutex_function)dlsym( handle,
                                                  "pthread_mutex_lock" );
            err = dlerror();
            if ( err )
            {
                fclose( outputFile );
                dlclose( handle );
                fprintf( stderr,
                         "Cannot get pthread_mutex_lock() pointer. dlsym: %s\n",
                         err );
                exit( 1 );
            }

            unlockFunction = (mutex_function)dlsym( handle,
                                                    "pthread_mutex_unlock" );
            err = dlerror();
            if ( err )
            {
                fclose( outputFile );
                dlclose( handle );
                fprintf( stderr,
                         "Cannot get pthread_mutex_unlock() pointer. dlsym: %s\n",
                         err );
                exit( 1 );
            }

            trylockFunction = (mutex_function)dlsym( handle,
                                                     "pthread_mutex_trylock" );
            err = dlerror();
            if ( err )
            {
                fclose( outputFile );
                dlclose( handle );
                fprintf( stderr,
                         "Cannot get pthread_mutex_trylock() pointer. dlsym: %s\n",
                         err );
                exit( 1 );
            }

            if ( logfilePath == 0 || strlen( logfilePath ) == 0 )
                outputFile = fopen( defaultLogfile, "w" );
            else
                outputFile = fopen( logfilePath, "w" );
            if ( !outputFile )
            {
                dlclose( handle );
                fprintf( stderr, "Cannot open mi.log" );
                exit( 1 );
            }

            if ( elf == 0 )
                this->write( "Env: application: unknown\n" );
            else
                this->write( "Env: application: %s\n", elf );

            if ( logfilePath == 0 )
                this->write( "Env: log file: %s\n", defaultLogfile );
            else
                this->write( "Env: log file: %s\n", logfilePath );

            if ( libpthreadPath == 0 )
                this->write( "Env: libpthread.so path: %s\n",
                             defaultLibpthreadPath );
            else
                this->write( "Env: libpthread.so path: %s\n",
                             libpthreadPath );

            if ( options != 0 && strlen( options ) != 0 )
            {
                if ( strcmp( options, "stack" ) == 0 )
                {
                    putStackTrace = true;
                }
                else
                {
                    fprintf( stderr,
                             "Unsupported option '%s' in the MI_OPTIONS "
                             "environment variable. Supported values: 'stack'.",
                             options );
                    exit( 1 );
                }
            }

            if ( putStackTrace )
                this->write( "Env: print stack trace\n" );
            else
                this->write( "Env: do not print stack trace\n" );
        }

        ~PthreadWrapper()
        {
            if ( outputFile ) fclose( outputFile );
            if ( handle )     dlclose( handle );
        }

        int write( const char * format, ... ) const
        {
            int     ret;

            va_list l;
            va_start( l, format );
            ret = vfprintf( outputFile, format, l );
            va_end( l );

            return ret;
        }

        // Based on: http://idlebox.net/2008/0901-stacktrace-demangled/
        void saveStack( void )
        {
            if ( !putStackTrace )   return;

            this->registerThread();

            // storage array for stack trace address data
            void *      addrlist[1024];

            // retrieve current stack addresses
            // locks a mutex internally!
            int         addrlen = backtrace( addrlist, 1024 );
            if ( addrlen == 0 )
            {
                this->write( "Bt:  <empty, possibly corrupt>\n" );
                return;
            }

            // resolve addresses into strings containing "filename(function+address)",
            // this array must be free()-ed
            char **     symbollist = backtrace_symbols( addrlist, addrlen );

            // allocate string which will be filled with the demangled function name
            size_t      funcnamesize = 256;
            char *      funcname = (char*) malloc( funcnamesize );

            // iterate over the returned symbol lines. skip the first, it is the
            // address of this function. skip the second, it is the address of
            // the pthread_mutex_zzz(...) from libmi.so
            for ( int i = 2; i < addrlen; i++ )
            {
                char *  begin_name = 0;
                char *  begin_offset = 0;
                char *  end_offset = 0;

                // find parentheses and +address offset surrounding the mangled name:
                // ./module(function+0x15c) [0x8048a6d]
                for ( char *  p = symbollist[i]; *p; ++p )
                {
                    if ( *p == '(' )    begin_name = p;
                    else if (*p == '+') begin_offset = p;
                    else if (*p == ')' && begin_offset)
                    {
                        end_offset = p;
                        break;
                    }
                }

                if ( begin_name && begin_offset && end_offset && (begin_name < begin_offset) )
                {
                    *begin_name++ = '\0';
                    *begin_offset++ = '\0';
                    *end_offset = '\0';

                    // mangled name is now in [begin_name, begin_offset) and caller
                    // offset in [begin_offset, end_offset). now apply __cxa_demangle():

                    int        status;
                    char *     ret = abi::__cxa_demangle( begin_name,
                                                          funcname, &funcnamesize, &status);
                    if ( status == 0 )
                    {
                        funcname = ret; // use possibly realloc()-ed string
                        this->write( "Bt:  %s : %s+%s\n",
                                     symbollist[i], funcname, begin_offset );
                    }
                    else
                    {
                        // demangling failed. Output function name as a C function
                        // with no arguments.
                        this->write( "Bt:  %s : %s()+%s\n",
                                     symbollist[i], begin_name, begin_offset );
                    }
                }
                else
                {
                    // couldn't parse the line? print the whole line.
                    this->write( "Bt:  %s\n", symbollist[i] );
                }
            }

            free( funcname );
            free( symbollist );
            this->unregisterThread();
        }

        mutex_function  getLockFunction( void )    const { return lockFunction; }
        mutex_function  getUnlockFunction( void )  const { return unlockFunction; }
        mutex_function  getTrylockFunction( void ) const { return trylockFunction; }
};



static PthreadWrapper   pw;

extern "C"
{
    // Instrumented functions

    int pthread_mutex_lock( pthread_mutex_t *  m )
    {
        if ( pw.isProcessed() )
        {
            return pw.getLockFunction()( m );
        }

        PreciseTime     before( PreciseTime::Current() );
        int             retVal( pw.getLockFunction()( m ) );
        PreciseTime     after( PreciseTime::Current() );

        pw.getLockFunction()( &outputLock );
        pw.write( "Op: lock Object: %p Thread: %lu RetCode: %d Clocks: %f\n",
                  m, pthread_self(), retVal, (double)( after - before ) );
        pw.saveStack();
        pw.getUnlockFunction()( &outputLock );

        return retVal;
    }

    int pthread_mutex_unlock( pthread_mutex_t *  m )
    {
        if ( pw.isProcessed() )
        {
            return pw.getUnlockFunction()( m );
        }

        PreciseTime     before( PreciseTime::Current() );
        int             retVal( pw.getUnlockFunction()( m ) );
        PreciseTime     after( PreciseTime::Current() );

        pw.getLockFunction()( &outputLock );
        pw.write( "Op: unlock Object: %p Thread: %lu RetCode: %d Clocks: %f\n",
                  m, pthread_self(), retVal, (double)( after - before ) );
        pw.saveStack();
        pw.getUnlockFunction()( &outputLock );

        return retVal;
    }

    int pthread_mutex_trylock( pthread_mutex_t *  m )
    {
        if ( pw.isProcessed() )
        {
            pw.getTrylockFunction()( m );
        }

        PreciseTime     before( PreciseTime::Current() );
        int             retVal( pw.getTrylockFunction()( m ) );
        PreciseTime     after( PreciseTime::Current() );

        pw.getLockFunction()( &outputLock );
        pw.write( "Op: trylock Object: %p Thread: %lu RetCode: %d Clocks: %f\n",
                  m, pthread_self(), retVal, (double)( after - before ) );
        pw.saveStack();
        pw.getUnlockFunction()( &outputLock );

        return retVal;
    }
}

