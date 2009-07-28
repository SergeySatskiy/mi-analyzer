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

