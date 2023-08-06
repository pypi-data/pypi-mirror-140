if __name__ == "__main__":
    
    import logging
    import pandas as pd
    import numpy as np
    import sys
    
    '''df=pd.read_csv("data.csv")
    data=df.iloc[:,1:]
    names=df.iloc[:,0]
    w=[1,1,2,1,1]
    n=len(data.columns)
    impact=['+','-','+','+','-']'''
    
    
    logging.basicConfig(filename="101903463-log.log",level=logging.DEBUG)
    
    
    if len(sys.argv)>5:
        logging.warning("Wrong number of parameters passed")
        print("Give all 5 parameters")
    elif len(sys.argv)<5:
        logging.warning("Wrong number of parameters passed")
        print("Give all 5 parameters")
        
    else:
        try:
            fname=sys.argv[1]
            if fname!="data.csv":
                logging.warning("Wrong input file")
                print("Input file given is wrong")
            df=pd.read_csv(fname)
            data=df.iloc[:,1:]
            names=df.iloc[:,0]
            n=len(data.columns)
            w=sys.argv[2]
            c1=w.count(",")
            if(c1!=n-1):
                logging.error("Values of weights are not separated by comma")
                print("Separate the values by comma")
            w=list(map(int,w.split(",")))
            
            impact=sys.argv[3]
            c2=impact.count(",")
            if(c1!=n-1):
                logging.error("Values of impacts are not separated by comma")
                print("Separate the values by comma")
            impact=impact.split(",")
            ofile=sys.argv[4]
            
        except FileNotFoundError:
                logging.error("Input file not found")
                print("Input file not found")
        else:
            if len(df.columns)<3:
                logging.warning("Wrong column entries")
                print("Columns should be greater than 3")
                
            for i in range(0,len(data)):
                rv=list(data.iloc[i])
                for j in range(1,len(rv)):
                    try:
                        rv[j]=pd.to_numeric(rv[j])
                    except ValueError:
                        logging.error(f"Value error in input file at {i},{j}")
            if(len(impact)!=n or len(w)!=n):
                logging.error("Number of impacts or weights does not match number of columns")
                print("Number of impacts or weights does not match number of columns")
            for i in impact:
                if(i!='+' and i!='-'):
                    logging.error("Impacts must be + or -")
                    print("Impacts must be + or -")
            
            
            data_norm=data/np.sqrt(np.power(data,2).sum(axis=0))
            data_norm_w=data_norm*w
            sm_n=0
            sm_p=0
            for i in range(0,n):
                if(impact[i]=='-'):
                    negative_ideal=data_norm_w.min()
                    sm_n+=np.sqrt(np.power(data_norm_w-negative_ideal,2).sum(axis=1))
                else:
                    positive_ideal=data_norm_w.max()
                    sm_p+=np.sqrt(np.power(data_norm_w-positive_ideal,2).sum(axis=1))
    
            score=sm_n/(sm_n+sm_p)
    
            df['Score']=score
            df['Rank']=df['Score'].rank(ascending=False)
            df.sort_values("Rank", inplace = True)
            df.to_csv(ofile)
            
            
                    
                    
                
            
                
            
                
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    
    
    data_norm
    
    data_norm_w=data_norm*w
    data_norm_w
    
    sm_n=0
    sm_p=0
    for i in range(0,n):
        if(impact[i]=='-'):
            negative_ideal=data_norm_w.min()
            sm_n+=np.sqrt(np.power(data_norm_w-negative_ideal,2).sum(axis=1))
        else:
            positive_ideal=data_norm_w.max()
            sm_p+=np.sqrt(np.power(data_norm_w-positive_ideal,2).sum(axis=1))
    
    score=sm_n/(sm_n+sm_p)
    
    df['Score']=score
    df['Rank']=df['Score'].rank(ascending=False)
    df.sort_values("Rank", inplace = True)
    
    
    '''
    



