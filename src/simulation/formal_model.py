'''
Created on Jan 25, 2022

@author: jesus calvillo
'''

class Formal_Model:
    def __init__(self,time,basic_propositions):
        self.time=time
        self.basic_propositions=basic_propositions
        self.proposition_values={}
        for b_prop in self.basic_propositions:
            self.proposition_values[b_prop]=0
            
    def print_basic_propositions(self,file=None):
        props=[]
        for prop in self.basic_propositions:
            prop_string=prop[0]
            if len(prop)>1:
                prop_string+="("
                for arg in range(1,len(prop)):
                    prop_string+=prop[arg]
                    if arg<len(prop)-1:prop_string+=","  
                prop_string+=")"
            props.append(prop_string)
        
        props_string=" ".join(props)
        
        if file:file.write(props_string+"\n")
        else: print(props_string)
        
        
    
    def print_me(self,only_true=True, file=None):
        if file: 
            file.write("==================================================\n")
            file.write("MODEL OBSERVATION AT TIME "+str(self.time)+"\n")
        else: 
            print("==================================================")
            print("MODEL OBSERVATION AT TIME "+str(self.time)+"\n")
        
        if only_true:       
            if file:file.write("PROPOSITIONS THAT ARE TRUE:\n")
            else: print("PROPOSITIONS THAT ARE TRUE:")
            
        for b_prop in self.basic_propositions:
            res=b_prop[0]+"("
            for arg in range(1,len(b_prop)):
                res+=b_prop[arg]
                if arg<len(b_prop)-1:res+=","  
            res+=")"
            
            if only_true:
                if self.proposition_values[b_prop]:
                    if file:file.write(res+"\n")
                    else:print(res)
            else:
                if file:file.write(str(self.proposition_values[b_prop])+"\t"+res+"\n")
                else: print(str(self.proposition_values[b_prop])+"\t"+res)
                
    
    #Even though prolog prints numbers with 6 decimal digits, it seems it also accepts no digits and behaves the same, w.r.t. binary vectors
    def print_binary_vector(self, file=None):
        vect=[self.proposition_values[prop] for prop in self.basic_propositions]
        vect=[f"{var:.0f}" for var in vect]
        res=" ".join(vect)
        if file: file.write(res+"\n")
        else: print(res)
        
    def get_predicate_value(self,predicate,agent,possible_values):
        for poss_value in possible_values:
            if self.proposition_values[(predicate,agent,poss_value)]:return poss_value
        return "none"
    
    def apply_values(self,props_values):
        for (proposition,value) in props_values:
            self.proposition_values[proposition]=value
            