#/!usr/bin/env python3
# throws error when run using ./ocr.py... but works fine using python ocr.py....
#
# ./ocr.py : Perform optical character recognition, usage:
#     ./ocr.py train-image-file.png train-text.txt test-image-file.png
#
# Authors: (Raja Rajeshwari Premkumar (rpremkum), Vijaya Krishna Gopalakrishnan Partha (vgopala), Gopal Seshadri (gseshad))
# (based on skeleton code by D. Crandall, Oct 2018)

#
# Issues faced:
# finding a good emission was a challenge
# I tried many other techniques - finding emission using each pixel in the test letter and hidden. but it is very sensitive to noise
# I tried using only the * (since it is not sensitive to noise) - then faced issue with setting for test space, tried using only ' ' but again sensitive to noise. So ultimately it is now and amalgamation of both.
# the transition works well where emission cant, but the noise m is tricky. There were other techniques of setting noise I tried but this is by far the best.
# There are 3 assumptions that are inline with the code.
# How it works-The train file bc.train is used to get the transition probability. 
# We remove POS from the train file and the combination ' .','. ' and '..' are replaced with a '.' as part of data cleaning 
#Each letter in the train file is scanned starting if letter i is scanned then a count is increased for transition from i to i+1th charcter. after scanning the count is then divided by total number of occurances of letter i
#The above is repeated for uppercase letter after removing special characters. 
# The log of the above calculated transition is set
# Simple algorithm is based on emission, for every test letter the corresponding hidden indicated by the emission is displayed
# Initial probability for each is found using number of occurances after a new line.
# Emission probability is calculated in two parts:
#first calculate the emission by comparing the * between the test and the hidden
#second calculate the emission by comparing the ' ' between test and hidden
#final emission is the product of above- intuition behind this is the emission w.r.t the space approximates how good the image of that test letter is-inverse of it would be noise
# also between the test and hidden the spaces also should match, hence a product of the emission w.r.t * and ' ' was taken
#the challenge here is the emission by comparing ' ' is 0 (meaning matches) with all or most of the hidden letters for the test letter that are spaces
#Hence, I handled this by taking a mean of the  * in each test letter and compared against it to get the spaces in the test image
#The above step was including special characters since they are outliers w.r.t count of stars, so I have checked if the test image matches to these special characters with some threshold, then do not consider as space
#noise m is also calculated- each test letter is scanned -the one with the least number of * in it is the noise. if the noise is 0 set it to 0.0002
# Viterbi algorithm-We use the -log of all probabilities and minimise the posterior*emission values in Viterbi:
#we use dictionaries of dictionary to hold the probabilites - emission, transition and posterior, for emission the key is the test letter index, the value is a dictionary with key hidden variable and value the emission probability
# for transition and posterior the key is hidden variable and value is a dictionary with key a hidden variable with value the probability
# initial is a dictionary with key the hidden variable and value the initial probability
# they are are intialised with zeroes to accomodate the counts but later while converting to log ,if any prob is 0 it is set to a very high value 
#For t=0, the product of initial and emission is taken we put weight 1.5 and 2  since intial is too high than emission and outweighs it sometimes
#the posterior is stored as a list for each hidden variable [posterior probability,h_back] where h_back is the hidden var from which it was obtained (for t=0 this is set to 'initial')]
# at each time t the product of posterior and emission of the test is taken. Before that the minimum of the posterior*transition is found. 
# the final string is printed as follows:
#for the last letter in the sentence the hidden with least probability is picked and the h_back is used to back traverse and find the complete sentence. it is then reversed and returned.


from PIL import Image, ImageDraw, ImageFont
import sys
import pandas as pd
import numpy as np
import math

CHARACTER_WIDTH=14
CHARACTER_HEIGHT=25


def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
   # print(im)
    (x_size, y_size) = im.size
   # print(im.size)
   # print(int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH)
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [ [ "".join([ '*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg+CHARACTER_WIDTH) ]) for y in range(0, CHARACTER_HEIGHT) ], ]
    return result

def load_training_letters(fname):
    TRAIN_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    letter_images = load_letters(fname)
    #print(letter_images)
    return { TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len(TRAIN_LETTERS) ) }

def read_data(filename):
    f=open(filename,'r')
    data=f.read() 
    pos=['ADJ', 'ADV', 'ADP', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRON', 'PRT', 'VERB']
    '''
    Remove parts of speech tags in the train file:
    '''
    for each in pos: 
        data=data.replace(" "+each,'')
        data=data.replace(each,'') 
        
    data=data.replace(' .','.')
    data=data.replace('. ','.')
    data=data.replace('..','.')
    data=data.replace(' ,',',')
    data=data.replace(',,',',')

    return(data)

def train_transition(filename,train_img):
     data=read_data(filename)     
     dict_letter_image=load_training_letters(train_img) # map letters with the images
     hidden_var=list(dict_letter_image.keys()) # all letters in train image
     n=len(hidden_var)
     trans_proba= {ch : {ch1:0 for ch1 in hidden_var} for ch in hidden_var} #initialize all transition prob to 0
     #mtotal={ch:data.count(ch) for ch in hidden_var} # total transitions for each character in train data
     #print('total',total)
     total_init=data.count('\n')+1 #total initial counts
     init_proba={ch :0 for ch in hidden_var} # for each character, initialize initial probability to 0
     init_proba[data[0]]+=1 # for the first character in train file
     nd=len(data)-1 # read till last but one character of the train file
     
     #print(data)
     for i in range(0,nd): 
         '''
         Record the initial occurance count for each character:
             '''
         if data[i]=='\n':
             j=i+1
             while(j<=nd): # ignore the characters not in hidden variables
                 if data[j] in hidden_var:
                     init_proba[data[j]]+=1
                     break # break once found the first hidden variable that is encountered in a new line
                 else:
                     j+=1
                     '''
                     Record the transition counts for each character:
                         '''
         if data[i+1] not in hidden_var or data[i] not in hidden_var:  # ignore the characters not in hidden variables          
             continue
         trans_proba[data[i]][data[i+1]]+=1 # record transition count from character i to i+1
         
         '''
         Train using upper case of the train data to account for proper transition of upper case letters:
             '''
     upper_hid=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ ')
     data=str.upper(data)
     for i in range(0,nd): 
         if data[i+1] not in upper_hid or data[i] not in upper_hid:  # ignore the characters that are not upper case letters or space          
             continue
         trans_proba[data[i]][data[i+1]]+=1
         '''
         Convert the counts to -log of probabilities:
             '''
    
     for ch_first in trans_proba: # for transition probability
         total= sum([trans_proba[ch_first][ch_next] for ch_next in trans_proba[ch_first] ])
         for ch_next in trans_proba[ch_first]:
             if total !=0 and trans_proba[ch_first][ch_next]!=0:                 
                 trans_proba[ch_first][ch_next]=-math.log(trans_proba[ch_first][ch_next]/float(total))
             else:
                 trans_proba[ch_first][ch_next]=-math.log(1/float(nd))+nd
             
         if (init_proba[ch_first]!=0):             
             init_proba[ch_first]=-math.log(init_proba[ch_first]/float(total_init)) # for initial probability   
         else:
             init_proba[ch_first]=-math.log(1/float(nd))+nd
        #print('A',trans_proba['A'])     
     return(init_proba,trans_proba)
    # print(np.array(discard).unique())
     
def emission(train_letters,test_letters):
    
    '''
    initialize
    '''
    hidden_var=list(train_letters.keys())    # list of hidden variables
    emi_proba={i : {ch1:0 for ch1 in hidden_var} for i in range(0,len(test_letters))} # emission probabilities for each image against each letter
    num_pix_img=CHARACTER_HEIGHT*CHARACTER_WIDTH # total number of pixel
   
                    
                
    '''
    calculate the emission probabilities for test characters that are not spaces using *:
    '''
    spaces=[]
    for test in range(0,len(test_letters)): # for each image in the test example
        if test not in spaces:
            test_img=test_letters[test]
            a=test_img[:]
            str_test="\n".join([ r for r in test_img ])
            for hid in train_letters:  # for each hidden letter of the language calculate emission prob for the test image 
                hid_img=train_letters[hid]
                c_test=0
                c_hid=0
                b=hid_img[:]
                str_hid="\n".join([ r for r in hid_img ])                
                for i in range(0,CHARACTER_HEIGHT):# loop through entire one character of the test image and hiddden letter
                    for j in range(0,CHARACTER_WIDTH):
                        g=a[i][j]
                        h=b[i][j]
                        if h=='*':
                            c_hid+=1 # keeps count of number of * in the hidden character
                            if g==h:
                                c_test+=1 
                                # keeps count of number of matches of * between the test character and the hidden letter
                                #c_hid will be 0 when hid==' '
                if c_hid!=0 and (c_test/float(c_hid))!=0: 
                    emi_proba[test][hid]*=-math.log(c_test/float(c_hid))  
                else:
                    #we know that test is not a space so low priority when c_hid=0 i.e. when hid=' '
                    #also satisfied when no matches found with other hidden characters
                    emi_proba[test][hid]*=-math.log(1/float(num_pix_img))+num_pix_img
    '''
    identify the spaces in the test letter
    '''
    
    spaces=[]    
    len_test=len(test_letters)
    sum_star_proba=0
    star_proba=[("\n".join([ r for r in each ]).count('*'))/float(num_pix_img) for each in test_letters]   
    mean_star_proba=sum(star_proba)/float(len_test)
   
    
    for t in range(0,len(test_letters)):
        str_test="\n".join([ r for r in test_letters[t] ])
        sum_star=str_test.count('*')
        star_proba=sum_star/float(num_pix_img)
        if star_proba<mean_star_proba/1.6: # Assumption1 all test letters have %of stars almost as much as the mean -1.6 can be called the deviation allowed
            spec_prob=[emi_proba[t][h] for h in '(),.-!?\"']                          
            if round(float(min(spec_prob)))>0.3: # Assumption1 in line 181 takes these special characters as well and they get classified as a space
                #Hence we keep a threshold of 0.25, if the test letter is classied as a special character with a log probability less than 0.25 then we don not include it in the spaces
                spaces.append(t)
               
                  
    '''
    to identify the space in test image and also set the emission for all based on ' ':
    '''
    
    for test in range(0,len(test_letters)): # for each image in the test example
        test_img=test_letters[test]
        a=test_img[:]
        str_test="\n".join([ r for r in test_img ])
        count_zero=0
        for hid in train_letters:
            # for each hidden letter of the language calculate emission prob for the test image 
            hid_img=train_letters[hid]
            c_test=0
            c_hid=0
            b=hid_img[:]
            str_hid="\n".join([ r for r in hid_img ])            
            for i in range(0,CHARACTER_HEIGHT):# loop through entire one character of the test image and hiddden letter
                for j in range(0,CHARACTER_WIDTH):
                    g=a[i][j]
                    h=b[i][j]
                    if h==' ':
                        c_hid+=1 # keeps count of number of ' ' in the hidden character
                        if g==h:
                            c_test+=1 # keeps count of number of matches of ' ' between the test character and the hidden letter
            
            if c_hid!=0 and c_test!=0:# c_hid!=0 should always be satisfied (assumption that hidden characters will have at least one space)
                emi_proba[test][hid]*=-math.log(c_test/float(c_hid))
                
            else:
                emi_proba[test][hid]*=-math.log(1/float(num_pix_img))+num_pix_img
          
    '''
    calculate the emission probabilities for the spaces in test
    Also set the emission for other letters against the hidden variable space:
    '''
 
    for sp in spaces:
        for h in train_letters:             
            if h==' ':
                emi_proba[sp][h]=-math.log(0.9999)
            else:
                emi_proba[sp][h]=-math.log(1/float(num_pix_img))+num_pix_img
 
    for t in range(0,len(test_letters)):
        if t not in spaces:
            emi_proba[t][' ']=-math.log(1/float(num_pix_img))+num_pix_img
                
    return(emi_proba)
    
def simple(proba): # proba is the final resultant probability of each image w.r.t each character
    to_str=''
    for each in proba:        
        dvalues=list(proba[each].values())
        min_proba=min(dvalues) # since it is in log terms we use min
        keys=list(proba[each].keys())
        ind=dvalues.index(min_proba)
        res_ch=keys[ind]
        to_str+=res_ch
    return(to_str) # return the most probable string for image passed in proba

def image_to_str(vit):
    list_img=list(vit.keys())
    last=len(list_img)-1
    res_str=''
    vals=[each[0] for each in list(vit[last].values())]
    key=list(vit[last].keys())
    min_val_last=min(vals)
    last_ch=key[vals.index(min_val_last)]
    res_str+=last_ch
    prev_ch=last_ch
    for im in range(last-1,-1,-1):
        now_ch=vit[im+1][prev_ch][1]
        res_str+=now_ch
        prev_ch=now_ch
    return(res_str[::-1])
    
def viterbi(emis,init,trans):    
    list_img=list(emis.keys())
    list_ch=list(init.keys())
    post={im: {ch:0 for ch in list_ch} for im in list_img} #posterior probabilities
    
    for im in list_img:        
        for ch in list_ch:
            if im==0: 
                '''
    Posterior for the first character in the image= initial*emission:
        '''
                post[im][ch]=[1.5*m*init[ch]+2*emis[im][ch],'init'] # multiply initial by 0.1 to reduce the weightage on initial probability
                
            else:
                '''
    Estimate other posterior probabilities starting from the second character
    '''
                # here m percent noise in image considered, m percent we need to rely on the transition probability
                temp_post={ch1: post[im-1][ch1][0]+m*trans[ch1][ch] for ch1 in list_ch}
                val=list(temp_post.values())
                minval_prev_ch=min(val)
                key=list(temp_post.keys())
                prev_ch=key[val.index(minval_prev_ch)]
                # 1-m percent we can rely on emission 
                post[im][ch]=[minval_prev_ch+20*emis[im][ch],prev_ch]
                
    return(post)
    

    
def estimate_noise(test_let):
    num_star=[]
    for test in test_let:
        str_test="\n".join([ r for r in test])
        num_star.append(str_test.count('*'))
    num_pix=CHARACTER_HEIGHT*CHARACTER_WIDTH
    
    for i in range(0,num_star.count(0)):
        num_star.remove(0)
    
    num_star.sort()
    noise=num_star[0]/float(num_pix) #trying to fetch the test letter space with some noise
    
    if noise<0.001 or num_star[0]>CHARACTER_WIDTH/float(2): #Assumption3 -each test letter is at more than width/2
        noise=0.001
    return(noise)
    
        
#####
# main program
(train_img_fname, train_txt_fname, test_img_fname) = sys.argv[1:]


train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)
m=estimate_noise(test_letters)
EMI_P=emission(train_letters,test_letters)
print('Simple: %s' % simple(EMI_P))
INIT_P,TRANS_P=train_transition(train_txt_fname,train_img_fname)
VITERBI_P=viterbi(EMI_P,INIT_P,TRANS_P)
vit=image_to_str(VITERBI_P)
print('Viterbi: %s' % vit)
print("Final Answer:")
print(vit)


#print("\n".join([ r for r in test_letters[27] ]))
# Same with test letters. Here's what the third letter of the test data
#  looks like:
#print("\n".join([ r for r in test_letters[2]]))

