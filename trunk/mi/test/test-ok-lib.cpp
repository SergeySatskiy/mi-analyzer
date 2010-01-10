//
// File:   test-ok-lib.cpp
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

#include <iostream>
using namespace std;


int f0( void );
int f1( void );

int main( int argc, char ** argv )
{
    cout << "Test (ok, so) t0: m1.lock -> m2.lock -> m3.lock -> m3.unlock -> m2.unlock -> m1.unlock" << endl
         << "              t1: m1.lock -> m2.lock -> m3.lock -> m3.unlock -> m2.unlock -> m1.unlock" << endl;
    f0();
    f1();
    usleep( 1000 );
    return 0;
}

