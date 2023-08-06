'''
Author: BDFD
Date: 2022-02-24 15:23:11
LastEditTime: 2022-02-25 12:17:33
LastEditors: BDFD
Description: 
FilePath: \5.2-PyPi-WES_Calculation\WES_Calculation\gumbel.py
'''
import numpy as np;
import statistics;
# import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

def count(x,y,z):
    result = x*y*z+5
    return print(x,y,z,result)

def gumbel_i1(i1,To,Tt,Tti,Tmat,Tmit,Tr):
    if i1==1:
        yo=-np.log(np.log(np.array(To)/(np.array(To)-1))) # emperical y of observed data
        yTt=-np.log(np.log(Tt/(Tt-1)))
        yTti=-np.log(np.log(np.array(Tti)/(np.array(Tti)-1)))
        yTmat=-np.log(np.log(np.array(Tmat)/(np.array(Tmat)-1)))
        yTmit=-np.log(np.log(np.array(Tmit)/(np.array(Tmit)-1)))
        yr=-np.log(np.log(np.array(Tr)/(np.array(Tr)-1))) # range of y for plotting   
    if i1==2:
        yo=np.log(np.log(np.array(To)))
        yTt=np.log(np.log(Tt)) 
        yTti=np.log(np.log(np.array(Tti)))
        yTmat=np.log(np.log(np.array(Tmat)))
        yTmit=np.log(np.log(np.array(Tmit)))
        yr=np.log(np.log(np.array(Tr))) # range of y for plotting
    return yo,yTt,yTti,yTmat,yTmit,yr

def gumbel_i3(i3,n,datao):
    if i3 == 1:
        a = 0
    if i3 == 2:
        a = 0.3175
    if i3 == 3:
        a = 0.44
    To = [0 for j in range(n)]
    To[0] = (n+1-2*a)/(1-a)
    for i in range(1,n-1):
        if datao[i]!=datao[i+1]:
            To[i]=(1+n-2*a)/(1+i-a)
        else:
            To[i]=(1+n-2*a)/(1+i+1-a)
        if datao[i]==datao[i-1]:
            To[i-1]=To[i]
    To[n-1]=(1+n-2*a)/(n-a)
    if datao[n-1]==datao[n-2]:
        To[n-2]=To[n-1]  
    return To

def gumbel(result, test2, test3, i1, i2, i3):
    res = result
    print('res is ', res,'and type is ', type(res))
    unitt = test2
    print('unitt is ', unitt,'and type is ', type(unitt))
    unitx = test3
    print('unitx is ', unitx,'and type is ', type(unitx))
    datao = list(map(float,res))
    datao = sorted(datao, reverse=True)
    print('datao is ', datao,'and type is ', type(datao))
    Tt=[2,5,10,20,25,50,100,200] # Typical return periods used in the output report  
    Tti=[1.005,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,500] # Return periods for plotting
    Tmat=[1.005,2,5,10,50,100,200] # major ticks (Note:Tmat + Tmit must = Tti.)
    Tmit=[3,4,20,30,40,60,70,80,90,500] # minor ticks (Note:Tmat + Tmit must = Tti.)
    zp=1.645 # Quantile of standard normal distribution used for confidence interval (By default, 1.645 for 90% confidence limit)
    nbin=20 # number of bins in histogram
    n=len(datao) # number of the observed data, or record length
    print(n)
    meanx = np.average(datao)
    print(meanx)
    sdx=statistics.stdev(datao) # standard deviation of X data series
    print(sdx)
    Csx=n*sum((np.array(datao)-meanx)**3)/(n-1)/(n-2)/sdx**3 
    print(Csx)
    gi3result = gumbel_i3(i3,n,datao)
    To = gi3result
    Foo = 1-1/np.array(To)
    print(Foo)
    o,bedge=np.histogram(datao,bins=nbin) # histogram
    F1bc=[0 for j in range(nbin)] # probability of each bin in Theoretical Distribution 1
    bc=[0 for j in range(nbin)] # bin centers
    Tt=np.array(Tt)
    Tti[0]=min(Tti[0],To[n-1])
    Tti[len(Tti)-1]=max(Tti[len(Tti)-1],To[0])
    Tmat[0]=Tti[0]
    Tr=[Tti[0],Tti[len(Tti)-1]] # range of return periods for plotting
    gi1result = gumbel_i1(i1,To,Tt,Tti,Tmat,Tmit,Tr)
    yo = gi1result[0]
    yTt = gi1result[1]
    yTti = gi1result[2]
    yTmat = gi1result[3]
    yTmit = gi1result[4]
    yr = gi1result[5]
    print('yo is',yo,'yTt is',yTt,'yTti is', yTti,'yTmat is', yTmat,'yTmit is', yTmit,'yr is', yr)
    # yo,yTt,yTti,yTmat,yTmit,yr
    return 1
