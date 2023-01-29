#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import time
import psutil

# In[7]:


def dictFromInp(filename):
    with open(filename,'r') as file:
        data = file.read().split('\n')
        inp = dict()
        for d in data:
            if d.isalpha():
                key = d
                inp[key] = []
            if d.isdigit():
                inp[key].append(int(d))
        
    return inp

def formulateString(d):
    l = []
    for s in d.keys():
        currString = s
        for i in d[s]:
            currString = currString[:i+1] + currString + currString[i+1:]
        assert len(currString) == 2**len(d[s])*len(s)
        l.append(currString)
    
    return l


def sequenceAlignment(seq1, seq2, gapPenalty,alphaPenalty):
    
    # sequenceAlignmentValue
    m = len(seq1)
    n = len(seq2)

    dp = np.zeros((m+1,n+1))

    for i in range(m+1):
        dp[i,0] = i*gapPenalty

    for j in range(n+1):
        dp[0,j] = j*gapPenalty

    for i in range(1,m+1):
        for j in range(1,n+1):
            dp[i,j] = min(alphaPenalty[seq1[i-1]][seq2[j-1]] + dp[i-1,j-1], 
                          gapPenalty + dp[i,j-1], gapPenalty + dp[i-1,j])
    
    # sequenceAlignmentFormulation
    s1 = ""
    s2 = ""
    
    i = m
    j = n
    
    while i>0 and j>0:
        if dp[i,j]==dp[i-1,j-1]+alphaPenalty[seq1[i-1]][seq2[j-1]]:
            s1 += seq1[i-1]
            s2 += seq2[j-1]
            i -= 1
            j -= 1
        elif dp[i,j]==gapPenalty + dp[i,j-1]:
            s1 += "_"
            s2 += seq2[j-1]
            j -= 1
        elif dp[i,j]==gapPenalty + dp[i-1,j]:
            s1 += seq1[i-1]
            s2 += "_"
            i -= 1
            
    while i>0:
        s1 += seq1[i-1]
        s2 += "_"
        i -= 1
    while j>0:
        s1 += "_"
        s2 += seq2[j-1]
        j -= 1
    
    return s1[::-1],s2[::-1]


def divideConquerSequenceAlignment(seq1, seq2, gapPenalty, alphaPenalty):
    m = len(seq1)
    n = len(seq2)
    
    if m<2 or n<2:
        return sequenceAlignment(seq1,seq2,gapPenalty,alphaPenalty)
    
    f = spaceEfficientSequenceAlignment(seq1,seq2[:n//2],gapPenalty,alphaPenalty)
    g = spaceEfficientSequenceAlignment(seq1[::-1],seq2[n//2:][::-1],gapPenalty,alphaPenalty)[::-1]
    optScore = f+g
    
    optSplit = np.argmin(optScore)
    
    preAlign1, preAlign2 = divideConquerSequenceAlignment(seq1[:optSplit],seq2[:n//2],gapPenalty,alphaPenalty)
    suffAlign1, suffAlign2 = divideConquerSequenceAlignment(seq1[optSplit:],seq2[n//2:],gapPenalty,alphaPenalty)
    
    return preAlign1+suffAlign1,preAlign2+suffAlign2

    
def spaceEfficientSequenceAlignment(seq1, seq2, gapPenalty, alphaPenalty):
    m = len(seq1)
    n = len(seq2)
    
    dpEff = np.zeros((m+1,2))
    
    for i in range(m+1):
        dpEff[i,0] = i*gapPenalty
        
    for j in range(1,n+1):
        dpEff[0,1] = j*gapPenalty
        for i in range(1,m+1):
            dpEff[i,1] = min(alphaPenalty[seq1[i-1]][seq2[j-1]] + dpEff[i-1,0], 
                             gapPenalty + dpEff[i,0], gapPenalty + dpEff[i-1,1])
        dpEff[:,0] = dpEff[:,1]
    
    return dpEff[:,1]
        
    
def alignmentPenalty(s,t,gapPenalty,alphaPenalty):
    a=0
    i=len(s)-1
    while(i>=0):
        if s[i]=='_' or t[i]=='_':
            a += gapPenalty
            i -= 1
        else:
            a += alphaPenalty[s[i]][t[i]]
            i -= 1
    
    return a


def createOutput(align1,align2,pen,tim,mem,filename):
    with open(filename,'w') as f:
        f.write(f"{align1[:50]} {align2[:50]}\n{align1[-50:]} {align2[-50:]}\n{pen}\n{tim:.2f}\n{mem:.2f}")

    
def runSequenceAlignmentDC(filename):
    tik = time.time()
    d = dictFromInp(filename)
    l = formulateString(d)
    seq1 = l[0]
    seq2 = l[1]
    gapPenalty = 30
    alphaPenalty = {'A':{'A':0, 'C':110, 'G':48, 'T':94}, 'C':{'A':110, 'C':0, 'G':118, 'T':48}, 'G':{'A':48, 'C':118, 'G':0, 'T':110}, 'T':{'A':94, 'C':48, 'G':110, 'T':0}}
    mem = psutil.Process().memory_info().rss / (1024)
    effAlign1, effAlign2 = divideConquerSequenceAlignment(seq1,seq2,gapPenalty,alphaPenalty)
    memUsed = psutil.Process().memory_info().rss / (1024) - mem
    tok = time.time() - tik
    alignPenalty = alignmentPenalty(effAlign1, effAlign2, gapPenalty, alphaPenalty)
    createOutput(effAlign1, effAlign2, alignPenalty, tok, memUsed, "outputDC.txt")
    

if __name__ == '__main__':

    filename = 'testInp.txt'
    runSequenceAlignmentDC(filename)
