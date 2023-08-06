'''
Author: BDFD
Date: 2022-03-01 17:28:34
LastEditTime: 2022-03-01 18:03:20
LastEditors: BDFD
Description: 
FilePath: \5.2-PyPi-WES_Calculation\WES_Calculation\greenampt.py
'''

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter
import numpy as np
from numpy import *
import statistics
import io
import base64


def gumbeltest(result, test2, test3, i1, i2, i3):
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
    meanx=average(datao)
    sdx=statistics.stdev(datao) # standard deviation of X data series
    Csx=n*sum((array(datao)-meanx)**3)/(n-1)/(n-2)/sdx**3 # Skew Coefficient of X data series

    if i3==1:
        a=0 # a: a coefficient in plotting position equation:
    if i3==2:
        a=0.3175
    if i3==3:
        a=0.44

    To=[0 for j in range(n)] # Empirical return periods of observed data
    To[0]=(n+1-2*a)/(1-a)

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

    Foo=1-1/array(To) # Emperical CDF at observed values

    o,bedge=np.histogram(datao,bins=nbin) # histogram
    F1bc=[0 for j in range(nbin)] # probability of each bin in Theoretical Distribution 1
    bc=[0 for j in range(nbin)] # bin centers

    # 2) Various y (reduced variate) values
    Tt=array(Tt)

    Tti[0]=min(Tti[0],To[n-1])
    Tti[len(Tti)-1]=max(Tti[len(Tti)-1],To[0])
    Tmat[0]=Tti[0]

    Tr=[Tti[0],Tti[len(Tti)-1]] # range of return periods for plotting

    if i1==1:
        yo=-np.log(np.log(array(To)/(array(To)-1))) # emperical y of observed data
        yTt=-np.log(np.log(Tt/(Tt-1)))
        yTti=-np.log(np.log(array(Tti)/(array(Tti)-1)))
        yTmat=-np.log(np.log(array(Tmat)/(array(Tmat)-1)))
        yTmit=-np.log(np.log(array(Tmit)/(array(Tmit)-1)))
        yr=-np.log(np.log(array(Tr)/(array(Tr)-1))) # range of y for plotting   
    if i1==2:
        yo=np.log(np.log(array(To)))
        yTt=np.log(np.log(Tt)) 
        yTti=np.log(np.log(array(Tti)))
        yTmat=np.log(np.log(array(Tmat)))
        yTmit=np.log(np.log(array(Tmit)))
        yr=np.log(np.log(array(Tr))) # range of y for plotting
        
    yTmatl = FixedLocator(yTmat)
    yTmitl = FixedLocator(yTmit)

    PTmat=1/array(Tmat) # Exceedance Probability
    PTmat[0]=round(PTmat[0],5)

    # 3) A limiting distribution with an infinite n
    scale=sdx*sqrt(6)/math.pi
    if i1==1:
        mode=meanx-sdx*0.5772*sqrt(6)/math.pi
    if i1==2:
        mode=meanx+sdx*0.5772*sqrt(6)/math.pi

    xr1=array(yr)*scale+mode # range of x for plotting

    xTt1=yTt*scale+mode # really needed? Can it be read from xr1?

    x1o=(xr1[1]-xr1[0])*(array(yo)-yr[0])/(yr[1]-yr[0])+xr1[0] # theoretical values at To
    cm1=np.corrcoef(datao,x1o) # Correlation matrix between observed data and theoretical values 
    R1=cm1[0,1] # Correlation coefficient between observed data and theoretical values

    #F1o=1/np.exp(np.exp((mode-array(datao))/scale)) # Theoretical CDF at observed values
    if i1==1:
        F1o=1/np.exp(np.exp(-array((yr[0]+(yr[1]-yr[0])*(array(datao)-xr1[0])/(xr1[1]-xr1[0]))))) # Theoretical CDF at observed values
    if i1==2:
        F1o=1-1/np.exp(np.exp(array((yr[0]+(yr[1]-yr[0])*(array(datao)-xr1[0])/(xr1[1]-xr1[0]))))) # Theoretical CDF at observed values
    KS1=max(abs(array(Foo-F1o))) # Kolmogorov-Smirnov Test Statistic

    for i in range(1,nbin+1): 
        F1bc[i-1]=-1/np.exp(np.exp((bedge[i]-mode)/scale))+1/np.exp(np.exp((bedge[i-1]-mode)/scale))
    C21=sum((o-array(F1bc)*n)**2/(array(F1bc)*n)) # Chi-Squared Test Statistic
    if min(array(F1bc)*n)<5:
        print('Warning: Bins need to be regrouped in the Chi-Squared Test.')

    #Var=scale**2*(1.11+0.52*yTt+0.61*yTt**2)/n
    Var=scale**2*((1.1128-0.9066/n)-(0.4574-1.1722/n)*yTt+(0.8046-0.1855/n)*yTt**2)/(n-1) # This is for maxima analysis. Still applicable to the minimum?
    xTt1u=xTt1+zp*sqrt(Var) # 95% confidence limit
    xTt1l=xTt1-zp*sqrt(Var) # 5% confidence limit

    # 4) A distribution with the actual n

    if i1==1:
        Kr=(array(yr)-0.5775/n**(0.66/n))*n**(1.268/n)/1.2811
        xr2=array(Kr)*sdx+meanx
        KTt=(yTt-0.5775/n**(0.66/n))*n**(1.268/n)/1.2811 # really needed?
        xTt2=meanx+KTt*sdx # really needed? Can it be read from xr2?
    if i1==2:
        Kr=(-array(yr)-0.5775/n**(0.66/n))*n**(1.268/n)/1.2811
        xr2=meanx-array(Kr)*sdx # why "-" here?
        KTt=(-yTt-0.5775/n**(0.66/n))*n**(1.268/n)/1.2811 #  
        xTt2=meanx-KTt*sdx # why "-" here?

    xTt2u=xTt2+zp*sqrt(Var) # 95% confidence limit
    xTt2l=xTt2-zp*sqrt(Var) # 5% confidence limit

    x2o=(xr2[1]-xr2[0])*(array(yo)-yr[0])/(yr[1]-yr[0])+xr2[0] # theoretical values at To
    cm2=np.corrcoef(datao,x2o) # Correlation matrix between observed data and theoretical values 
    R2=cm2[0,1] # Correlation coefficient between observed data and theoretical values 

    if i1==1:
        F2o=1/np.exp(np.exp(-array((yr[0]+(yr[1]-yr[0])*(array(datao)-xr2[0])/(xr2[1]-xr2[0]))))) # Theoretical CDF at observed values
    if i1==2:

        F2o=1-1/np.exp(np.exp(array((yr[0]+(yr[1]-yr[0])*(array(datao)-xr2[0])/(xr2[1]-xr2[0]))))) # Theoretical CDF at observed values
    KS2=max(abs(array(Foo-F2o))) # Kolmogorov-Smirnov Test Statistic
    
    data=()
    for i in range(1,len(Tt)+1):
        data+=((str(Tt[i-1]),str(round(xTt1[i-1],2)),str(round(xTt2[i-1],2))),)

    ax=plt.axes()

    ax.xaxis.set_major_locator(yTmatl)
    yTmatf = FixedFormatter(Tmat)
    ax.xaxis.set_major_formatter(yTmatf)

    ax.xaxis.set_minor_locator(yTmitl)
    ax.xaxis.set_minor_formatter(plt.NullFormatter())

    plt.xlabel('Return Period ('+str(unitt)+')')
    plt.ylabel('Value ('+str(unitx)+')')
    plt.plot(yr,xr1,label="Theoretical Gumbel Distribution (Limiting)",color="red",linewidth=2)
    plt.plot(yTt,xTt1u,label="95% Confidence Limits",color="red",linewidth=1.5,linestyle=":")
    plt.plot(yTt,xTt1l,color="red",linewidth=1.5,linestyle=":")
    plt.plot(yr,xr2,label="Theoretical Gumbel Distribution (based on a finite record length)",color="blue",linewidth=2,linestyle="--")
    plt.plot(yTt,xTt2u,label="95% Confidence Limits",color="blue",linewidth=1.5,linestyle=":")
    plt.plot(yTt,xTt2l,color="blue",linewidth=1.5,linestyle=":")
    plt.scatter(yo,datao,c="white",marker="o",s=20,edgecolors="black",label="Observed Data")

    if i1==1:
        plt.scatter(-np.log(np.log(2.3276/(2.3276-1))),meanx,c="red",marker="o",s=20,edgecolors="red",label="Mean of Observed Data")# (return period = 2.33 at the limiting distribution)")

    plt.xlim([yr[0], yr[1]])
    plt.tick_params(labelbottom=True,labelright=True,direction="in")
    plt.grid(color="black",alpha=.8,linewidth=1,linestyle="--")
    ax.tick_params(which="minor", axis="x", direction="in")
    plt.grid(which="minor", axis="x",color="black",alpha=.4,linewidth=1,linestyle="--")

    secax = ax.secondary_xaxis('top')
    secax.set_xlabel('Exceedance Probability')
    secax.xaxis.set_major_locator(yTmatl)
    PTmatl = FixedFormatter(PTmat)
    secax.xaxis.set_major_formatter(PTmatl)
    secax.tick_params(direction="in")

    plt.legend()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close("all")
    return (plot_url,data)