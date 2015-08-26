namespace anatomist
{

  class QAObjectDrag /*: QUriDrag */
  {
%TypeHeaderCode
#include <anatomist/control/objectDrag.h>
%End

  public:
    QAObjectDrag( const set_AObjectPtr & );
    virtual ~QAObjectDrag();

    static bool canDecode( const QMimeData * e );
    static bool canDecodeURI( const QMimeData * e );
    static bool decode( const QMimeData * e, set_AObjectPtr & o );
    static SIP_PYTUPLE decodeURI( const QMimeData * e );
%MethodCode
  std::list<QString> l1, l2;
  bool x = anatomist::QAObjectDrag::decodeURI( a0, l1, l2 );
  if( !x )
  {
    Py_INCREF( Py_None );
    sipRes = Py_None;
  }
  else
  {
    PyObject *objs = PyList_New( l1.size() );
    std::list<QString>::iterator il, el = l1.end();
    int i = 0;
    for( il=l1.begin(); il!=el; ++il, ++i  )
      PyList_SetItem( objs, i, PyString_FromString( il->toLocal8Bit().data() ) );
    PyObject *ana = PyList_New( l2.size() );
    i = 0;
    for( il=l2.begin(), el=l2.end(); il!=el; ++il, ++i  )
      PyList_SetItem( ana, i, PyString_FromString( il->toLocal8Bit().data() ) );
    sipRes = PyTuple_New( 2 );
    PyTuple_SetItem( sipRes, 0, objs );
    PyTuple_SetItem( sipRes, 1, ana );
  }
%End

  private:
    QAObjectDrag( const anatomist::QAObjectDrag & );
  };

};

