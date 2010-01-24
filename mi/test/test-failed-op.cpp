//
// File:   test-failed-op.cpp
//
// Author: Sergey Satskiy, copyright (c) 2009
//
// Date:   November 24, 2009
//
// $Id$
//
// Permission to copy, use, modify, sell and distribute this software
// is granted provided this copyright notice appears in all copies.
// This software is provided "as is" without express or implied
// warranty, and with no claim as to its suitability for any purpose.
//

#include <pthread.h>
#include <unistd.h>

#include <iostream>
using namespace std;

pthread_mutex_t     m1 = PTHREAD_MUTEX_INITIALIZER;


void *  thread0( void * )
{
    pthread_mutex_lock( &m1 );
    usleep( 500 );
    pthread_mutex_unlock( &m1 );
    return 0;
}

void *  thread1( void * )
{
    usleep( 100 );
    if ( pthread_mutex_trylock( &m1 ) == 0 )
        cout << "Error test execution" << endl;

    return 0;
}


int main( void )
{
    cout << "Test (failed operation, elf) t0: m1.lock -> m1.unlock" << endl
         << "                             t1: m1.trylock while it is locked" << endl;

    pthread_t       t0;
    pthread_t       t1;

    pthread_create( &t0, 0, thread0, 0 );
    pthread_create( &t1, 0, thread1, 0 );
    pthread_join( t0, 0 );
    pthread_join( t1, 0 );

    return 0;
}


