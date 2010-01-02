%Import aims.sip

// switch to Qt 3 or Qt 4
%#if QT_VERSION >= 0x040000%
%Import QtOpenGL/QtOpenGLmod.sip
// allow tests for Qt3/Qt4 by "extending" the PyQt timeline
%Timeline {Qt_3_3_6}
%#else%
%Import qt/qtmod.sip
%Import qtgl/qtglmod.sip
// allow tests for Qt3/Qt4 by "extending" the PyQt timeline
%Timeline {Qt_4_1_1}

%#if defined( __POWERPC__ )%
typedef long GLint;
%#else%
typedef int GLint;
%#endif%
%#endif%

%Module anatomist.cpp.anatomistsip

%Include anatomist.sip

