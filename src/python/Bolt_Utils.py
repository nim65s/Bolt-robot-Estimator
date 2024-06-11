import numpy as np
from scipy.spatial.transform import Rotation 

'''
Class with some function used in other objects
'''
class utils():
    def __init__(self):
        pass

    def cross(a,b):
        # returns a ^ b [PINOCCHIO INCLUDES A CROSSPRODUCT]
        return np.array([b[1]*a[2] - b[2]*a[1],
                        b[2]*a[0] - b[0]*a[2],
                        b[0]*a[1] - b[1]*a[0]])

    def normalize(a):
        return a/np.linalg.norm(a)
    
    def MatrixFromVectors(L, n=3):
        # L tuple of numpy vectors
        A = np.stack(L).reshape((-1, n))
        return A
    
    def scalar(a, b) -> float:
        # returns a scalar b
        return np.sum(a*b)

    def RotationMatrix(EulerArray) -> np.ndarray:
        return Rotation.from_euler('zyx', EulerArray).as_matrix()
    
    def rotation(EulerArray, ArrayToRotate) -> np.ndarray:
        R = Rotation.from_euler('xyz', EulerArray).as_matrix()
        return R@ArrayToRotate
    
    def S(x) -> np.ndarray:
        """ Skew-symetric operator """
        sx = np.array([[0,    -x[2],  x[1]],
                       [x[2],   0,   -x[0]],
                       [-x[1], x[0],    0 ]])
        return sx

'''
A class to have a common log for all code
Display logs on flight, or only when PrintLog() is called
'''
class Log():
    def __init__(self, name="", PrintOnFlight=True):
        self.PrintOnFlight = PrintOnFlight
        self.fulllog = "\n\n   ---   beginnig log:: " + name + " --- \n\n"
        if self.PrintOnFlight : print(self.fulllog)

    def LogTheLog(self, log, style="info", ToPrint=True):
        if style=="info":
            log = "  -> " + log
        elif style=="subinfo":
            log = "    ...  " + log
        elif style=="warn":
            log = "  -!- " + log
        elif style=="danger":
            log = "** ! ** " + log
        elif style=="title":
            log = "\n\n***\n\n " + log + "\n\n***\n\n "
        elif style=="subtitle":
            log = " ····> " + log
        if ToPrint and self.PrintOnFlight: print(log)
        self.fulllog  +=  log + "\n"
    def GetLog(self):
        return self.fulllog
    def PrintLog(self):
        print(self.GetLog())

'''
Classes of functions that returns its derivatives
Used to derive trajectory in speed and acceleration
'''
class Sinus():
    def __init__(self, a, w, x=None):
        self.a = a
        self.w = w
        if x is not None :
            self.evaluate(x)
        else:
            return None
    def evaluate(self, x):
        return self.a * np.sin(self.w * x)
    def deriv(self):
        return Cosinus(self.a*self.w, self.w)
    
        
class Cosinus():
    def __init__(self, a, w):
        self.a = a
        self.w = w
    def evaluate(self, x):
        return self.a * np.cos(self.w * x)
    def deriv(self):
        return Sinus(-self.a*self.w, self.w)
    

class Exp():
    def __init__(self, C, w):
        self.C = C
        self.w = w
    def evaluate(self, x):
        return self.C * np.exp(-self.w * x)
    def deriv(self):
        return Exp(-self.C*self.w, self.w)
    
