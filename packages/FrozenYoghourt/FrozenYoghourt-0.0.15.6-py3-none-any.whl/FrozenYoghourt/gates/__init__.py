from FrozenYoghourt import *
from FrozenYoghourt.mode import *
from FrozenYoghourt.maths import *

def ID():
    if Mode.representation == 'numpy':
        return np.array([[1, 0], [0, 1]])
    else:
        return Matrix([[1, 0], [0, 1]])

def X():
    if Mode.representation == 'numpy':
        return np.array([[0, 1], [1, 0]])
    else:
        return Matrix([[0, 1], [1, 0]])

def Y():
    if Mode.representation == 'numpy':
        return np.array([[0, -1j], [1j, 0]])
    else:
        return Matrix([[0, -I], [I, 0]])

def Z():
    if Mode.representation == 'numpy':
        return np.array([[1, 0], [0, -1]])
    else:
        return Matrix([[1, 0], [0, -1]])
    
def pauli(val, mul = 1):
    
    """
    Return a Pauli matrix or tensor product of matrices
    
    Parameter
    ---------
    val: int, str, list
        Value or list of values of matrices in either integer (0, 1, 2, 3)
        or string ('i', 'x', 'y', 'z') form. If a list is given, compute 
        the tensor product of the pauli's in the list from left to right.
    
    mul: int
        Multiplicity of value or list of values
        
    Returns
    -------
    pauli_mat: np.ndarray, sympy.Matrices
        Pauli matrix or tensor product of matrices
        
    """
    
    option = type(val)
    if option == list:
        option = type(val[0])
    
    if option == int:
        num = {0: ID(), 1: X(), 2: Y(), 3:Z()}
        if type(val) == int:
            pauli_mat = tp(num[val], mul = mul)
        else:
            pauli_list = [num[elem] for elem in val]
            pauli_mat = tp(*pauli_list, mul = mul)
      
    elif option == str:
        text = {'i': ID(), 'x': X(), 'y': Y(), 'z': Z()}
        if type(val) == str:
            pauli_mat = tp(text[val], mul = mul)
        else:
            pauli_list = [text[elem] for elem in val]
            pauli_mat = tp(*pauli_list, mul = mul)
            
    return pauli_mat

def H():
    if Mode.representation == 'numpy':
        return 1 / np.sqrt(2) * np.array([[1, 1], [1, -1]])
    else:
        return 1 / sqrt(2) * Matrix([[1, 1], [1, -1]])

def Rx(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.cos(theta / 2), -1j * np.sin(theta / 2)],
                         [-1j * np.sin(theta / 2), np.cos(theta / 2)]])
    else:
        return Matrix([[cos(theta / 2), -I * sin(theta / 2)],
                       [-I * sin(theta / 2), cos(theta / 2)]])

def Ry(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.cos(theta / 2), -np.sin(theta / 2)],
                         [np.sin(theta / 2), np.cos(theta / 2)]])
    else:
        return Matrix([[cos(theta / 2), -sin(theta / 2)],
                       [sin(theta / 2), cos(theta / 2)]])

def Rz(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.exp(-1j * theta / 2), 0],
                         [0, np.exp(1j * theta / 2)]])
    else:
        return Matrix([[exp(-I * theta / 2), 0],
                       [0, exp(I * theta / 2)]])

def Phase(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[1, 0], [0, np.exp(1j*theta)]])
    else:
        return Matrix([[1, 0], [0, exp(I*theta)]])

def u2(angles:list = None, unimodular = False, index = ''):
    
    if type(angles) == bool:
        unimodular = angles
        angles = None
    
    if Mode.representation == 'numpy':
        if unimodular: 
            return to_su(random_unitary(2).data)
        else: 
            return random_unitary(2).data
    else:
        if angles is None:
            theta, phi, lam = symbols(f'theta_{index}, phi_{index}, lambda_{index}', real = True)
        else:
            theta, phi, lam = angles
        if unimodular:
            return Matrix([[exp(I*phi)*cos(theta / 2), -exp(I * -lam) * sin(theta / 2)],
                                          [exp(I * lam) * sin(theta / 2), exp(I * (-phi)) * cos(theta / 2)]])
        else:
            return Matrix([[cos(theta / 2), -exp(I * lam) * sin(theta / 2)],
                                           [exp(I * phi) * sin(theta / 2), exp(I * (phi + lam)) * cos(theta / 2)]])

def CX():
    if Mode.representation == 'numpy':
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1],
                         [0, 0, 1, 0]])
    else:
        return Matrix([[1, 0, 0, 0],
                       [0, 1, 0, 0],
                       [0, 0, 0, 1],
                       [0, 0, 1, 0]])

def CU(control, target, U, no_qubits = 2):
    """
    Manually build the unitary matrix for non-adjacent CU gates
    Parameters:
    -----------
    control: int
        Index of the control qubit (1st qubit is index 0)
    target: int
        Index of the target qubit (1st qubit is index 0)
    U: ndarray
        Target unitary matrix
    edian: bool (True: qiskit convention)
        Qubits order convention
    no_qubits: int
        Number of qubits in the circuit
    Returns:
    --------
    cx_out:
        Unitary matrix for CU gate
    """

    left = [Id()] * no_qubits
    right = [Id()] * no_qubits

    if Mode.representation == 'numpy':

        left[control] = np.array([[1, 0], [0, 0]])
        right[control] = np.array([[0, 0], [0, 1]])

    else:

        left[control] = Matrix([[1, 0], [0, 0]])
        right[control] = Matrix([[0, 0], [0, 1]])

    right[target] = U

    cu_out = tp(*left) + tp(*right)

    return cu_out

def Swap():
    if Mode.representation == 'numpy':
        return np.array([[1, 0, 0, 0],
                         [0, 0, 1, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1]])
    else:
        return Matrix([[1, 0, 0, 0],
                       [0, 0, 1, 0],
                       [0, 1, 0, 0],
                       [0, 0, 0, 1]])

def SQiSW():
    if Mode.representation == 'numpy':
        return np.array([[1, 0, 0, 0],
                         [0, 1 / np.sqrt(2), 1j / np.sqrt(2), 0],
                         [0, 1j / np.sqrt(2), 1 / np.sqrt(2), 0],
                         [0, 0, 0, 1]])
    else:
        return Matrix([[1, 0, 0, 0],
                       [0, 1 / sqrt(2), I / sqrt(2), 0],
                       [0, I / sqrt(2), 1 / sqrt(2), 0],
                       [0, 0, 0, 1]])

def Gamma():
    if Mode.representation == 'numpy':
        return 1/2 * np.array([[1, -1, 1, -1], 
                               [1, 1, -1, -1], 
                               [1, -1, -1, 1], 
                               [1, 1, 1, 1]])
    else:
        return 1/2 * Matrix([[1, -1, 1, -1], 
                             [1, 1, -1, -1], 
                             [1, -1, -1, 1], 
                             [1, 1, 1, 1]])

def Magic():
    if Mode.representation == 'numpy':
        return 1 / np.sqrt(2) * np.array([[1, 1j, 0, 0],
                                          [0, 0, 1j, 1],
                                          [0, 0, 1j, -1],
                                          [1, -1j, 0, 0]])
    else:
        return 1 / sqrt(2) * Matrix([[1, I, 0, 0],
                                     [0, 0, I, 1],
                                     [0, 0, I, -1],
                                     [1, -I, 0, 0]])

def Rxx(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.cos(theta / 2), 0, 0, -1j * np.sin(theta / 2)],
                         [0, np.cos(theta / 2), -1j * np.sin(theta / 2), 0],
                         [0, -1j * np.sin(theta / 2), np.cos(theta / 2), 0],
                         [-1j * np.sin(theta / 2), 0, 0, np.cos(theta / 2)]])
    else:
        return Matrix([[cos(theta / 2), 0, 0, -I * sin(theta / 2)],
                       [0, cos(theta / 2), -I * sin(theta / 2), 0],
                       [0, -I * sin(theta / 2), cos(theta / 2), 0],
                       [-I * sin(theta / 2), 0, 0, cos(theta / 2)]])

def Ryy(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.cos(theta / 2), 0, 0, 1j * np.sin(theta / 2)],
                         [0, np.cos(theta / 2), -1j * np.sin(theta / 2), 0],
                         [0, -1j * np.sin(theta / 2), np.cos(theta / 2), 0],
                         [1j * np.sin(theta / 2), 0, 0, np.cos(theta / 2)]])
    else:
        return Matrix([[cos(theta / 2), 0, 0, I * sin(theta / 2)],
                       [0, cos(theta / 2), -I * sin(theta / 2), 0],
                       [0, -I * sin(theta / 2), cos(theta / 2), 0],
                       [I * sin(theta / 2), 0, 0, cos(theta / 2)]])

def Rzz(theta:float):
    if Mode.representation == 'numpy':
        return np.array([[np.exp(-1j * theta / 2), 0, 0, 0],
                         [0, np.exp(1j * theta / 2), 0, 0],
                         [0, 0, np.exp(1j * theta / 2), 0],
                         [0, 0, 0, np.exp(-1j * theta / 2)]])
    else:
        return Matrix([[exp(-I * theta / 2), 0, 0, 0],
                       [0, exp(I * theta / 2), 0, 0],
                       [0, 0, exp(I * theta / 2), 0],
                       [0, 0, 0, exp(-I * theta / 2)]])

def CAN(tx:float, ty:float, tz:float):
    if Mode.representation == 'numpy':
        return np.array([[np.exp(-1j*tz/2)*np.cos((tx-ty)/2), 0, 0, -1j*np.exp(-1j*tz/2)*np.sin((tx-ty)/2)], 
                         [0, np.exp(1j*tz/2)*np.cos((tx+ty)/2), -1j*np.exp(1j*tz/2)*np.sin((tx+ty)/2), 0], 
                         [0, -1j*np.exp(1j*tz/2)*np.sin((tx+ty)/2), np.exp(1j*tz/2)*np.cos((tx+ty)/2), 0], 
                         [-1j*np.exp(-1j*tz/2)*np.sin((tx-ty)/2), 0, 0, np.exp(-1j*tz/2)*np.cos((tx-ty)/2)]])
    else:
        return Matrix([[exp(-I*tz/2)*cos((tx-ty)/2), 0, 0, -I*exp(-I*tz/2)*sin((tx-ty)/2)], 
                       [0, exp(I*tz/2)*cos((tx+ty)/2), -I*exp(I*tz/2)*sin((tx+ty)/2), 0], 
                       [0, -I*exp(I*tz/2)*sin((tx+ty)/2), exp(I*tz/2)*cos((tx+ty)/2), 0], 
                       [-I*exp(-I*tz/2)*sin((tx-ty)/2), 0, 0, exp(-I*tz/2)*cos((tx-ty)/2)]])