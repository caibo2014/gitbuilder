#!/bin/bash -x
#
# Copy this file to build.sh so that gitbuilder can run it.
#
# What happens is that gitbuilder will checkout the revision of your software
# it wants to build in the directory called gitbuilder/build/.  Then it
# does "cd build" and then "../build.sh" to run your script.
#
# You might want to run ./configure here, make, make test, etc.
#

# Don't forget to run autoconf and ./configure, if that's what your project
# needs.

# just use make-debs.sh

./make-debs.sh /ceph_tmp/release

# Actually build the project
#make || exit 3

# Only run the unit tests if the 'make test' target exists.  Make will
# return 1 if a target exists but isn't up-to-date, or 2 on error.
#make -q tests
#if [ "$?" = 1 ]; then
#	# run "make test", but give it a time limit in case a test gets stuck
#	../maxtime 1800 make test || exit 4
#fi

exit 0
