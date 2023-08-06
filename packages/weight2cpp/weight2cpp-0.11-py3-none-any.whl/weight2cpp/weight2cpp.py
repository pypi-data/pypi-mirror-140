
import numpy as np

class Predict2Cpp():
    def __init__(self, ):
        self.cpp_array =""

    def getCpp(self, weights: list):

        weights_tmp, maxClm, mdl_shp = [], 0, []
        print(len(weights))

        for cnt, w in enumerate(weights):
            if w.ndim == 1: maxClm = len(w) if maxClm < len(w) else maxClm 
            if w.ndim == 2: mdl_shp.append(len(w))
            if cnt == len(weights)-1: mdl_shp.append(len(w))
            #print(w, w.shape,"d,l,s=", w.ndim, len(w), w.size)

        Layers = int(len(weights)/2 + 1) 
        Rows = maxClm + 2
        Clms = maxClm
        print("model struct=", mdl_shp);
        print("Layers, Rows, Clms=",Layers, Rows, Clms)
        
        weights_tmp = np.zeros(shape=(Layers, Rows,Clms),dtype=np.float32)

        L=0
        for wt in weights:
            if wt.ndim ==2 : 
                L+= 1
                R=0
                for r in range(len(wt)): 
                    for c in range(wt.shape[1]): weights_tmp[L,r,c] = wt[r,c]
            if wt.ndim ==1 : 
                for c in range(wt.shape[0]): weights_tmp[L,r+1,c] = wt[c]

        cpp = ""
        L=0
        print(len(weights_tmp), weights_tmp.shape)
        cpp = "float mdw["+str(Layers)+"]"+"["+str(Rows)+"]"+"["+str(Clms)+"]={" + "\n"
        for wt in weights_tmp:
            L+= 1
            cpp = cpp + "{"
            for r in range(Rows):
                cpp = cpp + "{" 
                for c in range(Clms): cpp = cpp + float(wt[r,c]).hex() + ", " #//= cpp + str(wt[r,c]) + ", "
                cpp = cpp[0:len(cpp)-2]  + "}, \n"
            cpp = cpp[0:len(cpp)-3]  + "}, \n"
        cpp = cpp[0:len(cpp)-3] + "\n}; \n"

        cpp = cpp + "int ln=" + str(Layers) + ";\n"
        cpp = cpp + "int ls[" + str(Layers) + "]=" + str(mdl_shp).replace("[","{").replace("]","}") + ";\n"
        cpp = cpp + "int latf[" + str(Layers) + "]={0,1,0,1,0...}" + "; //Input Activation Function num; latf[0]= input layer \n"

        cpp = cpp + "//int model_struct=" + str(mdl_shp).replace("[","{").replace("]","}") + ";\n"
        cpp = cpp + "//int Layers, Rows, Clms = " + str(Layers) + ", " +str(Rows) + ", " + str(Clms)  + ";\n"

        self.cpp_array = cpp
