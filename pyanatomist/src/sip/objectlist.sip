namespace anatomist
{

class ObjectList : anatomist::MObject
{
%TypeHeaderCode
#include <anatomist/object/Object.h>
#include <anatomist/mobject/ObjectList.h>
#include <pyaims/vector/vector.h>
%End

%ConvertToSubClassCode
  if (dynamic_cast<anatomist::ObjectList *>(sipCpp))
    sipType = sipType_anatomist_ObjectList;
  else
    sipType = 0;
%End

public:
  ObjectList ();
  virtual ~ObjectList ();
  virtual size_t size() const;
  virtual anatomist::AIterator begin();
  virtual anatomist::AIterator end();
  virtual void insert (anatomist::AObject * );
  int type() const;
};


class ObjectVector : anatomist::MObject
{
%TypeHeaderCode
#include <anatomist/mobject/objectVector.h>
#include <pyaims/vector/vector.h>
%End

public:
  ObjectVector();
  virtual ~ObjectVector();

  virtual size_t size() const;
  virtual anatomist::AIterator begin();
  virtual anatomist::AIterator end();
  virtual void insert( anatomist::AObject * );
  virtual void insert( anatomist::AObject *, int pos );
  void insert( const weak_shared_ptr_AObject &, int pos = -1 );
  void insert( const rc_ptr_AObject &, int pos = -1 );
  virtual anatomist::AIterator find( const anatomist::AObject * ) const;
  anatomist::AIterator find( const weak_shared_ptr_AObject & ) const;
  anatomist::AIterator find( const rc_ptr_AObject & ) const;
  virtual void erase( anatomist::AIterator & );
  virtual bool CanRemove( anatomist::AObject *obj );
  int type() const;
};

};

