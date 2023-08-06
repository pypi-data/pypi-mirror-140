# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


class Lempei_Ziv_Complexity():
    
    def __init__(self, 
                 in_AOI,
                 in_AOI_str,
                 in_AOI_str_ncr,
                 k_grams, simple_analysis = False):


        self.result_set = {'AOI_based_variables': {}}       
        self.in_AOI = in_AOI_str_ncr
        
         
    def Lempei_Ziv_c (self, sequence):
        
        sub_strings = set()
        n = len(sequence)
    
        ind = 0
        inc = 1
        while True:
            if ind + inc > len(sequence):
                break
            sub_str = sequence[ind : ind + inc]
            if sub_str in sub_strings:
                inc += 1
            else:
                sub_strings.add(sub_str)
                ind += inc
                inc = 1
        #print(sub_strings)
        return len(sub_strings), list(sub_strings)
        
        
    def process (self):
        
        complexity, decomposition = self.Lempei_Ziv_c(self.in_AOI)
        
        self.result_set['AOI_based_variables'].update({'lempei_ziv_complexity': {}})
        self.result_set['AOI_based_variables']['lempei_ziv_complexity'].update({'complexity': complexity,
                                                                                'decomposition': decomposition})
 
        print('\n\n-----------------------------------------------------------------------')
        print("Lempei Ziv Analysis")
        print('-----------------------------------------------------------------------\n')
            
        print("\t{0:40}\t {1}".format('Lempei Ziv Complexity', np.round(complexity,3)))
        print("\t{0:40}\t {1}".format('Lempei Ziv Decomposition', decomposition[0]))
        for i in range (1, len(decomposition)):
            print("\t{0:40}\t {1}".format('_____', decomposition[i]))
            
        
    def get_result_set (self):
        return self.result_set  
        
        
        
        
        
        
        
        

