
namespace anatomist
{

  class Observable : carto::SharedObject
  {
%TypeHeaderCode
#include <anatomist/observer/Observer.h>
#include <anatomist/observer/Observable.h>
#include <anatomist/surface/textobject.h>
#include <anatomist/surface/transformedobject.h>
#include <anatomist/surface/texture.h>
#include <anatomist/application/globalConfig.h>
%End

%TypeCode
#include <anatomist/graph/Graph.h>
#include <anatomist/graph/GraphObject.h>
#include <anatomist/object/clippedobject.h>
#include <anatomist/window3D/window3D.h>
%End

%ConvertToSubClassCode

  // std::cout << "Observable ConvertToSubClassCode: " << sipCpp << " / " << typeid( *sipCpp ).name() << std::endl;
  sipType = 0;
  if( dynamic_cast<anatomist::CommandContext *>( sipCpp ) )
  {
    *sipCppRet = dynamic_cast<anatomist::CommandContext *>( sipCpp );
    sipType = sipType_anatomist_CommandContext;
  }
  else
  {
    if( dynamic_cast<anatomist::Observable *>( sipCpp ) )
    {
      sipType = sipType_anatomist_Observable;
      *sipCppRet = dynamic_cast<anatomist::Observable *>( sipCpp );
      if( dynamic_cast<anatomist::AObject *>( sipCpp ) )
      {
        if (dynamic_cast<anatomist::ASurface_3 *>(sipCpp))
        sipType = sipType_anatomist_ASurface_3;
        else if (dynamic_cast<anatomist::ASurface_2 *>(sipCpp))
        sipType = sipType_anatomist_ASurface_2;
        else if (dynamic_cast<anatomist::ATexture *>(sipCpp))
        sipType = sipType_anatomist_ATexture;
        else if (dynamic_cast<anatomist::MObject *>(sipCpp))
        {
        if (dynamic_cast<anatomist::AGraph *>(sipCpp))
          sipType = sipType_anatomist_AGraph;
        else if (dynamic_cast<anatomist::AGraphObject *>(sipCpp))
          sipType = sipType_anatomist_AGraphObject;
        else if (dynamic_cast<anatomist::ClippedObject *>(sipCpp))
          sipType = sipType_anatomist_ClippedObject;
        else if (dynamic_cast<anatomist::ObjectList *>(sipCpp))
          sipType = sipType_anatomist_ObjectList;
        else
          sipType = sipType_anatomist_MObject;
        }
        else if (dynamic_cast<anatomist::SliceableObject *>(sipCpp))
        sipType = sipType_anatomist_SliceableObject;
        else if (dynamic_cast<anatomist::TextObject *>(sipCpp))
        sipType = sipType_anatomist_TextObject;
        else if (dynamic_cast<anatomist::TransformedObject *>(sipCpp))
        sipType = sipType_anatomist_TransformedObject;
        else
          sipType = sipType_anatomist_AObject;
      }
      else if( dynamic_cast<anatomist::AWindow *>( sipCpp ) )
      {
        // std::cout << "  Observable - is a AWindow: " << sipCppRet << std::endl;
        if( dynamic_cast<AWindow3D *>( sipCpp ) )
        {
          *sipCppRet = dynamic_cast<AWindow3D *>( sipCpp );
          sipType = sipType_AWindow3D;
        }
        else if( dynamic_cast<ControlledWindow *>( sipCpp ) )
        {
          *sipCppRet = dynamic_cast<ControlledWindow *>( sipCpp );
          sipType = sipType_ControlledWindow;
        }
        else if( dynamic_cast<QAWindow *>( sipCpp ) )
        {
          *sipCppRet = dynamic_cast<QAWindow *>( sipCpp );
          sipType = sipType_QAWindow;
        }
        else
        {
          *sipCppRet = dynamic_cast<anatomist::AWindow *>( sipCpp );
          sipType = sipType_anatomist_AWindow;
        }
      }
    }
    else if( dynamic_cast<anatomist::GlobalConfiguration *>( sipCpp ) )
    {
      *sipCppRet = dynamic_cast<anatomist::GlobalConfiguration *>( sipCpp );
      sipType = sipType_anatomist_GlobalConfiguration;
    }
  }

%End

  public:
    Observable();
    virtual ~Observable();
    void addObserver(anatomist::Observer*);
    void deleteObserver(anatomist::Observer*);
    void deleteObservers();
    int countObservers() const;
    virtual void notifyObservers(void* = 0);
    virtual void notifyUnregisterObservers();
    bool hasChanged() const;
    bool obsHasChanged( int ) const;
    bool obsHasChanged( const std::string & ) const;
    void setChanged() const;

  protected:
    void clearChanged() const;
    void obsSetChanged( int, bool = true ) const;
    void obsSetChanged( const std::string &, bool = true ) const;
  };


  class Observer
  {
%TypeHeaderCode
#include <anatomist/observer/Observer.h>
#include <anatomist/observer/Observable.h>
#include <anatomist/object/clippedobject.h>
#include <anatomist/surface/textobject.h>
#include <anatomist/surface/transformedobject.h>
%End

%TypeCode
#include <anatomist/graph/Graph.h>
#include <anatomist/graph/GraphObject.h>
#include <anatomist/window/Window.h>
%End

%ConvertToSubClassCode
  // std::cout << "ConvertToSubClassCode Observer " << sipCpp << std::endl;
  sipType = sipType_anatomist_Observer;
  *sipCppRet = sipCpp;
  if( dynamic_cast<anatomist::AObject *>( sipCpp ) )
  {
    *sipCppRet = dynamic_cast<anatomist::AObject *>( sipCpp );
    if (dynamic_cast<anatomist::ASurface_3 *>(sipCpp))
      sipType = sipType_anatomist_ASurface_3;
    else if (dynamic_cast<anatomist::ASurface_2 *>(sipCpp))
      sipType = sipType_anatomist_ASurface_2;
    else if (dynamic_cast<anatomist::MObject *>(sipCpp))
    {
      if (dynamic_cast<anatomist::AGraph *>(sipCpp))
        sipType = sipType_anatomist_AGraph;
      else if (dynamic_cast<anatomist::AGraphObject *>(sipCpp))
        sipType = sipType_anatomist_AGraphObject;
      else if (dynamic_cast<anatomist::ClippedObject *>(sipCpp))
        sipType = sipType_anatomist_ClippedObject;
      else if (dynamic_cast<anatomist::ObjectList *>(sipCpp))
        sipType = sipType_anatomist_ObjectList;
      else
        sipType = sipType_anatomist_MObject;
    }
    else if (dynamic_cast<anatomist::SliceableObject *>(sipCpp))
      sipType = sipType_anatomist_SliceableObject;
    else if (dynamic_cast<anatomist::TextObject *>(sipCpp))
      sipType = sipType_anatomist_TextObject;
    else if (dynamic_cast<anatomist::TransformedObject *>(sipCpp))
      sipType = sipType_anatomist_TransformedObject;
  }
  else if( dynamic_cast<anatomist::AWindow *>( sipCpp ) )
  {
    *sipCppRet = dynamic_cast<anatomist::AWindow *>( sipCpp );
    // std::cout << "  Observer - is a AWindow: " << sipCppRet << std::endl;
    if( dynamic_cast<QAWindow *>(sipCpp) )
    {
      *sipCppRet = dynamic_cast<QAWindow *>( sipCpp );
      if( dynamic_cast<ControlledWindow *>( sipCpp ) )
        if( dynamic_cast<AWindow3D *>( sipCpp ) )
          sipType = sipType_AWindow3D;
        else
          sipType = sipType_ControlledWindow;
      else
        sipType = sipType_QAWindow;
    }
  }
%End

  public:
    Observer();
    virtual ~Observer();
    virtual void update( const anatomist::Observable*, void* ) = 0;

  protected:
    virtual void cleanupObserver();
    virtual void registerObservable( anatomist::Observable* );
    virtual void unregisterObservable( anatomist::Observable* );
  };

};

