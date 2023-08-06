# -*- coding: utf-8 -*-
import numpy as np
from Bio import SeqIO

bases = ['A', 'C', 'G', 'T']
def onehot2(seq):
    X = np.zeros((len(seq), len(bases))) #(41*4)
    for i, char in enumerate(seq):
        X[i, bases.index(char)] = 1 #(put 1 for every found char A,C,G,T)
    return X

def OneHotSequence(file1):
    sequences = [] 
    for record in SeqIO.parse(file1,"fasta"):
        sequences.append((record.seq.upper()))   
    PosSeq=[]
    for i in range (len(sequences)):
        c=sequences[i]
        b=c._data
        PosSeq.append(b)
    


    input_features2 = []
    for a in range(len(PosSeq)):
        input_features2.append(onehot2(PosSeq[a]))
    input_features = np.array(input_features2)
    return PosSeq,input_features