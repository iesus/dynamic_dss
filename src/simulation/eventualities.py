'''
%        Copyright 2022 Jesús Calvillo <jescalvillot@gmail.com>
%
%      Licensed under the Apache License, Version 2.0 (the "License");
%      you may not use this file except in compliance with the License.
%      You may obtain a copy of the License at
%
%           http://www.apache.org/licenses/LICENSE-2.0
%
%     Unless required by applicable law or agreed to in writing, software
%     distributed under the License is distributed on an "AS IS" BASIS,
%     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%     See the License for the specific language governing permissions and
%     limitations under the License.
'''

import copy
              
class Eventuality_Type:
    '''
    Provides a definition of a type of eventuality. An object of this type can generate "Eventuality" objects, which are specific instances of eventualities.
    Here we provide a range of parameters in which a particular eventuality can fall. 
    '''
    def __init__(self, name, aspectual_type, duration_mean=1,duration_var=0, rols={}, reqs={}, init_conseqs={}, interrupts_agent=False, interrupts_patient=False):
        self.name = name
        self.aspectual_type=aspectual_type
        self.duration_mean=duration_mean
        self.duration_variation=duration_var
        self.roles=copy.deepcopy(rols)
        self.probability_distro=None
        self.dependencies=[]
        self.requirements=copy.deepcopy(reqs) #propositions that need to be true/false in the current or previous formal model
        self.consequences=copy.deepcopy(init_conseqs)#propositions that are entailed to be true/false in the current or the next formal model
        self.interrupts_patient=interrupts_patient #this is true if the ev_type interrupts the activities of other participants (e.g. hitting interrupts whomever gets hit)
        self.interrupts_agent=interrupts_agent #this means the predicate interrupts whoever makes it true, e.g. fall
  
        #Depending on the aspectual type, each eventuality_type has different phases
        if self.aspectual_type in ["accomplishment"]:
            self.phases=["begin_","middle_","result_"]
        elif self.aspectual_type in ["culmination"]:
            self.phases=["begin_","result_"]
        else:self.phases=[]  #If the eventuality is a state , process or happening, there are no phases
    
    def print_me(self):
        '''
        Pretty prints the object, used for debugging.
        '''
        print(self.name)
        print(self.aspectual_type)
        print(self.roles)
        print(self.requirements)
        print(self.consequences)
        
    def add_role_fillers(self,role_name,fillers):
        '''
        Possible roles are: agent, patient and destination
        '''
        if role_name not in self.roles:self.roles[role_name]=copy.copy(fillers)
        else:self.roles[role_name].extend(fillers)
        
    def add_probability_distribution(self,distro):
        '''
        A distribution is a dictionary from conditional factors to a dictionary of output values.
        prob_distros["smile"]={0:0.6,1:0.4}
        prob_distros["eat"]={}
        prob_distros["eat"][(("p","eat","me","fries"),0,("p","eat","me","sandwich"),0)]    ={"fries":0.2, "sandwich":0.2, "none":0.6}
        prob_distros["eat"][(("p","eat","me","fries"),1,("p","eat","me","sandwich"),0)]    ={"fries":0.1, "sandwich":0.1, "none":0.8}
        prob_distros["eat"][(("p","eat","me","fries"),0,("p","eat","me","sandwich"),1)]    ={"fries":0.1, "sandwich":0.1, "none":0.8}
        '''
        one_value=list(distro.values())[0]
        one_key=list(distro.keys())[0]
        if isinstance(one_value,dict): #if the values are dictionaries, it means the keys are factors on which the eventuality depends
            ind=0
            while ind+2<=len(one_key):
                self.dependencies.append(one_key[ind])
                ind+=2
        #If it's not a dictionary it means that the eventuality does not have probabilistic factors (although it could still have requirements)
        self.probability_distro=distro

    def get_agent_phase_propositions(self,phase_predicate,agent):
        '''
        Given a predicate and an agent, generate all the possible combinations of the predicate with its phases.
        '''
        propositions=[]
        if len(self.roles)==1:#if it's a single place predicate 
            propositions.append((phase_predicate,agent.name))
        else: #we only have 2 place predicates at most
            if "destination" in self.roles: second_arguments=list(set(agent.locations) & set(self.roles["destination"]))
            if "patient" in self.roles: second_arguments=self.roles["patient"]        
            for argument in second_arguments:
                propositions.append((phase_predicate, agent.name,argument))
        return propositions
    
    def get_agent_propositions(self,agent):
        '''
        Given an agent generate the possible propositions for the current eventuality, with its phases 
        '''
        propositions=[]
        if self.phases:
            for phase in self.phases:
                phase_predicate=phase+self.name
                propositions.extend(self.get_agent_phase_propositions(phase_predicate, agent))
        else: propositions=self.get_agent_phase_propositions(self.name, agent) 
            
        return propositions 
        
    def get_probability_value(self,formal_models,agent_name,random_generator):
        '''
        Compute the probability of occurrence of the current eventuality type. Depending on this value,
        an instance of this eventuality may be created (an object of Eventuality)
        '''
        one_key=list(self.probability_distro.keys())[0]
        if not isinstance(one_key,tuple):
            return random_generator.choices(list(self.probability_distro.keys()),self.probability_distro.values())[0]
        else:
            dict_key=[]
            (previous_model,current_model)=formal_models
            for dependency in self.dependencies:    
                dict_key.append(dependency)
                
                proposition=list(dependency)
                proposition=[agent_name if val=="me" else val for val in proposition]
                if dependency[0]=="p":
                    dict_key.append(previous_model.proposition_values[tuple(proposition[1:])])
                else:dict_key.append(current_model.proposition_values[tuple(proposition)])
            
            
            prob_distro=self.probability_distro[tuple(dict_key)]
            new_object=random_generator.choices(list(prob_distro.keys()),prob_distro.values())[0]
            
            return new_object
            
            
    
class Eventuality_Effects:
    '''
    Container for information related to the effects of a given eventuality on othe next or current state of affairs.
    '''
    def __init__(self, eventuality):
        self.eventuality=eventuality
        self.new_locations={}     
        self.proposition_values=[]
        self.new_eventualities=[]
        self.interruptions=[]
        
class Eventuality:
    '''
    Each object of this class is an instance of an Eventuality_Type.
    '''
    def __init__(self,ev_type,initial_time,initial_location,random_generator, duration=False, roles={}, trajectory=None):
        self.type=ev_type
        self.initial_time=initial_time
        
        #If the total duration is not given as a parameter, it is a random variable with mean ev_type.duration_mean
        if not duration:self.duration=ev_type.duration_mean+random_generator.choice(range(-ev_type.duration_variation,ev_type.duration_variation+1))
        else: self.duration=duration
        
        self.initial_location=initial_location
        self.roles=copy.copy(roles)
        self.trajectory=trajectory
        
        
        proposition=[self.type.name]
        if "agent" in self.roles:       proposition.append(self.roles["agent"].name)
        if "patient" in self.roles:     proposition.append(self.roles["patient"].name)
        if "destination" in self.roles: proposition.append(self.roles["destination"].name)
        
        if ev_type.phases:
            self.phase=0
            proposition[0]=self.type.phases[self.phase]+proposition[0]
            self.proposition=tuple(proposition)
        else: 
            self.phase=-1 #This means there are no phases
            self.proposition=tuple(proposition)
        
        #Activating an eventuality means the participant cannot engage in the same one again
        if self.type.name in self.roles["agent"].current_abilities:
            self.roles["agent"].current_abilities.remove(self.type.name)
        
        
    def change_phase(self):
        '''
        As time passes by in the microworld, each eventuality changes their phase.
        '''
        if self.phase==-1: return 
        elif self.phase+1>=len(self.type.phases):print("there are no more phases")
        else:
            self.phase+=1
            new_prop=list(self.proposition)
            new_prop[0]=self.type.phases[self.phase]+self.type.name
            self.proposition=tuple(new_prop)
            
    #TODO: parameterize fall, hit, walk_to, drive_to, cross_street
    def get_effects(self,time_step):
        '''
        When an eventuality is created, or as time passes by, it can have effects on the state of affairs of the microworld,
        Here we monitor for those effects and return them in an Eventuality_Effects object.
        '''
        new_effects=Eventuality_Effects(self)
        time_lapsed = time_step - self.initial_time + 1 #current time inclusive (i.e. if this is the first step, it has been already 1 time step)
        
        #INTERRUPTIONS
        #When falling or hitting happens, the agent/patient needs to cancel their activities
        if self.type.name=="fall" and time_lapsed==2:new_effects.interruptions=[self.roles["agent"]]
        if self.type.name=="hit": new_effects.interruptions=[self.roles["patient"]]
            
        #MOVEMENT
        #When someone is walking or the bus is driving, depending on how much time has passed by, the agents need to change location
        if self.type.name in ["walk_to","drive_to"]:
            agent=self.roles["agent"]
            
            if time_lapsed%agent.speed==0: #If the agent is about to arrive somewhere
                next_step=int(time_lapsed/agent.speed)
                new_location=self.trajectory[next_step]
                new_ev=(("arrive",self.roles["agent"].name,new_location),0)
                new_effects.new_eventualities.append(new_ev)
                    
            if (time_lapsed-1)%agent.speed==0: #If we just started OR it is time to move to the next location...
            #if time_lapsed==1 or time_lapsed%agent.speed==0: #If we just started OR it is time to move to the next location...
                current_step=int((time_lapsed-1)/agent.speed)
                #print("lapsed:",time_lapsed,"speed:",agent.speed, "step:",current_step)
                new_location=self.trajectory[current_step]
                
                if new_location in ["jm_front","h_front"]:
                    if new_location=="jm_front":otherside="h_front"
                    else:otherside="jm_front"
                    
                    if otherside in self.trajectory and self.trajectory.index(otherside)>current_step:
                        jumps_required=len(self.trajectory[self.trajectory.index(new_location):self.trajectory.index(otherside)])
                        durat=self.roles["agent"].speed*jumps_required+1
                        new_ev=(("cross_street",self.roles["agent"].name),durat)
                        new_effects.new_eventualities.append(new_ev)
                
                if current_step: #if step>0, we move
                    new_place_prop=tuple(["place",self.roles["agent"].name,new_location])
                    new_effects.proposition_values.append((new_place_prop,1))
                    new_effects.new_locations[self.roles["agent"].name]=new_location
                    
                    previous_location=self.trajectory[current_step-1]
                    prev_place_prop=tuple(["place",self.roles["agent"].name,previous_location])
                    new_effects.proposition_values.append((prev_place_prop,0))
        
        #OTHER EFFECTS
        initial_effects=[]
        end_effects=[]
        #So far we handle consequences >during< the eventuality manuallly like in "walk_to" above
        for (conseq, value) in self.type.consequences:
            if conseq[0]=="b":relevant_effects=initial_effects#If the consequence concerns the beginning or end of this eventuality
            else: relevant_effects=end_effects
            
            ind=1
            prop=[conseq[ind]]
            for i in range(ind+1,len(conseq)):
                if conseq[i]=="me":         prop.append(self.roles["agent"].name)
                elif conseq[i]=="patient":  prop.append(self.roles["patient"].name)#elif conseq[i] in ["food","refreshment"]:prop.append(self.roles["patient"].name)
                elif conseq[i]=="location": prop.append(self.roles["destination"].name)
                else: prop.append(conseq[i])
            prop=tuple(prop)
            relevant_effects.append((prop,value))
            
        #Effects triggered at the beginning of eventuality
        if time_lapsed==1:
            for (prop,value) in initial_effects:
                if prop[0]!="place" and value==1:
                    new_effects.new_eventualities.append((prop,0)) #The zero here refers to the duration of the eventuality, it is not the false value in initial_effects
                else:new_effects.proposition_values.append((prop,value))

        #During the eventuality, we turn on the corresponding proposition
        #if time_step  < self.initial_time+self.duration:new_effects.proposition_values.append((self.proposition,1))
        if time_lapsed <= self.duration:
            new_effects.proposition_values.append((self.proposition,1))
        #Effects triggered after the eventuality is finalized
        else:
            for (prop,value) in end_effects:
                if prop[0]!="place" and value==1:new_effects.new_eventualities.append((prop,0))
                else:new_effects.proposition_values.append((prop,value))
        
        if time_lapsed==1 or time_lapsed+1==self.duration:#If we are at the beginning or one step before finishing the eventuality
            self.change_phase()
  
        return new_effects
    
    def print_me(self):
        print("\n\t"+self.type.name)
        print("initial time:"+str(self.initial_time))
        print("duration:"+str(self.duration))
        print("initial location:"+self.initial_location)
        if "agent"   in self.roles:print("agent:"+self.roles["agent"].name)
        if "patient" in self.roles:print("patient:"+self.roles["patient"].name)
        if "destination" in self.roles:print("destination: "+self.roles["destination"].name)
        print("")