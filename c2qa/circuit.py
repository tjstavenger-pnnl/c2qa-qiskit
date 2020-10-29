# from c2qa.operators import CVOperators
from c2qa.qumoderegister import QumodeRegister
import numpy
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.extensions import UnitaryGate
from strawberryfields.backends.fockbackend import ops

class CVCircuit(QuantumCircuit):
    def __init__(self, qmr: QumodeRegister, qr: QuantumRegister, cr: ClassicalRegister, name: str = None):
        super().__init__(qmr.qreg, qr, cr, name=name)

        self.qmr = qmr
        self.qr = qr
        self.cr = cr

        # self.ops = CVOperators(self.qmr)

    def cv_initialize(self, fock_states):
        """ Initialize qumodes to the given fock_states. """
        for qumode, n in enumerate(fock_states):
            if n >= self.qmr.cutoff:
                raise ValueError("The parameter n should be lower than the cutoff")

            vector = numpy.zeros((self.qmr.cutoff,))
            vector[n] = 1

            super().initialize(vector, self.qmr[qumode])

    def cv_conditional(self, name, op_a, op_b):
        """ Make two operators conditional (i.e., controlled by qubit in either the 0 or 1 state) """
        sub_qmr = QumodeRegister(self.qmr.num_qumodes, self.qmr.num_qubits_per_mode)
        sub_qr = QuantumRegister(1)
        sub_circ = QuantumCircuit(sub_qmr.qreg, sub_qr, name=name)
        sub_circ.append(UnitaryGate(op_a).control(num_ctrl_qubits=1, ctrl_state=0), [sub_qr[0]] + sub_qmr[0])
        sub_circ.append(UnitaryGate(op_b).control(num_ctrl_qubits=1, ctrl_state=1), [sub_qr[0]] + sub_qmr[1])

        return sub_circ.to_instruction()

    def cv_bs(self, theta, qumode_a, qumode_b, phi = 0.0):
        r"""
        Beamsplitter gate using Strawberry Fields FockBackend operator.

        .. math::
            B(\theta,\phi) = \exp\left(\theta (e^{i \phi} a_1 a_2^\dagger -e^{-i \phi} a_1^\dagger a_2) \right)

        Args:
            theta (float): Transmittivity angle :math:`\theta`. The transmission amplitude of
                the beamsplitter is :math:`t = \cos(\theta)`.
                The value :math:`\theta=\pi/4` gives the 50-50 beamsplitter (default).
            phi (float): Phase angle :math:`\phi`. The reflection amplitude of the beamsplitter
                is :math:`r = e^{i\phi}\sin(\theta)`.
                The value :math:`\phi = \pi/2` gives the symmetric beamsplitter.
        """
        # operator = self.ops.bs(phi)
        operator = ops.beamsplitter(theta, phi, self.qmr.cutoff)

        self.unitary(obj=operator, qubits=qumode_a + qumode_b, label='BS')

    def cv_d(self, r, qumode, phi = 0.0):
        r"""
        Phase space displacement gate using Strawberry Fields FockBackend operator.

        .. math::
            D(\alpha) = \exp(\alpha a^\dagger -\alpha^* a) = \exp\left(-i\sqrt{2}(\re(\alpha) \hat{p} -\im(\alpha) \hat{x})/\sqrt{\hbar}\right)

        where :math:`\alpha = r e^{i\phi}` has magnitude :math:`r\geq 0` and phase :math:`\phi`.

        The gate is parameterized so that a user can specify a single complex number :math:`a=\alpha`
        or use the polar form :math:`a = r, \phi` and still get the same result.

        Args:
            r (float): displacement magnitude :math:`|\alpha|`
            phi (float): displacement angle :math:`\phi`
        """
        # operator = self.ops.d(alpha)
        operator = ops.displacement(r, phi, self.qmr.cutoff)

        self.unitary(obj=operator, qubits=qumode, label='D')

    def cv_cnd_d(self, alpha, beta, ctrl, qumode_a, qumode_b):
        # self.append(self.cv_conditional('Dc', self.ops.d(alpha), self.ops.d(beta)), [ctrl] + qumode_a + qumode_b)
        print("hello")

    def cv_r(self, theta, qumode):
        r"""
        Rotation gate using Strawberry Fields FockBackend operator.

        .. math::
            R(\theta) = e^{i \theta a^\dagger a}

        Args:
            theta (float): rotation angle :math:`\theta`.
        """
        # operator = self.ops.r(phi)
        operator = ops.phase(theta, self.qmr.cutoff)

        self.unitary(obj=operator, qubits=qumode, label='R')

    def cv_s(self, r, qumode, phi = 0.0):
        r"""
        Phase space squeezing gate using Strawberry Fields FockBackend operator.

        .. math::
            S(z) = \exp\left(\frac{1}{2}(z^* a^2 -z {a^\dagger}^2)\right)

        where :math:`z = r e^{i\phi}`.

        Args:
            r (float): squeezing amount
            phi (float): squeezing phase angle :math:`\phi`
        """
        # operator = self.ops.s(z)
        operator = ops.squeezing(r, phi, self.qmr.cutoff)

        self.unitary(obj=operator, qubits=qumode, label='S')

    def cv_cnd_s(self, z_a, z_b, ctrl, qumode_a, qumode_b):
        # self.append(self.cv_conditional('Sc', self.ops.s(z_a), self.ops.s(z_b)), [ctrl] + qumode_a + qumode_b)
        print("hello")

    def cv_s2(self, r, qumode_a, qumode_b, phi = 0.0):
        r"""
        Two-mode squeezing gate using Strawberry Fields FockBackend operator.

        .. math::
        S_2(z) = \exp\left(z a_1^\dagger a_2^\dagger - z^* a_1 a_2 \right) = \exp\left(r (e^{i\phi} a_1^\dagger a_2^\dagger e^{-i\phi} a_1 a_2 ) \right)

        where :math:`z = r e^{i\phi}`.

        Args:
            r (float): squeezing amount
            phi (float): squeezing phase angle :math:`\phi`
        """
        # operator = self.ops.s2(z)
        operator = ops.two_mode_squeeze(r, phi, self.qmr.cutoff)

        self.unitary(obj=operator, qubits=qumode_a + qumode_b, label='S2')
