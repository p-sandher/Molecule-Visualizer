CC = clang
CFLAGS = -Wall -std=c99 -pedantic
SPATH = /usr/include/python3.7m
SLIBPATH = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

all: libmol.so _molecule.so

clean:
	rm -f *.o *.so molecule_wrap.c molecule.py

libmol.so: mol.o
	$(CC) mol.o -shared -lm -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) mol.c -c -fpic -o mol.o

swig: molecule.i mol.h
	swig -python molecule.i

molecule_wrap.o: swig
	$(CC) $(CFLAGS) -c molecule_wrap.c -I$(SPATH) -fpic -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) $(CFLAGS) -shared molecule_wrap.o -lm -dynamiclib -L$(SLIBPATH) -L. -lmol -o _molecule.so

#export LD_LIBRARY_PATH=`pwd`3
