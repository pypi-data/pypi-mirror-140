`ffmpegio-plugin-static-ffmpeg`: A Python `ffmpegio` plugin to use FFmpeg binaries in `static-ffmpeg` package
=============================================================================================================

|pypi| |pypi-status| |pypi-pyvers| |github-license| |github-status|

.. |pypi| image:: https://img.shields.io/pypi/v/ffmpegio-plugin-static-ffmpeg
  :alt: PyPI
.. |pypi-status| image:: https://img.shields.io/pypi/status/ffmpegio-plugin-static-ffmpeg
  :alt: PyPI - Status
.. |pypi-pyvers| image:: https://img.shields.io/pypi/pyversions/ffmpegio-plugin-static-ffmpeg
  :alt: PyPI - Python Version
.. |github-license| image:: https://img.shields.io/github/license/python-ffmpegio/python-ffmpegio-plugin-static-ffmpeg
  :alt: GitHub License
.. |github-status| image:: https://img.shields.io/github/workflow/status/python-ffmpegio/python-ffmpegio-plugin-static-ffmpeg/Run%20Tests
  :alt: GitHub Workflow Status

`Python ffmpegio <https://python-ffmpegio.github.io/python-ffmpegio/>`__ package aims to bring 
the full capability of `FFmpeg <https://ffmpeg.org>`__ to read, write, and manipulate multimedia 
data to Python. FFmpeg is an open-source cross-platform multimedia framework, which can handle 
most of the multimedia formats available today.

One caveat of FFmpeg is that there is no official program installer for Windows and MacOS (although 
`homebrew` could be used for the latter). `ffmpegio-plugin-static-ffmpeg` enables the `ffmpegio` package to 
use the build of FFmpeg distributed by the `static-ffmpeg <https://github.com/zackees/static_ffmpeg>`__ 
package.

Use
===

Simply install the package:

.. code-block:: bash

  pip install ffmpegio-core ffmpegio-plugin-static-ffmpeg

Then `ffmpegio` will auto-detect the plugin and `static-ffmpeg`'s executables:

.. code-block:: python
  
  import ffmpegio

  print(ffmpegio.path.FFMPEG_BIN) # ...\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe
  print(ffmpegio.path.FFPROBE_BIN) # ...\site-packages\static_ffmpeg\bin\win32\ffprobe.exe
  
Because the `static-ffmpeg` package downloads its binaries on demand, the first
time importing `ffmpegio` with this plugin enabled may take a while.

.. note::
  `ffmpegio-plugin-static-ffmpeg` will *not* be activated if `ffmpeg` and `ffprobe` are 
  already available on the system PATH.
