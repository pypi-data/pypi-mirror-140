# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
from nltk.util import ngrams


class N_Gram():
    
    def __init__(self,  
                 in_AOI,
                 in_AOI_str,
                 in_AOI_str_ncr,
                 k_grams, simple_analysis = False):

        
        self.in_AOI = in_AOI_str_ncr
        self.nb_aoi = len(set(in_AOI))
        
        self.k_grams = k_grams
        self.result_set = {'AOI_based_variables': {}}
        
        
    def comp_ngram (self, n, discard_order = True):
        
        seq_aoi = self.in_AOI
        self.nb_aoi = len(set(seq_aoi))
        
        seq_aoi = seq_aoi.replace("", " ")
        #print(seq_aoi.split())
        
        #print(set(seq_aoi.split()))
   
        n_grams = ngrams(seq_aoi.split(), n)
        poly_gram = []
        if discard_order:
            for grams in n_grams:
                poly_gram.append(tuple(sorted(grams)))
        else :
            for grams in n_grams:
                poly_gram.append(grams)

        nb_seq = len(poly_gram)        
        results = {}
     
        for item in sorted(set(poly_gram)):
            results.update({item: (poly_gram.count(item))/nb_seq}) 

        return results    
        
        
    def process (self):
        
        results = self.comp_ngram(self.k_grams, discard_order = False)
        results_d = self.comp_ngram(self.k_grams)
   
        self.result_set['AOI_based_variables']['N_Gram'] = {}
        self.result_set['AOI_based_variables']['N_Gram'] = ({'results': results,
                                                              'results_od' : results_d}) 
         
  
        print('\n\n-----------------------------------------------------------------------')
        print("{nbr_gram}-GRAM Analysis".format(nbr_gram = self.k_grams))
        print('-----------------------------------------------------------------------\n')

        for gram, prop in results.items():
            
            gram_str = gram[0]
            for i in range (1, len(gram)):
                gram_str += "|"
                gram_str += gram[i]
            print("\t{0:40}\t {1}".format(gram_str, round(prop, 3)))
                
    def get_result_set (self):
        return self.result_set
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    