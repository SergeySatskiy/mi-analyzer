//
// File:   test-ok-condition-vars-elf.cpp
//
// Author: Sergey Satskiy, copyright (c) 2009
//
// Date:   January 24, 2010
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

pthread_mutex_t condition_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  condition_cond  = PTHREAD_COND_INITIALIZER;


void *  thread0( void * )
{
    pthread_mutex_lock( &condition_mutex );
    pthread_cond_wait( &condition_cond, &condition_mutex );
    pthread_mutex_unlock( &condition_mutex );
    return 0;
}

void *  thread1( void * )
{
    usleep( 250 );
    pthread_mutex_lock( &condition_mutex );
    pthread_cond_signal( &condition_cond );
    pthread_mutex_unlock( &condition_mutex );
    return 0;
}

int main( void )
{
    cout << "Test (ok, elf, condition variable) t0: m.lock -> c.wait -> m.unlock" << endl
         << "                                   t1: m.lock -> c.signal -> m.unlock" << endl;

    pthread_t       t0;
    pthread_t       t1;

    pthread_create( &t0, NULL, &thread0, NULL);
    pthread_create( &t1, NULL, &thread1, NULL);
    pthread_join( t0, NULL);
    pthread_join( t1, NULL);

    return 0;
}


