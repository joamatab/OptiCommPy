import numpy as np
from numpy.matlib import repmat
from commpy.utilities import bitarray2dec, dec2bitarray
from numba import njit

def GrayCode(n):
    
    code = []
    
    for i in range(1 << n):
       
        # Generating the decimal
        # values of gray code then using
        # bitset to convert them to binary form
        val = (i ^ (i >> 1))
         
        # Converting to binary string
        s = bin(val)[2::]
        code.append(s.zfill(n))
        
    return code

def GrayMapping(M, constType):
    
    L   = int(np.sqrt(M)-1)
    bitsSymb = int(np.log2(M))
    
    code = GrayCode(bitsSymb)
        
    if constType == 'qam':
        PAM = np.arange(-L, L+1, 2)
        PAM = np.array([PAM])

        # generate complex square M-QAM constellation
        const = repmat(PAM, L+1, 1) + 1j*repmat(np.flip(PAM.T,0), 1, L+1)
        const = const.T
    
        for ind in np.arange(1,L+1,2):
            const[ind] = np.flip(const[ind],0)        
        
    elif constType == 'psk':
        pskPhases = np.arange(0,2*np.pi,2*np.pi/M)
        
        # generate complex M-PSK constellation
        const     = np.exp(1j*pskPhases) 
    
    const    = const.reshape(M,1)
    const_   = np.zeros((M,2),dtype=complex)
    

    for ind in range(0,M):    
        const_[ind,0]   = const[ind,0]   # complex constellation symbol
        const_[ind,1]   =  int(code[ind],2) # mapped bit sequence (as integer decimal)
        
    # sort complex symbols column according to their mapped bit sequence (as integer decimal)                 
    const = const_[const_[:,1].real.argsort()] 
    
    return const

@njit
def minEuclid(symb, const):
    return np.abs(symb - const).argmin()

def modulateGray(bits, M, constType):
       
    bitsSymb = int(np.log2(M))      
    const = GrayMapping(M, constType)
    
    symb    = bits.reshape(-1,bitsSymb).T
    symbInd = bitarray2dec(symb)    

    return const[symbInd,0]

def demodulateGray(symb, M ,constType):
    
    const = GrayMapping(M, constType)
         
    minEuclid_vec = np.vectorize(minEuclid, excluded = [1])        
    index_list = minEuclid_vec(symb, const[:,0])     
    demodBits = dec2bitarray(index_list, int(np.log2(M)))
    
    return demodBits