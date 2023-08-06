import os
from colt import Colt
import numpy as np

from .gaussian import GaussianExternalInterface, GaussianExternalInput


def _parse_diple(fh):
    for _ in range(2):
        next(fh)
    cols = next(fh).split()
    return [float(cols[1]), float(cols[2]), float(cols[3])]


def _parse_wbo(natoms, filename):
    wbo = np.zeros((natoms, natoms))
    with open(filename, 'r') as fh:
        for line in fh:
            i, j, value = line.split()
            i, j, value = int(i), int(j), float(value)
            wbo[i,j] = value
            wbo[j,i] = value
    return wbo



class XTBInterface(GaussianExternalInterface):

    name = "XTB"
    executable = 'xtb'
    _command = "%s %s --chrg %d %s --wbo "

    _user_input = """
    options = :: str, optional, alias=o
    save = false :: bool, alias=s
    input = xtbinput.xyz :: file
    """

    @classmethod
    def from_config(cls, config):
        inp = GaussianExternalInput.from_config(config)
        return cls(inp, config['input'], config['options'], config['save'])

    def __init__(self, inp, xtbfilename, options, save):
        super().__init__(inp)
        #
        if options is None:
            options = "--wbo "
        self._options = options
        self._save = save
        self.input = inp.inputfile

    def _write_general_inputs(self):
        pass

    def set_options(self, options, save):
        self._save = save
        if options is None:
            return
        self._options = options

    def _get_command(self, options):
        return self._command % (self.executable, self.input, self.chg, self._options + options)

    def _handle_xcontrol(self):
        if self._save is True:
            return
        if os.path.isfile("xcontrol"):
           os.remove("xcontrol")

    def _run_interface(self, command):
        self._handle_xcontrol()
        self.run_interface(command, self.name)

    def _run_energy(self):
        command = self._get_command(" --sp --copy > output_energy ")
        self._run_interface(command)
        self.logger.write(get_gaussian_wbo_txt(self.inp_file.atomids, 'wbo'))
        return (self._read_xtb_energy_and_dipole("output_energy"),
                None, None)

    def _run_gradient(self):
        command = self._get_command(" --grad --copy > output_gradient ")
        self._run_interface(command)
        self.logger.write(get_gaussian_wbo_txt(self.inp_file.atomids, 'wbo'))
        output = (self._read_xtb_energy_and_dipole("output_gradient"),
                self._read_xtb_gradient("gradient"), None)
        self.clean_up()
        return output

    def _run_frequency(self):
        e_and_dip, grad, _ = self._run_gradient()
        command = self._get_command(" --hess --copy > output_freq")
        self._run_interface(command)
        return (e_and_dip,
                grad,
                self._read_xtb_hessian("hessian"))

    def clean_up(self):
        os.rename("gradient", "grad_old")
        return

    def _read_xtb_energy_and_dipole(self, filename):
        with open(filename, 'r') as fh:
            for line in fh:
                if line.startswith('molecular dipole:'):
                    dipole = _parse_diple(fh)
                if 'TOTAL ENERGY' in line:
                    energy = float(line.split()[3])
                    return energy, dipole

    def _read_xtb_gradient(self, filename):
        with open(filename, 'r') as fh:
            itr = iter(fh)
            for _ in range(self.natoms+2):
                next(itr)
            return np.array([[float(val) for val in next(itr).split()]
                              for _ in range(self.natoms)])

    def _read_xtb_hessian(self, filename):
        with open(filename, 'r') as fh:
            itr = iter(fh)
            next(itr)
            return np.array([float(entry) 
                             for line in itr 
                             for entry in line.split()])


def iformat(num):
    return str(num).center(6)


def get_header(start, end):
    first =  "     Atom"
    second = "     ----"
    for i in range(start+1, end+1):
        first += " " + iformat(i) + " "
        second += " ------ "
    return first + "\n" +  second + "\n"


def get_wbo_line(atom, wbo, idx, istart, end):
    line = str(idx+1)
    line = " "*(4-len(line)) + line + '.  ' + atom + " "*(2-len(atom))
    for i in range(istart, end):
        line += "%7.4f " % wbo[idx, i]
    return line + '\n'


def get_block(atomids, wbo, istart, end):
    txt = get_header(istart, end) 
    for i, atom in enumerate(atomids):
        txt += get_wbo_line(atom, wbo, i, istart, end)
    return txt + "\n"

    
def get_gaussian_wbo_txt(atomids, filename):
    txt = """
 Wiberg bond index matrix in the NAO basis:

 """
    natoms = len(atomids)
    wbo = parse_wbo(natoms, filename)
    istart = 0
    while (istart < natoms):
        end = istart + 9
        if end >= natoms:
            end = natoms
        txt += get_block(atomids, wbo, istart, end)
        istart = end
    return txt


def parse_wbo(natoms, filename):
    wbo = np.zeros((natoms, natoms))
    with open(filename, 'r') as fh:
        for line in fh:
            i, j, value = line.split()
            i, j, value = int(i)-1, int(j)-1, float(value)
            wbo[i,j] = value
            wbo[j,i] = value
    return wbo
