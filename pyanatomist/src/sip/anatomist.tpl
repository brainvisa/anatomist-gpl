%Import aims.sip

%Import QtCore/QtCoremod.sip
%Import QtGui/QtGuimod.sip
%Import QtWidgets/QtWidgetsmod.sip
%Import QtOpenGL/QtOpenGLmod.sip
%#if QT_VERSION >= 0x060000%
%Import QtOpenGLWidgets/QtOpenGLWidgetsmod.sip
%#endif%

%Module anatomist.cpp.anatomistsip

%Include anatomist.sip

