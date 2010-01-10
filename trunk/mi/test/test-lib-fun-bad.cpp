//
// File:   test-lib-fun-bad.cpp
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

pthread_mutex_t     m1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t     m2 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t     m3 = PTHREAD_MUTEX_INITIALIZER;


void *  thread0( void * )
{
    pthread_mutex_lock( &m1 );
    pthread_mutex_lock( &m2 );
    pthread_mutex_lock( &m3 );
    pthread_mutex_unlock( &m3 );
    pthread_mutex_unlock( &m2 );
    pthread_mutex_unlock( &m1 );

    return 0;
}

void *  thread1( void * )
{
    usleep( 500 );
    pthread_mutex_lock( &m3 );
    pthread_mutex_lock( &m2 );
    pthread_mutex_lock( &m1 );
    pthread_mutex_unlock( &m1 );
    pthread_mutex_unlock( &m2 );
    pthread_mutex_unlock( &m3 );

    return 0;
}



int  f0( void )
{
    pthread_t       t0;

    pthread_create( &t0, 0, thread0, 0 );
    return 0;
}



int  f1( void )
{
    pthread_t       t1;

    pthread_create( &t1, 0, thread1, 0 );
    return 0;
}

