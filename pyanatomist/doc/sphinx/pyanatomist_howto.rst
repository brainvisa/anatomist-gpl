How to
++++++

Use / change Anatomist settings
-------------------------------

>>> import anatomist.direct.api as ana
>>> a = ana.Anatomist()
>>> print a.config()['windowSizeFactor' ]
2.0
>>> a.config()['windowSizeFactor' ] = 1.
>>> print a.config()['windowSizeFactor' ]
1.0

Configuration options are those recognized in the configuration file.
It is documented :anatomist:`here in the embedded help <html/en/programming/config.html>`.
