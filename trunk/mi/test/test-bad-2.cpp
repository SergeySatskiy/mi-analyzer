//
// File:   test-bad-2.cpp
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

#include <iostream>
using namespace std;

int main( void )
{
    cout << "Test (bad) m1.lock -> m2.lock -> m1.unlock -> m2.unlock" << endl;

    pthread_mutex_t     m1 = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t     m2 = PTHREAD_MUTEX_INITIALIZER;

    pthread_mutex_lock( &m1 );
    pthread_mutex_lock( &m2 );
    pthread_mutex_unlock( &m1 );
    pthread_mutex_unlock( &m2 );

    return 0;
}

