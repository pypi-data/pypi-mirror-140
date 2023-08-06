.. include:: replace.rst

Miscellaneous functions
=======================


|menu_calceph_getmaxsupportedorder|
-----------------------------------

.. ifconfig:: calcephapi in ('C')

    .. c:function:: int calceph_getmaxsupportedorder (int segid)

        :param  segid: |arg_segid|
        :return: maximal order of the computable derivatives for this type of segment.

.. ifconfig:: calcephapi in ('F2003')

    .. f:function:: calceph_getmaxsupportedorder (segid) BIND(C)
    
        :param  segid [INTEGER, intent(in)]: |arg_segid|
        :r calceph_getmaxsupportedorder: maximal order of the computable derivatives for this type of segment.
        :rtype calceph_getmaxsupportedorder: INTEGER(C_INT)

.. ifconfig:: calcephapi in ('F90')

     .. f:subroutine:: f90calceph_getmaxsupportedorder (segid) 
     
        :param  version [INTEGER, intent(in)]: |arg_segid|
        :r f90calceph_getmaxsupportedorder: maximal order of the computable derivatives for this type of segment.
        :rtype f90calceph_getmaxsupportedorder: INTEGER

.. ifconfig:: calcephapi in ('Python')

    .. py:method:: getmaxsupportedorder (segid)  
    
        :param  int segid: |arg_segid|
        :return: |arg_version|
        :rtype: str 

.. ifconfig:: calcephapi in ('Mex')

    .. mat:function:: calceph_getmaxsupportedorder (segid) 
    
        :param  int arg_segid: |arg_segid|
        :return: maximal order of the computable derivatives for this type of segment.
        :rtype: int




This function returns the maximal order of the derivatives computed by the functions |calceph_compute_order|, |calceph_orient_order|, ....  for the segment type *segid*.
If the segment type is unknown by the library, the function returns -1.

.. ifconfig:: calcephapi in ('C', 'F2003', 'F90')
    
    The accepted values of *segid* are the predefined constants *CALCEPH_SEGTYPE_...* (:ref:`Constants`).

.. ifconfig:: calcephapi in ('Python', 'Mex')
    
    The accepted values of *segid** are the predefined constants *Constants.SEGTYPE_...* (:ref:`Constants`).


.. ifconfig:: calcephapi in ('C')

    ::
              
        int maxorder = calceph_getmaxsupportedorder(CALCEPH_SEGTYPE_SPK_2);
        printf ("maximal order is %d \n", maxorder);


.. ifconfig:: calcephapi in ('F2003')

    ::
              
        integer maxorder
        
        maxorder = calceph_getmaxsupportedorder(CALCEPH_SEGTYPE_SPK_2)
        write(*,*) 'maximal order is ', maxorder


.. ifconfig:: calcephapi in ('F90')

    ::

        integer maxorder
        
        maxorder = calceph_getmaxsupportedorder(CALCEPH_SEGTYPE_SPK_2)
        write(*,*) 'maximal order is ', maxorder


.. ifconfig:: calcephapi in ('Python')

    ::

        from calcephpy import *
        maxorder = getmaxsupportedorder(Constants.SEGTYPE_SPK_2)
        print('maximal order is ', maxorder)


.. ifconfig:: calcephapi in ('Mex')

    ::

        maxorder = calceph_getmaxsupportedorder(Constants.SEGTYPE_SPK_2)


|menu_calceph_getversion_str|
-----------------------------

.. ifconfig:: calcephapi in ('C')

    .. c:function:: void calceph_getversion_str ( char version[CALCEPH_MAX_CONSTANTNAME])

        :param  version: |arg_version|

.. ifconfig:: calcephapi in ('F2003')

    .. f:subroutine:: calceph_getversion_str (version) BIND(C)
    
        :param  version [CHARACTER(len=1,kind=C_CHAR), dimension(CALCEPH_MAX_CONSTANTNAME), intent(out)]: |arg_version|

.. ifconfig:: calcephapi in ('F90')

     .. f:subroutine:: f90calceph_getversion_str (version) 
     
        :param  version [CHARACTER(len=CALCEPH_MAX_CONSTANTNAME), intent(out)]: |arg_version|

.. ifconfig:: calcephapi in ('Python')

    .. py:method:: calcephpy.getversion_str () 
    
        :return: |arg_version|
        :rtype: str 

.. ifconfig:: calcephapi in ('Mex')

    .. mat:function:: calceph_getversion_str () 
    
        :returns: |arg_version|
        :rtype: str 


.. ifconfig:: calcephapi in ('C')

    This function returns the version of the |LIBRARYNAME|, as a null-terminated string.

.. ifconfig:: calcephapi in ('F2003', 'F90', 'Python', 'Mex')

    This function returns the version of the |LIBRARYNAME|, as a string.

.. ifconfig:: calcephapi in ('F90', 'F2003')

    Trailing blanks are added to the name version.


.. ifconfig:: calcephapi in ('C')

    ::
              
        char cversion[CALCEPH_MAX_CONSTANTNAME];
        calceph_getversion_str(cversion);
        printf ("library version is '%s'\n", cversion);


.. ifconfig:: calcephapi in ('F2003')

    ::
              
           character(len=CALCEPH_MAX_CONSTANTNAME) version
           
           call calceph_getversion_str(version)
           write(*,*) 'library version is ', version


.. ifconfig:: calcephapi in ('F90')

    ::

           character(len=CALCEPH_MAX_CONSTANTNAME) version
           
           call f90calceph_getversion_str(version)
           write(*,*) 'library version is ', version


.. ifconfig:: calcephapi in ('Python')

    ::

        from calcephpy import *
        print('version=', getversion_str())


.. ifconfig:: calcephapi in ('Mex')

    ::

        version = calceph_getversion_str()

