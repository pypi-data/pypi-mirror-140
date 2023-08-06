import numpy as np
import pandas as pd
import sys
filename = sys.argv[1]
ww=sys.argv[2].split(',')
impact = sys.argv[3].split(',')
class topsis:
    a=None #matrix
    w=None #weights
    impact=None #impacts
    columns=None
    rows=None
    normalization=None
    best=[]
    worst=[]
    diw=None
    dib=None
    siw=None
    sib=None
  
    
    

    def _init_(self,a,w,impact):
        #self.a=self.floater(a)
        #self.a=np.array(self.a)
        a=a.astype("float64")
        self.a=a
        self.rows=len(a)
        self.columns=len(a[0])
        #self.w=self.floater(w)
        #self.w=self.w/sum(self.w)
        self.w=w
        self.impact=impact

		
    def maketable(self):
        self.normalization=self.a
        for i in range(self.columns):
            denominator=sum(self.a[:,i]**2)**0.5
            for j in range(self.rows):
                self.normalization[j,i]=((self.a[j,i])/denominator)
        #print(self.normalization)
                
    def multiply_weights(self):
        for i in range(self.rows):
            for j in range(self.columns):
               self.normalization[i,j]=self.normalization[i,j]*self.w[j]
        
    def best_and_worst(self):
        for i in range(self.columns):
            if self.impact[i]=='+':
                self.worst.append(min(self.normalization[:,i]))
                self.best.append(max(self.normalization[:,i]))
            else:
                self.worst.append(max(self.normalization[:,i]))
                self.best.append(min(self.normalization[:,i]))
    def calculations(self):
        self.diw=(self.normalization-self.worst)**2
        self.dib=(self.normalization-self.best)**2
        self.dw=[]
        self.db=[]
        for j in range(self.rows):
            self.dw.append(sum(self.diw[j,:])**0.5)
            self.db.append(sum(self.dib[j,:])**0.5)
		#print self.dw
        self.dw=np.array(self.dw)
        self.db=np.array(self.db)
		#print self.dw
    def performance(self):
        np.seterr(all='ignore')
        self.siw=self.dw/(self.dw+self.db)
        x=0
        m=0
        for i in range(self.rows):
			#print self.siw[i]
            if self.siw[i]>m or m==0:
                m=self.siw[i]
                x=i
        print('Choice',x+1,'is the best')
    def calc(self):
        self.maketable()
        self.multiply_weights()
        self.best_and_worst()
        self.calculations()
        self.performance()

def main(filename,ww,impact):
    dataset=pd.read_csv(filename)
    dataset=dataset.iloc[:,:].values
    weights=[]
    for item in ww:
        weights.append(float(item))
    print(weights)

    print(impact)
    t=topsis()
    t._init_(dataset,weights,impact)
    t.calc()


if __name__ == '__main__':
    main(filename,ww,impact)
