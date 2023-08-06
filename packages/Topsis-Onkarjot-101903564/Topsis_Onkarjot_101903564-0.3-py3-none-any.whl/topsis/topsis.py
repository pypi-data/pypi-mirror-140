from fileinput import filename
import pandas as pd
import numpy as np
import sys
import math
import logging


def get_topsis_result():
    logging.basicConfig(filename="logfile.log",format='%(asctime)s %(message)s',filemode='w')

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)


    n=len(sys.argv)
    if n!=4:
        logger.error("incorect no of argument")
        sys.exit()


    filename=sys.argv[1]
    try:
        f=open(filename,'r')
    except IndexError:
        logger.error("file not found")
        sys.exit()

    df=pd.read_csv(f)

    if df.shape[1]<3:
        logger.error("less than 3 column not possible")
        sys.exit()


    result=df
    df=df.iloc[:,1:]

    weights= (sys.argv[2]).split(",")
    weights = np.asarray(weights, dtype='float64')


    impact= (sys.argv[3]).split(",")

    if len(weights)!=len(impact):
        logger.error("size of arguments is different")
        sys.exit()
    elif len(weights)!=df.shape[1]:
        logger.error("size of arguments is different")
        sys.exit()

    vp=[]
    vn=[]
    i=0
    for column in df:
        sqrt_sum=math.sqrt(df[column].pow(2).sum())
        df[column]=df[column]/sqrt_sum
        df[column]=df[column]*weights[i]
    if(impact[i]=="+"):
        vp.append(df[column].max())
        vn.append(df[column].min())
    else:
        vn.append(df[column].max())
        vp.append(df[column].min())
    i+=1



    vp = pd.DataFrame(vp).T
    vn = pd.DataFrame(vn).T


    sp=df.values-vp.values
    sp=pd.DataFrame(sp)
    sp=sp.pow(2)
    sp["sum"] = sp.sum(axis=1)


    sn=df.values-vn.values
    sn=pd.DataFrame(sn)
    sn=sn.pow(2)
    sn["sum"] = sn.sum(axis=1)

    p=sn["sum"]/(sp["sum"]+sn["sum"])

    result["Topsis Score"]=p

    result["Rank"] = result["Topsis Score"].rank()


    result.to_csv("101903564-output.csv")

# if __name__=='__main__':
   
#    main()