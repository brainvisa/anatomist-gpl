namespace anatomist
{

class AIterator
{
%TypeHeaderCode
#include <anatomist/object/Object.h>
#include <anatomist/mobject/MObject.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipanatomistAObject.h"
#endif
#include <pyanatomist/aobject.h>
%End

public:
    AIterator();

    AIterator( const anatomist::AIterator & );
    ~AIterator();
    bool operator == ( const anatomist::AIterator & ) const;
    bool operator != ( const anatomist::AIterator & ) const;

    anatomist::AObject * next();
%MethodCode
    sipRes = **sipCpp;
    if( !sipRes )
    {
      PyErr_SetString( PyExc_StopIteration, "iterator outside bounds" );
      sipIsErr = 1;
    }
    else
      ++(*sipCpp);
%End

// This method should be commented out as long as this is not a proper iterator
// in the Python sense. See pyanatomist/python/anatomist/cpp/mobject.py.
//    anatomist::AIterator* __iter__() /Factory/;
// %MethodCode
//    sipRes = new anatomist::AIterator( *sipCpp );
// %End
};

class MObject : anatomist::AObject /Abstract/
{
%TypeHeaderCode
#include <anatomist/object/Object.h>
#include <anatomist/mobject/MObject.h>
#include <pyaims/vector/vector.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipanatomistAIterator.h"
#include "sipanatomistsipanatomistAObject.h"
#endif
#include <pyanatomist/aobject.h>
%End

public:
    MObject();
    virtual ~MObject();

    virtual size_t size() const = 0;
    virtual void 	insert (anatomist::AObject *) = 0;
    virtual anatomist::AIterator begin() = 0;
    virtual anatomist::AIterator end() = 0;
    void eraseObject( anatomist::AObject *);

    virtual float MinT() const;
    virtual float MaxT() const;

    virtual vector_FLOAT voxelSize() const;
    virtual bool boundingBox( vector_FLOAT &, vector_FLOAT & ) const;
    virtual anatomist::AObject* objectAt( const vector_FLOAT &, float = 0 );
    virtual bool Is2DObject();
    virtual bool Is3DObject();
    virtual bool isTransparent() const;
    virtual void update( const anatomist::Observable*, void* );
    virtual bool CanRemove( anatomist::AObject * );
    virtual void setContentChanged() const;
    bool hasContentChanged() const;
    virtual void clearHasChangedFlags() const;
    virtual void setPalette( const anatomist::AObjectPalette & );
    virtual anatomist::GLComponent* glAPI();
    virtual list_AObjectPtr generativeChildren() const;
    virtual list_AObjectPtr renderedSubObjects(
      const anatomist::ViewState & ) const;

    anatomist::AObject * __getitem__(int);
%MethodCode
    if ( a0 < (int) sipCpp->size())
    {
      anatomist::AIterator current = sipCpp->begin();

      for(int index=0; (index < a0); index++)
        current++;

      sipRes = *current;
    }
    else
    {
      sipRes = 0;
      sipIsErr = 1;
      PyErr_SetString( PyExc_IndexError, "index out of range" );
    }
%End

// At the moment __iter__ is patched in plain Python (see
// pyanatomist/python/anatomist/cpp/mobject.py), because AIterator is not a
// proper iterator in the Python sense.
//
//     anatomist::AIterator *__iter__() /Factory/;
// %MethodCode
//     sipRes = new anatomist::AIterator( sipCpp->begin() );
// %End
};

};

