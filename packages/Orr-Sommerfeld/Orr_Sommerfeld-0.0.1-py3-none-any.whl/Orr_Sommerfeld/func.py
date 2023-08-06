import math
import numpy as np
import scipy as sy
import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline
from pylab import *
from numpy import *
import cmath
import matplotlib.colors
from scipy.optimize import curve_fit

 
def run_print():
	return "Successful!"

def cheb(N):
    """
    N=numero de nodos
    genera la matriz de chebychev base 
    """
	if N==0: 
		D = 0.; x = 1.
	else:
		n = arange(0,N+1) # genera el vector con paso 1, de 0 hasta N+1
		x = cos(pi*n/N).reshape(N+1,1) 
		c = (hstack(( [2.], ones(N-1), [2.]))*(-1)**n).reshape(N+1,1) # reshape(N+1,1) me transpone el vector
		X = tile(x,(1,N+1)) #genera la matriz donde la fila i es el elemento i del vector
		dX = X - X.T
		D = dot(c,1./c.T)/(dX+eye(N+1)) #poner dot(c,1./c.T) es lo mismo que  c*(1/c).T (la funcion dot multiplica array)
		D -= diag(sum(D.T,axis=0))
	return D, x.reshape(N+1)
	
def Dmat(N):
    """
    N= numero de nodos
    genera las matrices de chebychev necesarias para resolver Orr_Sommerfeld
    Calcula D4 utilizando la teoria de Trefethen
    """
    D,y = cheb(N)
    D2=dot(D,D)
    y2=y*y
    s = (hstack(( [0.],1/(1-y2[1:-1]) , [0.])))
    s=diag(s)
    D4=dot(D2,D2)
    D4=dot((dot(diag(1-y2),D4)-8*dot(diag(y),dot(D2,D))-12*D2),s)
    D=D[1:-1,1:-1] # chequear que no cambie nada agregar esto aca
    D2=D2[1:-1,1:-1]
    D4=D4[1:-1,1:-1]
    
    return D,D2,D4

def Poiseuille(N):
    D,y = cheb(N)
    D2=dot(D,D)
    y2=y*y
    U=1-y2
    U=U.reshape(N+1,1)
    y=y.reshape(N+1,1)
    U1=dot(D,U)
    U2=dot(D2,U)
    U=U[1:-1]; U1=U1[1:-1] ;U2=U2[1:-1];
    return U,U1,U2
 
def Couette(N):
    D,y = cheb(N)
    D2=dot(D,D)
    U=y
    U=U.reshape(N+1,1)
    y=y.reshape(N+1,1)
    U1=dot(D,U)
    U2=np.zeros(N+1)
    U=U[1:-1]; U1=U1[1:-1] ;U2=U2[1:-1];
    return U,U1,U2
       	
def Flow(N,Np):
    """

    Np=0 Poiseuille flow;Np=1 Couette flow;Np=2 Boundary layer ;Np=3 Jet flow
    """	
    if Np==0:
        U,U1,U2=Poiseuille(N)
    if Np==1:
        U,U1,U2=Couette(N)
    if Np==2:
        U,U1,U2=Boundary_Layer_Flow(N)
    else:
        U,U1,U2=Jet_Flow(N)
    return U,U1,U2	

def Orr_Sommerfeld_temporal(N,R,alp,b,n,Np):
    """
    N= numero de nodos
    R= Numero de Reynolds
    alp= longitud de onda en x
    b= longitud de onda en y
    n= modo a evaluar
    Np= perfil a evaluar
    #Np=0 Poiseuille flow;Np=1 Couette flow;Np=2 Boundary layer ;Np=3 Jet flow
    Calcula los el autovalores (omega) y los autovectores para el problema de Orr_Sommerfeld temporal
    """
    D,D2,D4=Dmat(N)
    U,U1,U2=flow(N,Np)

    I=eye(N-1)
    k2=alp*alp+b*b
    A = -(D4-2.*k2*D2+k2*k2*I)/(R) - 1j*alp*U2*I + 1j*alp*dot(U*I,D2)-1j*alp*k2*U*I 
    B = 1j*alp*(D2-k2*I)
    H=dot(inv(B),A)
    lam, V = eig(H)
    ii = argsort(-lam.imag) 
    lam = lam[ii]
    V = V[:,ii]
    
    Q=-k2*I+D2
    p= -2j*alp*dot(inv(Q),dot(U1*I,V[:,n].reshape(N-1,1)))
    T=Q/R+1j*lam[n]*I-1j*alp*U*I
    u=dot( inv(T) , 1j*alp*p+dot(U1*I,V[:,n].reshape(N-1,1)) )
    w= 1j*b*dot(inv(T),p)
    v=V[:,n].reshape(N-1,1)
    return  lam,u,v,w,p
def Orr_Sommerfeld_Espacial(N,R,w,b,Np) :
    """
    N= numero de nodos
    R= Numero de Reynolds
    omega= frecuencia oscilacion 
    b= longitud de onda en y
    Np= perfil a evaluar
      Calcula los el autovalores (alpha) y los autovectores para el problema de Orr_Sommerfeld espacial  
    """
    D,D2,D4=Dmat(N)
    U,U1,U2=flow(N,Np) #perfil(N) #generico 
    d,_=cheb(N)# va a ser algo asi 
    D3=np.dot(d,np.dot(d,d))
    D3=D3[1:-1,1:-1]
    
    k2=alp*alp+b*b
    b2=b*b
    b3=b*b*b
    b4=b*b*b*b
    I=eye(N-1)
    O=np.zeros((N-1, N-1))
    
    R2=D2*4/R+2j*dot(U*I,D)
    
    R1=-2j*w*D-D3*4/R+4*(b2/R)*D-1j*dot(U*I,D2)+ (1j*b2)*U*I+1j*U2*I
    
    R0=1j*w*D2-1j*(w*b2)*I+D4/R-2*(b2)/R*D2+(b4)/R*I
    T1=2*D/R+1j*U*I
    T0=-1j*w*I-D2/R+b2/R*I
    S=1j*b*U1*I
    R2=np.array(R2);R1=np.array(R1);R0=np.array(R0);
    T0=np.array(T0);T0=np.array(T0);S=np.array(S);
    F1=np.concatenate(([-R1,-R0,O]), axis=1) # con esto creo las "Filas" 
    F2=np.concatenate(([I,O,O]), axis=1)
    F3=np.concatenate(([O,-S,-T0]), axis=1)
    
    #A=[[-R1,-R0,O],[I,O,O],[O,-S,-T0]]# 
    A=np.concatenate(([F1, F2,F3]), axis=0)
    
    F4=np.concatenate(([R2,O,O]), axis=1)
    F5=np.concatenate(([O,I,O]), axis=1)
    F6=np.concatenate(([O,O,T1]), axis=1)
    
    #B=[[R2,O,O],[O,I,O],[O,O,T1]]
    B=np.concatenate(([F4, F5,F6]), axis=0)
    
    #A = -(D4-2.*k2*D2+k2*k2*I)/(R) - 1j*alp*U2*I + 1j*alp*dot(U*I,D2)-1j*alp*k2*U*I #- 1j*alp*U2*I
    #B = 1j*alp*(D2-k2*I)
    
    
    H=dot(inv(B),A)
    lam, V = eig(H)
    ii = argsort(-1/lam.imag) 
    #ii = argsort(((lam.imag)**2+(lam.real)**2))  # sort eigenvalues and -vectors
    lam = lam[ii]
    V = V[:,ii]
    
    
    return lam,V

 
 
def normalizacion(u,v,w,p):
    """
    u=perturbacion en x
    v=perturbacion en y
    w=perturbacion en z
    p=perturbacion de presion
    """
    ur=u.real
    ui=u.imag
    norm= ur*ur+ui*ui
    i=np.where(abs(norm) == np.max(norm))
    ci=1/(ur[i]+ui[i]**2/ur[i])
    c=ci-1j*(ci*ui[i]/ur[i])    
    u=c*u
    v=c*v
    w=c*w
    p=c*p
    return u,v,w,p    
	
def stability_map(N,b,n_R,n_alp,Np):
    """
    N= numero de nodos
    b= longitud de onda en z
    n_R= discretización en R
    n_alp= discretización en alpha
    calcula el mapa de establidad 
    """
    tspan = (1000,10000)
    index_R= np.linspace(*tspan, n_R)
    index_alp=np.linspace(0.2,2,n_alp)
    index_R= np.array(index_R)
    index_alp =np.array(index_alp)
    
    w0 =np.empty((index_R.size,index_alp.size))
    w0=np.array(w0)
    
    stability_y=[]
    stability_x=[]
    X, Y = np.mgrid[1000:10000:complex(0, n_R), 0.2:2:complex(0, n_alp)]
    for i in range(index_R.size):
        for j in range(index_alp.size):
            lam_i,_,_,_,_=Orr_Sommerfeld_temporal(N,X[i][j],Y[i][j],b,0,Np)
            w0[i][j]=((lam_i[0]).imag)
            if -1e-4<(lam_i[0]).imag<0:
                stability_y=np.append(stability_y,[Y[i][j]],axis=0)
                stability_x=np.append(stability_x,[X[i][j]],axis=0)
    return w0,X,Y,stability_x,stability_y
            
	
