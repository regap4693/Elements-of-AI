# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 16:18:06 2018

@author: rajes
"""
#!/usr/bin/env python3
import pandas as pd
import math
import numpy as np
import sys

def train_pd_read(filename):
    tr=pd.read_csv(filename, header=None)
    train=[]
    trainimg=[]
    for i in range(0,tr.shape[0]):
        row=tr[0][i].split(' ')    
        train.append(pd.to_numeric(row[1:]))
        trainimg.append(row[0])
    col_x=['outputY']
    for i in range(1,65):
        col_x+=['red'+str(i),'green'+str(i),'blue'+str(i)]
    pd_train=pd.DataFrame(train,columns=col_x)
    print('\n read train in pandas')
   # print(pd_train.head())
   # print(pd_train['outputY'].value_counts())
    return pd_train


def train_dict_read(filename):
    tr=pd.read_csv(filename, header=None)
    row_num=tr.shape[0]
    dict_train={}
    trainimg=[]
    col_x=['outputY']
    for i in range(1,65):
        col_x+=['red'+str(i),'green'+str(i),'blue'+str(i)]

    dict_train={i : {col:0 for col in col_x} for i in range(0,row_num)}
    dict_train0={}
    dict_train90={}
    dict_train180={}
    dict_train270={}
    print('\n read train in dictionary')
    for i in range(0,row_num):
        row=tr[0][i].split(' ')[1:]
        row_spec={}
        for j in range(0,len(col_x)):
            dict_train[i][col_x[j]]=int(row[j])
            row_spec.update({col_x[j]:int(row[j])})
        if row[0]=='0':
        
            dict_train0.update({i:row_spec})
            
        if row[0]=='90':
            dict_train90.update({i:row_spec})
            
        if row[0]=='180':
            dict_train180.update({i:row_spec})
            
        if row[0]=='270':
            dict_train270.update({i:row_spec})        
    #print(len(list(dict_train270.keys())))
   # print(len(list(dict_train180.keys())))
   # print(len(list(dict_train90.keys())))
   # print(len(list(dict_train0.keys())))
    return(dict_train,dict_train0,dict_train90,dict_train180,dict_train270)
        
def test_dict_read(filename):
    test=pd.read_csv(filename, header=None)
    #print(test.head())
    row_num=test.shape[0]
    image_name=[]
    dict_test={}
    col_x=['outputY']
    for i in range(1,65):
        col_x+=['red'+str(i),'green'+str(i),'blue'+str(i)]
    col_x.append('model_y')
    dict_test={i : {col:0 for col in col_x} for i in range(0,row_num)}
    print('\n read test data')
    for i in range(0,row_num):
        row=test[0][i].split(' ')
        image_name.append(row[0])
        row=row[1:]
        for j in range(0,len(col_x)-1):
            dict_test[i][col_x[j]]=int(row[j])
        j+=1
        dict_test[i][col_x[j]]=270
   # print(len(list(dict_test.keys())))
   # print(dict_test[0])
   # print(image_name)
    return(image_name,dict_test)
    
def find_features(pd_train,less_deg,more_deg):
    col=[]
    for i in range(1,65):
        col+=['red'+str(i),'green'+str(i),'blue'+str(i)]
    print('finding features')
    feature=[]
    while(len(feature)<=50):
        col1=np.random.randint(0,192)
        col2=np.random.randint(0,192)
        pd_train['new_col']=pd_train[col[col1]]-pd_train[col[col2]]
        pd_less=pd_train[pd_train['new_col']<0]
        pd_more=pd_train[pd_train['new_col']>=0]
        count_less=pd_less[pd_less['outputY']==less_deg].shape[0]
        count_more=pd_more[pd_more['outputY']==more_deg].shape[0]
        if count_less>7000 and (count_less+count_more)>10000:                                    
            feature.append((col[col1],col[col2]))
    return(feature)

def hypo(x,feat):
    if x[feat[0]]-x[feat[1]]<0:
        return -1
    else:
        return 1
def normalize(x):
    sum_x=sum(x)
    diff=1-sum_x
    each_add=diff/len(x)
    x=[each_x+each_add for each_x in x]    
    return(x)

def adaboost(dict_trainy,features,negdeg,posdeg):
    print('adaboost')
    N=len(list(dict_trainy.keys()))
    w=pd.DataFrame({'wt':[1/N]*N},index=list(dict_trainy.keys())) 
    a={f:0 for f in features}
    for feat in features:                
        error=0
        for i in list(w.index):            
            hx=hypo(dict_trainy[i],feat)            
            if hx==-1 and dict_trainy[i]['outputY']!=negdeg:               
                error+=w['wt'][i]        
            elif hx==1 and dict_trainy[i]['outputY']!=posdeg:
                error+=w['wt'][i]
#         print(feat,'error',error)
        if error>=0.5:
            continue
        for j in list(w.index):
            hx=hypo(dict_trainy[i],feat) 
            if hx==1 and dict_trainy[i]['outputY']==posdeg:
                w['wt'][j]=w['wt'][j]*error/(1-error)
            elif hx==-1 and dict_trainy[i]['outputY']==negdeg:               
                w['wt'][j]=w['wt'][j]*error/(1-error)
        w['wt']=normalize(w['wt'])      
        
        a[feat]=math.log((1-error)/error)  
    return(a)
    
def write_model(wts,filename):    
    file=open(filename,'w')
    
    for each_0_90_180_270 in wts:
        for feat_wt in each_0_90_180_270:            
            file.write(str(feat_wt)+'->'+str(each_0_90_180_270[feat_wt])+'\n')
        file.write(';;')
    file.close()
    
def model_test(test,range0_90,range0_270,range0_180,range90_180,range90_270,range90_0,range180_270,range180_0,range180_90,range270_180,range270_0,range270_90,model_wt):
    #test if it is 0:
    acc0=0
    acc90=0
    acc180=0
    acc270=0
    total0=0
    total90=0
    total180=0
    total270=0
    wt0_90=model_wt[0]
    wt0_180=model_wt[1]
    wt0_270=model_wt[2]
    wt90_0=model_wt[3]
    wt90_180=model_wt[4]
    wt90_270=model_wt[5]
    wt180_0=model_wt[6]
    wt180_90=model_wt[7]
    wt180_270=model_wt[8]
    wt270_0=model_wt[9]
    wt270_90=model_wt[10]
    wt270_180=model_wt[11]
    row_num=len(list(test.keys()))    
    feature0_90=list(wt0_90.keys())
    feature0_270=list(wt0_270.keys())
    feature0_180=list(wt0_180.keys())
    feature90_180=list(wt90_180.keys())
    feature90_270=list(wt90_270.keys())
    feature90_0=list(wt90_0.keys())
    feature180_270=list(wt180_270.keys())
    feature180_0=list(wt180_0.keys())
    feature180_90=list(wt180_90.keys())
    feature270_180=list(wt270_180.keys())
    feature270_0=list(wt270_0.keys())
    feature270_90=list(wt270_90.keys())
    for i in range(0,row_num):
        res0_1=0
        res0_2=0
        res0_3=0
        res90_1=0
        res90_2=0
        res90_3=0
        res180_1=0
        res180_2=0
        res180_3=0
        res270_1=0
        res270_2=0
        res270_3=0
        
        result0_90={k:0 for k in feature0_90}        
        for feat in feature0_90:            
            result0_90[feat]=hypo(test[i],feat)*wt0_90[feat]        
        if sum(list(result0_90.values()))<0:
            res0_1=abs(sum(list(result0_90.values())))

        
        
        result0_180={k:0 for k in feature0_180}        
        for feat in feature0_180:            
            result0_180[feat]=hypo(test[i],feat)*wt0_180[feat]        
        if sum(list(result0_180.values()))<0:
            res0_2=abs(sum(list(result0_180.values())))

       
            
                
        result0_270={k:0 for k in feature0_270}        
        for feat in feature0_270:            
            result0_270[feat]=hypo(test[i],feat)*wt0_270[feat]        
        if sum(list(result0_270.values()))<0:
            res0_3=abs(sum(list(result0_270.values())))

            
        result90_180={k:0 for k in feature90_180}        
        for feat in feature90_180:            
            result90_180[feat]=hypo(test[i],feat)*wt90_180[feat]        
        if sum(list(result90_180.values()))<0:
            res90_1=abs(sum(list(result90_180.values())))

       
        result90_270={k:0 for k in feature90_270}        
        for feat in feature90_270:            
            result90_270[feat]=hypo(test[i],feat)*wt90_270[feat]        
        if sum(list(result90_270.values()))<0:
            res90_2=abs(sum(list(result90_270.values())))
      
        result90_0={k:0 for k in feature90_0}        
        for feat in feature90_0:            
            result90_0[feat]=hypo(test[i],feat)*wt90_0[feat]        
        if sum(list(result90_0.values()))<0:
            res90_3=abs(sum(list(result90_0.values())))
            
        result180_270={k:0 for k in feature180_270}        
        for feat in feature180_270:            
            result180_270[feat]=hypo(test[i],feat)*wt180_270[feat]        
        if sum(list(result180_270.values()))<0:
            res180_1=abs(sum(list(result180_270.values())))
            
        result180_0={k:0 for k in feature180_0}        
        for feat in feature180_0:            
            result180_0[feat]=hypo(test[i],feat)*wt180_0[feat]        
        if sum(list(result180_0.values()))<0:
            res180_2=abs(sum(list(result180_0.values())))
        
        result180_90={k:0 for k in feature180_90}        
        for feat in feature180_90:            
            result180_90[feat]=hypo(test[i],feat)*wt180_90[feat]        
        if sum(list(result180_90.values()))<0:
            res180_3=abs(sum(list(result180_90.values())))
            
        result270_180={k:0 for k in feature270_180}        
        for feat in feature270_180:            
            result270_180[feat]=hypo(test[i],feat)*wt270_180[feat]        
        if sum(list(result270_180.values()))<0:
            res270_1=abs(sum(list(result270_180.values())))
            
        result270_0={k:0 for k in feature270_0}        
        for feat in feature270_0:            
            result270_0[feat]=hypo(test[i],feat)*wt270_0[feat]        
        if sum(list(result270_0.values()))<0:
            res270_2=abs(sum(list(result270_0.values())))
        
        result270_90={k:0 for k in feature270_90}        
        for feat in feature270_90:            
            result270_90[feat]=hypo(test[i],feat)*wt270_90[feat]        
        if sum(list(result270_90.values()))<0:
            res270_3=abs(sum(list(result270_90.values())))
    
        max_val=max(res0_1,res0_2,res0_3,res90_1,res90_2,res90_3,res180_1,res180_2,res180_3,res270_1,res270_2,res270_3)
        if res0_1==max_val or res0_2==max_val or res0_3==max_val:
            test[i]['model_y']=0
        
        if res90_1==max_val or res90_2==max_val or res90_3==max_val:
            test[i]['model_y']=90
            
        if res180_1==max_val or res180_2==max_val or res180_3==max_val:
            test[i]['model_y']=180
            
        if res270_1==max_val or res270_2==max_val or res270_3==max_val:
            test[i]['model_y']=270
        

        

#         if final_res270>0 and final_res270>final_res90 and final_res270>final_res0 and final_res270>final_res180:
#             test[i]['model_y']=270
        
        if (test[i]['outputY']==test[i]['model_y']):
            if test[i]['outputY']==0:
                acc0+=1
            elif test[i]['outputY']==90:
                acc90+=1
            elif test[i]['outputY']==180:
                acc180+=1
            elif test[i]['outputY']==270:
                acc270+=1
        if test[i]['outputY']==0:
            total0+=1
        elif test[i]['outputY']==90:
            total90+=1
        elif test[i]['outputY']==180:
            total180+=1
        elif test[i]['outputY']==270:
            total270+=1
        print('row',i,'trueoutput',test[i]['outputY'],'predoutput',test[i]['model_y'])
        print('acc',acc0,acc90,acc180,acc270,'total',total0,total90,total180,total270)
    #print('Accuracy=',(acc0+acc90+acc180+acc270)/row_num*100)
    return(test)
        
def read_model(filename):
    weights=[]
    with open(filename, 'r') as myfile:
        all_data = myfile.read()    
        all_list=all_data.split(';;')    
        for data in all_list:
            wt_dict={}
            list_items=data.split('\n')    
            list_items=list_items[0:len(list_items)-1]
            for each in list_items:
                items=each.split('->')
                key1=items[0]
                key1=key1.strip("()'' ")                 
                key1=key1.split(',')                
                key=(tuple([key1[0].strip("''"),key1[1][2:]]))
                values=float(items[1])
                wt_dict[key]=values
            weights.append(wt_dict)
    return(weights)
    
def gen_output(filename,img_list,dict_test):
    file=open(filename,'w')
    c=0
    for row in dict_test:
        file.write(str(img_list[row])+' '+str(dict_test[row]['model_y'])+'\n')
        if(dict_test[row]['model_y']==dict_test[row]['outputY']):
            c+=1
    print('Accuracy='+str(c*100/len(list(dict_test.keys()))))

(to_do, train_test_fname, model_file_name,model) = sys.argv[1:]


if to_do=='train' and model=='adaboost':
    
    pd_train=train_pd_read(train_test_fname)
    dict_train,dict_train0,dict_train90,dict_train180,dict_train270=train_dict_read(train_test_fname)

    pd_train_0_90=pd_train[pd_train['outputY']!=270]
    pd_train_0_90=pd_train_0_90[pd_train_0_90['outputY']!=180]
    #print(pd_train_0_90['outputY'].value_counts())

    pd_train_0_270=pd_train[pd_train['outputY']!=90]
    pd_train_0_270=pd_train_0_270[pd_train_0_270['outputY']!=180]
   # print(pd_train_0_270['outputY'].value_counts())

    pd_train_0_180=pd_train[pd_train['outputY']!=90]
    pd_train_0_180=pd_train_0_180[pd_train_0_180['outputY']!=270]
  #  print(pd_train_0_180['outputY'].value_counts())

    pd_train_90_270=pd_train[pd_train['outputY']!=0]
    pd_train_90_270=pd_train_90_270[pd_train_90_270['outputY']!=180]
  #  print(pd_train_90_270['outputY'].value_counts())

    pd_train_90_180=pd_train[pd_train['outputY']!=0]
    pd_train_90_180=pd_train_90_180[pd_train_90_180['outputY']!=270]
  #  print(pd_train_90_180['outputY'].value_counts())
    
    pd_train_180_270=pd_train[pd_train['outputY']!=0]
    pd_train_180_270=pd_train_180_270[pd_train_180_270['outputY']!=90]
   # print(pd_train_180_270['outputY'].value_counts())
    
    dict_train_0_90=dict_train0.copy()
    dict_train_0_90.update(dict_train90)
    dict_train_0_180=dict_train0.copy()
    dict_train_0_180.update(dict_train180)
    dict_train_0_270=dict_train0.copy()
    dict_train_0_270.update(dict_train270)
    dict_train_90_180=dict_train90.copy()
    dict_train_90_180.update(dict_train180)
    dict_train_90_270=dict_train90.copy()
    dict_train_90_270.update(dict_train270)
    dict_train_180_270=dict_train180.copy()
    dict_train_180_270.update(dict_train270)
    
    
    range0_90=find_features(pd_train_0_90,0,90)
    range0_270=find_features(pd_train_0_270,0,270)
    range0_180=find_features(pd_train_0_180,0,180)
    range90_180=find_features(pd_train_90_180,90,180)
    range90_270=find_features(pd_train_90_270,90,270)
    range90_0=find_features(pd_train_0_90,90,0)
    range180_270=find_features(pd_train_180_270,180,270)
    range180_90=find_features(pd_train_90_180,180,90)
    range180_0=find_features(pd_train_0_180,180,0)
    range270_180=find_features(pd_train_180_270,270,180)
    range270_90=find_features(pd_train_90_270,270,90)
    range270_0=find_features(pd_train_0_270,270,0)


    
    wt0_90=adaboost(dict_train0,range0_90,0,90)    
    wt0_270=adaboost(dict_train0,range0_270,0,270)    
    wt0_180=adaboost(dict_train0,range0_180,0,180)    
    wt90_180=adaboost(dict_train90,range90_180,90,180)    
    wt90_270=adaboost(dict_train90,range90_270,90,270)
    wt90_0=adaboost(dict_train90,range90_0,90,0)    
    wt180_270=adaboost(dict_train180,range180_270,180,270)    
    wt180_0=adaboost(dict_train180,range180_0,180,0)    
    wt180_90=adaboost(dict_train180,range180_90,180,90)    
    wt270_180=adaboost(dict_train270,range270_180,270,180)    
    wt270_0=adaboost(dict_train270,range270_0,270,0)    
    wt270_90=adaboost(dict_train270,range270_90,270,90)
    
    all_wts=[wt0_90,wt0_180,wt0_270,wt90_0,wt90_180,wt90_270,wt180_0,wt180_90,wt180_270,wt270_0,wt270_90,wt270_180]
    write_model(all_wts,model_file_name)
    print('train done')
    
elif to_do=='test' and model=='adaboost':
    img_lst,dict_test=test_dict_read(train_test_fname)   
    model_wt=read_model(model_file_name)
    new_test=model_test(dict_test,range0_90,range0_270,range0_180,range90_180,range90_270,range90_0,range180_270,range180_0,range180_90,range270_180,range270_0,range270_90,model_wt)
    gen_output('output.txt',img_lst,new_test)
else:
    print('Please check , command says neither train nor test')