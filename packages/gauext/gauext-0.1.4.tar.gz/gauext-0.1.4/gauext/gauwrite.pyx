from libc.stdio cimport sprintf, fprintf, FILE, fopen, fclose
cimport numpy as np
import numpy as np


cdef void fortran_format_i(const int f, char* string):
    sprintf(string, "%20.12e", f);
    string[16] = b'D';

cdef void fortran_format_d(const double f, char* string):
    sprintf(string, "%20.12e", f);
    string[16] = b'D';

cdef void fortran_format_f(const float f, char* string):
    sprintf(string, "%20.12e", f);
    string[16] = b'D';

cdef void fprintout(FILE* fp, np.ndarray f, const int N):
    assert f.dtype == np.double or f.dtype == np.int

    cdef char[21] string;

    if f.dtype == np.double:
        for i, ele in enumerate(f):
            fortran_format_d(ele, string)
            fprintf(fp, string);
            if i % N == N-1:
                fprintf(fp, "\n");
    elif f.dtype == np.int:
        for i, ele in enumerate(f):
            fortran_format_i(ele, string);
            fprintf(fp, string);
            if i % N == N-1:
                fprintf(fp, "\n");

cdef void display_zeros(FILE* fp, const int nele):
    cdef np.ndarray value = np.zeros((nele,), dtype=np.double);
    fprintout(fp, value, 3)



def write_gaufile(filename, iopts, natoms, energy, dipole,
                  gradient=None, polarizability=None, dipole_deriv=None,
                  force_constants=None):
    cdef FILE* fp;
    cdef char[21] string;
    cdef np.ndarray _value;
    cdef np.ndarray e_and_dip = np.array([energy, dipole[0], dipole[1], dipole[2]], dtype=np.double)
    fp = fopen(filename.encode('utf-8'), "w")
    # write e_and_dip
    fprintout(fp, e_and_dip, 4)
    if iopts == 0:
        pass
    else:
        #
        if gradient is None:
            raise ValueError("Gradient asked, but not provided")
        fprintout(fp, gradient.flatten(), 3)
            
        if iopts == 2:
            if force_constants is None:
                raise ValueError("Frequency asked but not provided")
            #

            if polarizability is None:
                display_zeros(fp, 6)
            else:
                fprintout(fp, polarizability.flatten(), 3)

            if dipole_deriv is None:
                display_zeros(fp, 9*natoms)
            else:
                fprintout(fp, dipole_deriv.flatten(), 3)
            fprintout(fp, force_constants.flatten(), 3)
    #
    fclose(fp);
