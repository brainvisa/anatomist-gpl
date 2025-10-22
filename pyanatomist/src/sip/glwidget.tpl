
namespace anatomist
{

class GLWidgetManager : anatomist::View
{
%TypeHeaderCode
#include <anatomist/window/glwidgetmanager.h>
#include <pyaims/vector/vector.h>
%End

  public:
    virtual ~GLWidgetManager();

%#if 1 // QT_VERSION >= 0x060000%
    QOpenGLWidget *qglWidget ();
%#else%
    QGLWidget *qglWidget ();
%#endif%
    void setPrimitives( const anatomist::GLPrimitives & );
    anatomist::GLPrimitives primitives() const;

    void clearLists();
    void setExtrema( const Point3df &, const Point3df & );
    void setWindowExtrema( const Point3df &, const Point3df & );
    Point3df boundingMin() const;
    Point3df boundingMax() const;
    Point3df windowBoundingMin() const;
    Point3df windowBoundingMax() const;
    void setLightGLList( unsigned );
    void setPreferredSize( int, int );
    void setMinimumSizeHint( const QSize & );
    virtual bool positionFromCursor( int, int, Point3df & );
    virtual bool cursorFromPosition( const Point3df &, Point3df & );
    virtual Point3df objectPositionFromWindow( const Point3df & winpos );
    virtual bool translateCursorPosition( float, float, Point3df & );

    virtual std::string name() const;
    void setZoom( float );
    float zoom() const;
    const aims::Quaternion & quaternion() const;
    void setQuaternion( const Point4df & );
    void setQuaternion( const  aims::Quaternion & );
    // const float* rotation() const;
    void setXDirection( bool );
    void setYDirection( bool );
    void setZDirection( bool );
    bool invertedX() const;
    bool invertedY() const;
    bool invertedZ() const;
    void setRotationCenter( const Point3df & );
    Point3df rotationCenter() const;
    bool perspectiveEnabled() const;
    void enablePerspective( bool );
    void setAutoCentering( bool );
    // bool autoCentering() const;
    virtual void recordStart( const QString &,
                              const QString & = QString() );
    void saveContents( const QString &, const QString &, int=0, int=0 );
    void saveOtherBuffer( const QString &,
                          const QString &, int, int=0, int=0 );
    QImage snapshotImage( int bufmode, int width=0, int height=0 );
    void setOtherBuffersSaveMode( int );
    int otherBuffersSaveMode() const;

    bool hasTransparentObjects() const;
    void setTransparentObjects( bool );
    bool depthPeelingAllowed() const;
    unsigned numTextureUnits() const;
    anatomist::AWindow *aWindow();
    virtual int width() = 0;
    virtual int height() = 0;
    virtual void paintScene();
    virtual void updateGL();

  private :
    GLWidgetManager( const anatomist::GLWidgetManager& );
    GLWidgetManager();
};

};



%#if 1 // QT_VERSION >= 0x060000 // #ifdef ANA_USE_QOPENGLWIDGET%
class QAGLWidget : QOpenGLWidget, anatomist::GLWidgetManager
%#else%
class QAGLWidget : QGLWidget, anatomist::GLWidgetManager
%#endif%
{
%TypeHeaderCode
#include <anatomist/window/glwidget.h>
#include <pyaims/vector/vector.h>

%End

  public:

%#if 1 // QT_VERSION >= 0x060000 // #ifdef ANA_USE_QOPENGLWIDGET%
    QAGLWidget( anatomist::AWindow*, QWidget* = 0,
                const char* = 0,
                const QOpenGLWidget * = 0,
                Qt::WindowFlags = Qt::WindowFlags() );
%#else%
    QAGLWidget( anatomist::AWindow*, QWidget* = 0,
                const char* = 0,
                const QGLWidget * = 0, Qt::WindowFlags = Qt::WindowFlags() );
%#endif%
    virtual ~QAGLWidget();

    virtual QSize sizeHint() const;
    virtual QSize minimumSizeHint() const;
    virtual std::string name() const;

  signals:
    void viewRendered();

  public slots:
    virtual void updateGL();
    virtual void saveContents();
    virtual void recordStart();
    virtual void recordStop();

  private :
    QAGLWidget( const QAGLWidget& );
};


