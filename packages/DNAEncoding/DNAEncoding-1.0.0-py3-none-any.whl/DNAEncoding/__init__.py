# -*- coding: utf-8 -*-
import numpy as np
from Bio import SeqIO

def GetSequence(file1,SequenceLength):
    sequences = [] 
    for record in SeqIO.parse(file1,"fasta"):
        sequences.append((record.seq.upper()))   
    PosSeq=[]
    for i in range (len(sequences)):
        c=sequences[i]
        b=c._data
        PosSeq.append(b)
    return PosSeq