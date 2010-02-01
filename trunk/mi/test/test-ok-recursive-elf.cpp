//
// File:   test-ok-recursive-elf.cpp
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

pthread_mutex_t     m1 = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;
pthread_mutex_t     m2 = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;


void *  thread0( void * )
{
    pthread_mutex_lock( &m1 );
    pthread_mutex_lock( &m1 );
    pthread_mutex_unlock( &m1 );
    pthread_mutex_unlock( &m1 );

    return 0;
}

void *  thread1( void * )
{
    usleep( 500 );
    pthread_mutex_lock( &m2 );
    pthread_mutex_lock( &m2 );
    pthread_mutex_unlock( &m2 );
    pthread_mutex_unlock( &m2 );

    return 0;
}


int main( void )
{
    cout << "Test (ok, elf, recursive) t0: m1.lock -> m1.lock ->  m1.unlock -> m1.unlock" << endl
         << "                          t1: m2.lock -> m2.lock ->  m2.unlock -> m2.unlock" << endl;

    pthread_t       t0;
    pthread_t       t1;

    pthread_create( &t0, 0, thread0, 0 );
    pthread_create( &t1, 0, thread1, 0 );
    pthread_join( t0, 0 );
    pthread_join( t1, 0 );

    return 0;
}



