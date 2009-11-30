//
// File:   test-lib-fun-ok.cpp
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


int f( void )
{
    pthread_mutex_t     m1 = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t     m2 = PTHREAD_MUTEX_INITIALIZER;

    pthread_mutex_lock( &m1 );
    pthread_mutex_lock( &m2 );

    pthread_mutex_unlock( &m2 );
    pthread_mutex_unlock( &m1 );

    return 0;
}

