//
// File:   test-lib-bad.cpp
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


int f( void );

int main( int argc, char ** argv )
{
    cout << "Test (bad - locks are in a shared library)" << endl;
    return f();
}

