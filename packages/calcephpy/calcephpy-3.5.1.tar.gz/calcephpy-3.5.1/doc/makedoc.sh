#! /bin/bash
#/*-----------------------------------------------------------------*/
#/*! 
#  \file makedoc.sh
#  \brief shell script to build the html and latex documentation
#  \author  M. Gastineau 
#           Astronomie et Systemes Dynamiques, IMCCE, CNRS, Observatoire de Paris. 
#
#   Copyright, 2008-2020, CNRS
#   email of the author : Mickael.Gastineau@obspm.fr
#  
#*/
#/*-----------------------------------------------------------------*/
#
#/*-----------------------------------------------------------------*/
#/* License  of this file :
#  This file is "triple-licensed", you have to choose one  of the three licenses 
#  below to apply on this file.
#  
#     CeCILL-C
#       The CeCILL-C license is close to the GNU LGPL.
#       ( http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html )
#   
#  or CeCILL-B
#        The CeCILL-B license is close to the BSD.
#        (http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.txt)
#  
#  or CeCILL v2.1
#       The CeCILL license is compatible with the GNU GPL.
#       ( http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html )
#  
# 
# This library is governed by the CeCILL-C, CeCILL-B or the CeCILL license under 
# French law and abiding by the rules of distribution of free software.  
# You can  use, modify and/ or redistribute the software under the terms 
# of the CeCILL-C,CeCILL-B or CeCILL license as circulated by CEA, CNRS and INRIA  
# at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C,CeCILL-B or CeCILL license and that you accept its terms.
# */
# /*-----------------------------------------------------------------*/
CMD_MAKE_SPHINX="make -f Makefile.sphinx"
SPHINX_BUILD_HTML="sphinx-build -b html -d build/doctrees"

find html -not -path '*.svn*' -exec rm -f {} \;
rm -r -f  calceph_*.pdf


$CMD_MAKE_SPHINX clean
$SPHINX_BUILD_HTML -c source_c source html/c || exit 1

$CMD_MAKE_SPHINX clean
$SPHINX_BUILD_HTML -c source_f2003 source html/fortran2003|| exit 1

$CMD_MAKE_SPHINX clean
$SPHINX_BUILD_HTML -c source_f9x source html/fortran77 || exit 1
 
$CMD_MAKE_SPHINX clean
$SPHINX_BUILD_HTML -c source_python source html/python || exit 1

$CMD_MAKE_SPHINX clean
$SPHINX_BUILD_HTML -c source_mex source html/mex || exit 1

$CMD_MAKE_SPHINX clean
$CMD_MAKE_SPHINX latexpdf SPHINXOPTS="-c source_c" && mv build/latex/calceph.pdf calceph_c.pdf || exit 1

$CMD_MAKE_SPHINX clean
$CMD_MAKE_SPHINX latexpdf SPHINXOPTS="-c source_f2003" && mv build/latex/calceph.pdf calceph_fortran2003.pdf || exit 1

$CMD_MAKE_SPHINX clean
$CMD_MAKE_SPHINX latexpdf SPHINXOPTS="-c source_f9x" && mv build/latex/calceph.pdf calceph_fortran77.pdf || exit 1
 
$CMD_MAKE_SPHINX clean
$CMD_MAKE_SPHINX latexpdf SPHINXOPTS="-c source_python" && mv build/latex/calceph.pdf calceph_python.pdf || exit 1

$CMD_MAKE_SPHINX clean
$CMD_MAKE_SPHINX latexpdf SPHINXOPTS="-c source_mex" && mv build/latex/calceph.pdf calceph_mex.pdf || exit 1


$CMD_MAKE_SPHINX clean

#remove hidden file
rm -f html/*/.buildinfo

#generate the list of dependencies
FILELIST=`find html -name \*.\* -print` 
echo 'LISTFILEHTML='$FILELIST >Makefile_listdoc.am

# suppression des index inutiles en html : 
#pour le C
HTMLSRC=html/c/genindex.html
SEARCHSRC=html/c/searchindex.js 
perl -p -i -e 's/a>\n/a>/' $HTMLSRC
grep -v fortran $HTMLSRC | grep -v 'built-in' | grep -v calcephpy  | grep -v 'CalcephBin' >tmpfile && mv tmpfile $HTMLSRC
perl -p -i -e 's/"f\/_\/([^]])*]\,//g' $SEARCHSRC

#pour le fortran 2003
HTMLSRC=html/fortran2003/genindex.html
SEARCHSRC=html/fortran2003/searchindex.js 
perl -p -i -e 's/a>\n/a>/' $HTMLSRC
grep -v '(C ' $HTMLSRC | grep -v 'built-in' |  grep -v 'f90' |grep -v calcephpy | grep -v 'CalcephBin' >tmpfile && mv tmpfile $HTMLSRC
sed -i  -e 's/<a\(.*\)\_\/\(.*\)"><strong>(fortran variable)/<a\1\_\/\2"><strong>\2 \(fortran variable\)/g'  $HTMLSRC
perl -p -i -e 's/"f\/_\/f90([^]])*]\,//g' $SEARCHSRC

#pour le fortran 77
HTMLSRC=html/fortran77/genindex.html
SEARCHSRC=html/fortran77/searchindex.js 
perl -p -i -e 's/a>\n/a>/' $HTMLSRC
grep -v '(C ' $HTMLSRC | grep -v 'built-in' | grep -v calcephpy | grep -v '#f/_/calceph_' | grep -v 'CalcephBin' >tmpfile && mv tmpfile $HTMLSRC
sed -i  -e 's/<a\(.*\)\_\/\(.*\)"><strong>(fortran variable)/<a\1\_\/\2"><strong>\2 \(fortran variable\)/g'  $HTMLSRC

#pour le python
HTMLSRC=html/python/genindex.html
SEARCHSRC=html/python/searchindex.js 
perl -p -i -e 's/a>\n/a>/' $HTMLSRC
grep -v fortran $HTMLSRC | grep -v '(C '  | grep -v '(CalcephBin' >tmpfile && mv tmpfile $HTMLSRC
perl -p -i -e 's/"f\/_\/([^]])*]\,//g' $SEARCHSRC

#pour le Mex
HTMLSRC=html/mex/genindex.html
SEARCHSRC=html/mex/searchindex.js 
perl -p -i -e 's/a>\n/a>/' $HTMLSRC
grep -v '(C ' $HTMLSRC  | grep -v calcephpy | grep -v 'fortran' >tmpfile && mv tmpfile $HTMLSRC
perl -p -i -e 's/"f\/_\/([^]])*]\,//g' $SEARCHSRC

echo 'Generating the documentation.....ok'

