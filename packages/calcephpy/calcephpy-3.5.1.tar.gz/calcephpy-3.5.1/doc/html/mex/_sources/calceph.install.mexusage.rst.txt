Installation
************

The following section describes the installation of the **Mex** interface of the library.
If you want to install the interface for another programming language, you have to follow the instructions of the manual of that language.  

Unix-like system (Linux, Mac OS X, BSD, Cygwin, ...)
====================================================

Here are the steps needed to install the Mex interface of the library on Unix systems. 
In the following instructions, you must replace */home/mylogin/mydir* by the directory location where you want to install calceph.


.. highlight::  bash

    
If you use the Mex interface of the library for Octave (4.0 or later), you have to start Octave and execute the following commands.

    .. parsed-literal::

        pkg install -local  calcephoct-|version|.tar.gz


If you use the Mex interface of the library for Matlab (2017 or later), you have to use a C compiler compliant with your software Matlab, usually gcc.  If you use the gcc compiler, the steps are :

    * Compile of the dynamic library with the following command (replace /home/mylogin/mydir by the correct value) :
    
        .. parsed-literal::

            tar xzf calceph-|version|.tar.gz
            cd calceph-|version|
            ./configure --enable-shared --disable-static CC=gcc --enable-fortran=no --prefix=/home/mylogin/mydir
            make check && make install
        
    * Start Matlab and execute (replace /home/mylogin/mydir by the correct value) in order to compile the Mex interface:
        
        .. parsed-literal::

            addpath('/home/mylogin/mydir/libexec/calceph/mex')
            calceph_compilemex()

    * Add the path */home/mylogin/mydir/lib* to the environment variables **LD_LIBRARY_PATH** or **DYLD_LIBRARY_PATH**.
    
    * Add the path */home/mylogin/mydir/libexec/calceph/mex* to the environment variable **MATLABPATH**, in order to have the calceph functions available at the start of Mathlab.

Windows system
==============

Using the Microsoft Visual C++ compiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need the Microsoft Visual C++ compiler, such as cl.exe, and the Universal CRT SDK or a Windows SDK. 

The  "Universal CRT (C runtime) SDK" or a "Windows SDK" are now provided with the Microsoft Visual Studio.
You should verify that "Universal CRT (C runtime) SDK" or a "Windows SDK" is selected in the "Visual Studio Installer".      


The steps are :


* Expand the file calceph-|version|.tar.gz

* Execute the command ..:command:`cmd.exe` from the menu *Start / Execute...*

    This will open a console window

* cd *dir*\\calceph-|version|

    Go to the directory *dir* where |LIBRARYNAME| has been expanded.

* nmake /f Makefile.vc 

    This compiles |LIBRARYNAME| in the working directory.
    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *cl.exe*

* nmake /f Makefile.vc check

    This will make sure that the |LIBRARYNAME| was built correctly.

    If you get error messages, please report them to |EMAIL| (see :ref:`Reporting bugs`, for information on what to include in useful bug reports).

    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *cl.exe*

* nmake /f Makefile.vc  install DESTDIR= *dir*

    This will copy the file :file:`calceph.h` to the directory *dir*, the file :file:`libcalceph.lib` to the directory *dir* **\\lib**, the documentation files to the directory *dir* **\\doc**. Note: you need write permissions on these directories.

    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *cl.exe*

 
* If you don't install in a standard path, add  *dir* **\\lib**  to the environment variables **LD_LIBRARY_PATH**.

* Add the path *dir* **\\libexec\\calceph\\mex** to the environment variable **MATLABPATH** 

* Start Matlab or Octave and execute the following command in order to compile the Mex interface:
    
    .. parsed-literal::

       addpath('*dir* **\\libexec\\calceph\\mex**')
       calceph_compilemex()


Using the MinGW
~~~~~~~~~~~~~~~

You need a C compiler, such as gcc.exe.


* Expand the file calceph-|version|.tar.gz

* Execute the command *MinGW Shell* from the menu *Start*.

    This will open a MinGW Shell console window.

* cd *dir*\\calceph-|version|

    Go to the directory *dir* where |LIBRARYNAME| has been expanded.

* make -f Makefile.mingw

    This compiles |LIBRARYNAME| in the working directory.

    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *gcc.exe*


* make -f Makefile.mingw check

    This will make sure that the |LIBRARYNAME| was built correctly.

    If you get error messages, please report them to |EMAIL| (see :ref:`Reporting bugs` ,  for information on what to include in useful bug reports).

    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *gcc.exe*


* make -f Makefile.mingw install DESTDIR= *dir*

    This will copy the file  :file:`calceph.h`  to the directory *dir*, the file :file:`libcalceph.lib` to the directory *dir* **\\lib**, the documentation files to the directory *dir* **\\doc**. 

    Note: you need write permissions on these directories.

    This command line accepts several options :

    * CC= ``xx``

        specifies the name of the C compiler. The defaut value is *gcc.exe*

 
* If you don't install in a standard path, add  *dir* **\\lib**  to the environment variables **LD_LIBRARY_PATH**.

* Add the path *dir* **\\libexec\\calceph\\mex** to the environment variable **MATLABPATH** 

* Start Matlab or Octave and execute the following command in order to compile the Mex interface:
    
    .. parsed-literal::

       addpath('*dir* **\\libexec\\calceph\\mex**')
       calceph_compilemex()

.. highlight::  none
  

.. highlight::  none
