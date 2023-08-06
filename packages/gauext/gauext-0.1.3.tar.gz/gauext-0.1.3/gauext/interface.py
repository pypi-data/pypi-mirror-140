from abc import ABC, abstractmethod
import subprocess as sp
#
from .fileio import write_content_to_file




class GaussianExternalInterface(ABC):

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

    def do_calculation(self):
        # write the inputs that are method dependent and run the corresponding code
        return self.__run_interface()

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
        self.log_write("""
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
