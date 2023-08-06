from colt import Colt
from colt.colt import ColtMeta
from abc import abstractmethod
import subprocess as sp
from .atominfo import atomnumber_to_atomname
from .gauwrite import write_gaufile


def write_content_to_file(fileName, content, options="w"):
    """ write content to file [fileName]

        fileName = str, Name of the file to be read
        content  = str, content written to the file
    """
    with open(fileName, options) as f:
        f.write(content)


class Logger:
    """Basic Logger"""

    def __init__(self, filename):
        self.fh = open(filename, 'w')

    def __del__(self):
        if self.fh.closed is False:
            self.fh.close()

    def write(self, msg):
        self.fh.write(f"{msg}\n")

    def warning(self, msg):
        self.fh.write(f"Warning: {msg}\n")

    def error(self, msg, error='ValueError'):
        self.fh.write(f"{error}: {msg}\n")
        self.fh.close()
        if error == 'ErrorTermination':
            error = 'SystemExit'

        if error == 'ValueError':
            raise ValueError(msg)
        if error == 'SystemExit':
            raise SystemExit(msg)
        raise SystemExit


_GAUSSIAN_BASE_INTERFACE = """
# which layer in a ONIOM Calculation
layer = :: str :: R, M, S
# Name of the Gau-xxx.EIn file
inputfile = :: existing_file
# Name of the Gau-xxx.EOu file
outputfile = :: file
# Write additional information to gauout
msgfile = :: file
# name of a gaussian fchk file
fchkfile = :: file
# 
matelfile = :: file
"""

class ExternalMeta(ColtMeta):

    def __new__(cls, name, bases, clsdict):
        if '_user_input' in clsdict:
            clsdict['_user_input'] += _GAUSSIAN_BASE_INTERFACE
        else:
            clsdict['_user_input'] = _GAUSSIAN_BASE_INTERFACE

        return ColtMeta.__new__(cls, name, bases, clsdict)


class GaussianExternalInterface(Colt, metaclass=ExternalMeta):
    """ Read Gaussian External Input File """

    au2ang = 1.0/1.889725949297217

    def __init__(self, input_file):
        """ Sets up GaussianExternalInterface

            :
        """
        self.inp_file = input_file

    @property
    def method(self):
        return self.inp_file.imethod

    @property
    def logger(self):
        return self.inp_file.logger

    def log_write(self, msg):
        return self.inp_file.logger.write(msg)

    def log_warning(self, msg):
        return self.inp_file.logger.warning(msg)

    def log_error(self, msg, error='SystemExit'):
        return self.inp_file.logger.error(msg, error=error)

    @property
    def chg(self):
        return self.inp_file.chg

    @property
    def natoms(self):
        return self.inp_file.natoms

    @property
    def atomids(self):
        return self.inp_file.atomids

    @property
    def charges(self):
        return self.inp_file.charges

    @property
    def coords(self):
        return self.inp_file.coords

    @classmethod
    def run(cls):
        self = cls.from_commandline()
        self.do_calculation()

    def do_calculation(self):
        # write the inputs that are method dependent and run the corresponding code
        (e, d), grad, hess = self.__run_interface()
        self.inp_file.save(e, d, gradient=grad, force_constants=hess)

    def __run_interface(self):
        if self.method == 0:
            result = self._run_energy()
        elif self.method == 1:
            result = self._run_gradient()
        elif self.method == 2:
            result = self._run_frequency()
        else:
            raise ValueError(("Input Method can only be '0, 1, 2' ",
                              "but not %d" % self.method))
        return result

    @abstractmethod
    def _run_energy(self):
        ...

    @abstractmethod
    def _run_gradient(self):
        ...

    @abstractmethod
    def _run_frequency(self):
        ...

    def run_interface(self, script, name):
        self.log_write(f"""
 ############## Run section: GAUEXT  ##############
    Interface {name} call:
 --------------------------------------------------
    {script}
 --------------------------------------------------
 """)
        error = sp.call(script, shell=True)
        if error == 0:
            self.log_write("Normal Termination of interface")
            return True
        self.log_write('Error Termination: *** Something went wrong! ***')
        self.log_write("Error count: {error}")
        return False

    @classmethod
    def write_xyz_file(cls, filename, natoms, comment, atomids, coords):
        txt = "".join(["%d\n" % natoms,
                       "%s\n" % comment,
                       "".join(cls.get_coordinates(atomid, coord)
                               for atomid, coord in zip(atomids, coords))
                       ])
        write_content_to_file(filename, txt)

    @classmethod
    def get_coordinates(cls, atomid, coords):
        return "% 4s    % 14.10f   % 14.10f   % 14.10f \n" % (
               atomid, cls.au2ang*coords[0], cls.au2ang*coords[1], cls.au2ang*coords[2])



class GaussianExternalInput:

    @classmethod
    def from_config(cls, config):
        return cls(config['inputfile'], 
                   config['msgfile'],
                   config['layer'], 
                   config['outputfile'],
                   config['fchkfile'],
                   config['matelfile'])

    def __init__(self, inputfile, msgfile, layer=None, outputfile=None, fchkfile=None, matelfile=None):
        """
        > gauinp = ExternalInput(filename)
        > coords = gauinp.coords
        > NAtoms = gauinp.natoms

        :str filename: Gau-XXX.EIn, name of the external input file
                       created by gaussian

        """
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.fchkfile = fchkfile
        self.matelfile = matelfile
        #
        self.logger = Logger(msgfile)
        #
        (self.natoms, self.imethod, self.chg,
            self.mult, self.coords, self.atomids, self.charges, self.conn) = self.parse(inputfile)


    def save(self, energy, dipole, gradient=None, polarizability=None, dipole_deriv=None, force_constants=None):
        self.logger.write("Saving External Interface results")
        write_gaufile(self.outputfile, self.imethod, self.natoms, energy, dipole, gradient=gradient, force_constants=force_constants)
        self.logger.write("Exiting Interface")

    def _get_coordinates(self, line):
        res = line.split()
        return (atomnumber_to_atomname[int(res[0])],
                [float(res[1]), float(res[2]), float(res[3])],
                float(res[4]))

    def _get_connectivity(self, line):
        """ getConnectivity as non redundant gaussian connectivity """

        columns = line.split()
        if len(columns) == 1.0:
            return []
        return [int(i) for j, i in columns[1:] if j % 2 == 0]

    def _get_redundant_connectivity(self, conn):
        """ convert non redundant connectivity in reduant one """
        for i, ele in enumerate(conn):
            for e in ele:
                if i+1 not in conn[e-1]:
                    conn[e-1].append(i+1)
        return conn

    def parse(self, filename, conn=False, tConn='red'):
        """ Parse the gaussian external input file """
        with open(filename, "r") as f:
            line = f.readline()
            natoms, imethod, chg, mult = map(int, line.split())
            coords = []
            atomids = []
            charges = []
            for _ in range(natoms):
                atomid, coord, charge = self._get_coordinates(f.readline())
                coords.append(coord)
                atomids.append(atomid)
                charges.append(charge)
            if conn is True:
                connectivity = tuple(self._get_connectivity(line) for line in f.readline())
                if tConn == 'red':
                    connectivity = self._get_redundant_connectivity(connectivity)
            else:
                connectivity = None
        self.logger.write(f"Reading file '{filename}' completed: NAtoms={natoms}, Method={imethod}, chg={chg}, mult={mult}") 
        return natoms, imethod, chg, mult, coords, atomids, charges, connectivity

    def _write_coordinate_line(self, coord):
        return " %8s  %12.8f  %12.8f %12.8f " % (coord[0], coord[1][0], coord[1][1], coord[1][2])
