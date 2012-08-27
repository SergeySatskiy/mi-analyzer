//
// File:   mi.cpp
//
// Author: Sergey Satskiy, copyright (c) 2009 - 2012
//
// Date:   Aug 27, 2012
//
// $Id$
//
// Permission to copy, use, modify, sell and distribute this software
// is granted provided this copyright notice appears in all copies.
// This software is provided "as is" without express or implied
// warranty, and with no claim as to its suitability for any purpose.
//


#ifndef MITIME__HPP
#define MITIME__HPP

# include <sys/time.h>


class PreciseTime : public timespec
{
    private:
        enum
        {
            MSecsPerSecond = 1000,
            USecsPerMSec   = 1000,
            NSecsPerUSec   = 1000,
            USecsPerSecond = USecsPerMSec * MSecsPerSecond,
            NSecsPerMSec   = NSecsPerUSec * USecsPerMSec,
            NSecsPerSecond = NSecsPerMSec * MSecsPerSecond
        };

    public:
        static PreciseTime  Current( void )
        {
            PreciseTime    result;
            clock_gettime( CLOCK_REALTIME, &result );
            return result;
        }

        PreciseTime( void )
        {
            tv_sec = 0;
            tv_nsec = 0;
        }

        PreciseTime( time_t  sec )
        {
            tv_sec = sec;
            tv_nsec = 0;
        }

        PreciseTime( double  time )
        {
            tv_sec = int(time);
            tv_nsec = int( (time - tv_sec) * NSecsPerSecond );
        }

        time_t  Seconds( void ) const
        { return tv_sec; }

        unsigned long  NanoSeconds( void ) const
        { return tv_nsec; }

        operator double() () const
        {
            return (double)tv_sec + (double)tv_nsec / NSecsPerSecond;
        }

        int  Compare( const PreciseTime &  t ) const
        {
            if ( tv_sec < t.tv_sec )        return -1;
            else if ( tv_sec > t.tv_sec )   return 1;
            else if ( tv_nsec < t.tv_nsec ) return -1;
            else if ( tv_nsec > t.tv_nsec ) return 1;
            return 0;
        }

        PreciseTime &  operator += ( const PreciseTime &  t )
        {
            tv_sec += t.tv_sec;
            tv_nsec += t.tv_nsec;
            if ( tv_nsec >= NSecsPerSecond )
            {
                ++tv_sec;
                tv_nsec -= NSecsPerSecond;
            }
            return *this;
        }

        PreciseTime &  operator -= ( const PreciseTime &  t )
        {
            tv_sec -= t.tv_sec;
            if ( tv_nsec >= t.tv_nsec )
            {
                tv_nsec -= t.tv_nsec;
            }
            else
            {
                --tv_sec;
                tv_nsec += NSecsPerSecond;
                tv_nsec -= t.tv_nsec;
            }
            return *this;
        }

        bool  operator > ( const PreciseTime &  t ) const
        { return Compare( t ) > 0; }

        bool  operator >= ( const PreciseTime &  t ) const
        { return Compare( t ) >= 0; }

        bool  operator < ( const PreciseTime &  t ) const
        { return Compare( t ) < 0; }

        bool  operator <= ( const PreciseTime &  t ) const
        { return Compare( t ) <= 0; }
};

inline
PreciseTime operator + ( const PreciseTime &  lhs,
                         const PreciseTime &  rhs )
{
    PreciseTime      result( lhs );
    return result += rhs;
}

inline
PreciseTime operator - ( const PreciseTime &  lhs,
                         const PreciseTime &  rhs )
{
    PreciseTime      result( lhs );
    return result -= rhs;
}

inline
bool operator == ( const PreciseTime &  lhs,
                   const PreciseTime &  rhs )
{
    // Faster, than to use <
    return lhs.tv_sec  == rhs.tv_sec &&
           lhs.tv_nsec == rhs.tv_nsec;
}

inline
bool operator != ( const PreciseTime &  lhs,
                   const PreciseTime &  rhs )
{
    return !(lhs == rhs);
}


#endif /* MITIME__HPP */

