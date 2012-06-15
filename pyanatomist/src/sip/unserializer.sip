

namespace anatomist
{

  class Unserializer
  {
%TypeHeaderCode
#include <anatomist/processor/unserializer.h>
%End

  public:
    Unserializer();
    virtual ~Unserializer ();

    void registerPointer( void* ptr, int id, const std::string & type );

    void registerPointer( QWidget* ptr, int id );
%MethodCode
    sipCpp->registerPointer( (void *) a0, a1, "Widget" );
%End

    void registerPointer( anatomist::AObject* ptr, int id );
%MethodCode
    sipCpp->registerPointer( (void *) a0, a1, "AObject" );
%End

    void registerPointer( anatomist::AWindow* ptr, int id );
%MethodCode
    sipCpp->registerPointer( (void *) a0, a1, "AWindow" );
%End

    int makeID(void *, const std::string &="");

    int makeID(long, const std::string &="");
%MethodCode
    sipCpp->makeID( (void *) a0, *a1 );
%End

    int makeID(anatomist::AObject *);
%MethodCode
    sipCpp->makeID( a0, "AObject" );
%End

    int makeID(anatomist::AWindow *);
%MethodCode
    sipCpp->makeID( a0, "AWindow" );
%End

    int makeID(anatomist::Referential *);
%MethodCode
    sipCpp->makeID( a0, "Referential" );
%End

    int makeID(anatomist::Transformation *);
%MethodCode
    sipCpp->makeID( a0, "Transformation" );
%End

    int makeID(QWidget *);
%MethodCode
    sipCpp->makeID( a0, "Widget" );
%End


    int id(void *, const std::string & = "") const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, *a1);
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End

    int id( long, const std::string & = "") const;
%MethodCode
  try
  {
    sipRes = sipCpp->id((void *)a0, *a1);
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End


    int id( anatomist::AObject * ) const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, "AObject");
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End


    int id( anatomist::AWindow * ) const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, "AWindow");
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End


    int id( anatomist::Referential * ) const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, "Referential");
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End

    int id( anatomist::Transformation * ) const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, "Transformation");
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End

    int id( QWidget * ) const;
%MethodCode
  try
  {
    sipRes = sipCpp->id(a0, "Widget");
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End


};
};

