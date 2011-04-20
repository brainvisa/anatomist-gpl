TEMPLATE        = lib
TARGET  = pyanatomistexports${BUILDMODEEXT}

#!include ../../config

LIBS = ${ANATOMIST_LIBS}

HEADERS = \
        event.h \
        objectparamselectsip.h \
        pyanatomist.h \
        serializingcontext.h \
        sipconverthelpers.h

SOURCES = \
        objectparamselectsip.cc \
        pyanatomist.cc \
        serializingcontext.cc

