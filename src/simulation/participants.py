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


from eventualities import Eventuality

class Thing:
    def __init__(self,name,category,microworld):
        self.name=name
        self.category=category
        self.microworld=microworld


class Participant:
    def __init__(self, name,category,microworld, locations):
        self.name = name
        self.category=category #what category they are in the onthology
        self.microworld=microworld #we link the participant to the world it lives in
        
        self.abilities = {}  # what they can do
        self.propositions=[] # propositions where they are the agent
        self.locations = locations  # where they can be
        self.current_location=None
        self.current_abilities=[] #eventualities the participant can initiate at the current time
        
        self.initial_location=None #The location where the participant always appears initially
        self.interrupted=False #If the participant falls or is hit by the bus, this flag becomes true
        
    def print_me(self):
        print(self.name,self.category)
        print("Abilities:")
        for ab in self.abilities.keys():print("\t"+ab)
        print("Locations")
        for loc in self.locations:print("\t"+loc)
        print("Propositions")
        for prop in self.propositions:print("\t"+str(prop))
        
    def get_possible_propositions(self):
        propositions=[]
        for location in self.locations:propositions.append(("place",self.name,location))

        for eventuality_type in self.abilities.values():
            propositions.extend(eventuality_type.get_agent_propositions(self))
            
        self.propositions=propositions  
        
        
    def initialize(self,current_formal_model):
        '''
        A participant is initialized by being placed in their self.initial_location doing NOTHING
        We can add later further propositions to be true at initialization, however since propositions are 
        related to eventualities, it is better to add them while runnning the microworld rather than during initialization
        in order to be properly added to the agenda
        '''
        propositions=[]
        self.current_location=self.initial_location
        self.microworld.location_map(self.current_location).participants.append(self)
        for location in self.locations:
            propositions.append((("place",self.name,location),0))
            
        propositions.append((("place",self.name,self.current_location),1))
        
        for (prop,val) in propositions:
            current_formal_model.proposition_values[prop]=val
            
            
    def reset_propositions(self, current_formal_model, given_propositions=None):
        '''
        Turns all propositions related to the participant to 0, except the current location
        the current_location is set to the initial_location (but the proposition is not updated yet, that is done by the microworld run
        in the next time step)
        '''
        self.microworld.relocate_participant(self,self.initial_location)
        if given_propositions:prop_vals=[(proposition,0) for proposition in given_propositions]
        
        else:
            prop_vals=[(proposition,0) for proposition in self.propositions]
            prop_vals.append((("place",self.name,self.current_location),1))
        
        for (prop,val) in prop_vals:current_formal_model.proposition_values[prop]=val


    def return_abilities(self, current_new_eventualities):
        for eventuality in current_new_eventualities:
            if eventuality.type.name not in self.current_abilities:
                self.current_abilities.append(eventuality.type.name)
        
            
    
    def get_current_possible_abilities(self,formal_models):
        '''
        Returns the abilities that are allowed by the current state of affairs
        '''
        #current_abilities is the set of self.abilities minus those that are currently ongoing
        potential_allowed=list(self.current_abilities)
       
        not_allowed=[]
        for potential in potential_allowed:
            if not self.possible_predicate(formal_models, potential):
                not_allowed.append(potential)
                    
        for bad in not_allowed:potential_allowed.remove(bad)
        
        return potential_allowed
    
    def possible_predicate(self,formal_models, predicate):
        '''
        Receives a predicate and checks if it's possible given the current and previous formal models
        '''
        #First we check if the current location allows to begin the predicate
        if self.current_location not in self.abilities[predicate].initial_locations:
            return False
        
        for (req,val) in self.abilities[predicate].requirements:
            if req[0]=="p": #If the requirement concerns the previous time step
                req=req[1:]
                relevant_model=formal_models[0] #the model at the previous time
            else: relevant_model=formal_models[1]#the current time step model
                  
            prop=[req[0]]          
            if len(req)>1:
                if req[1]=="me":prop.append(self.name)
                else: prop.append(req[1])
                
                if len(req)>2:
                    second_arg=req[2]
                    
                    if second_arg.startswith("all_"):
                        sec_type=second_arg[4:]
                        if sec_type=="locations":possibles=self.locations
                        else:possibles=[f.name for f in self.microworld.things.values() if f.category==sec_type]
                        
                        for possib in possibles:
                            new_prop=tuple(prop+[possib])
                            if relevant_model.proposition_values[new_prop]!=val:return False
                            second_arg=possib
                    
                    if second_arg=="any_location":
                        checked=[]
                        for loc in self.locations:
                            propl=tuple(prop+loc)
                            if relevant_model.proposition_values[propl]==val:
                                second_arg=loc
                                break
                            else: checked.append(loc)
                        if len(checked)==len(self.locations): return False
                    prop.append(second_arg)
                        
            prop=tuple(prop)       
            if relevant_model.proposition_values[prop]!=val:return False
            
        return True
   
        
    
    def start_eventualities(self,formal_models,random_generator):
        '''
        It iterates over the set of possible eventualities that the participant can start, and starts some of them probabilistically
        THIS METHOD IS TAILORED TO THE STREET_LIFE MICROWORLD
        '''
     
        current_model=formal_models[1]
        potential_abilities=self.get_current_possible_abilities(formal_models)
        random_generator.shuffle(potential_abilities)
        new_eventualities=[]
         
        for predicate in potential_abilities:
            if self.abilities[predicate].probability_distro is not None: #If the predicate does not have a probability distro attached to it, 
                #it means it cannot be initiated by the participant and it is more like a side effect of some other predicate
                if not self.possible_predicate(formal_models, predicate):continue 
                #If the predicate has become impossible given the developing state of affairs, we ignore it
                
                #If its a hit, a person needs to be at the intersection
                if predicate=="hit":
                    people_intersection=[part.name for part in self.microworld.location_map("intersection").participants if part.category=="people"]
                    hitting=self.abilities[predicate].get_probability_value(formal_models,self.name,random_generator)
                    
                    if people_intersection and hitting: #If there are people at the intersection and the bus is actually hitting
                        new_argument_string=random_generator.choice(people_intersection) #we choose someone to get hit
                    else:continue
                
                else:new_argument_string=self.abilities[predicate].get_probability_value(formal_models,self.name,random_generator)
                
                if not new_argument_string or new_argument_string=="none":continue #none value means the eventuality is not happening now
                   
                if "patient" in self.abilities[predicate].roles:  
                    if new_argument_string in self.microworld.things.keys(): new_argument=self.microworld.things[new_argument_string]
                    else:new_argument=self.microworld.participants[new_argument_string]
                    
                    new_eventuality=Eventuality(self.abilities[predicate],current_model.time,self.current_location,random_generator,roles={"agent":self,"patient":new_argument})
                        
                elif "destination" in self.abilities[predicate].roles:
                    while new_argument_string==self.current_location or new_argument_string== "none": 
                        #If the new destination is our current location, we need to choose another one that is not none
                        new_argument_string=self.abilities[predicate].get_probability_value(formal_models,self.name,random_generator)
                    
                    new_argument=self.microworld.location_map(new_argument_string)
                    trajectory=self.locations[self.current_location].paths[new_argument_string]  
                    durat=(len(trajectory)-1)*self.speed+1# we only take 1 step for the reaching of the final destination
                    new_eventuality=Eventuality(self.abilities[predicate],current_model.time,self.current_location,random_generator,
                                    duration=durat, roles={"agent":self,"destination":new_argument}, trajectory=trajectory)
                
                #If it's a single place predicate (e.g. glad, sad, fall)  
                else:new_eventuality=Eventuality(self.abilities[predicate], current_model.time, self.current_location,random_generator, roles={"agent":self})
                
                new_effect_eventualities=self.microworld.apply_eventuality_effects(new_eventuality, current_model,random_generator)
                new_eventualities.extend(new_effect_eventualities)
                new_eventualities.append(new_eventuality)

        
        if self.category=="people" and \
           current_model.proposition_values[("walk",self.name)]==0 and \
           current_model.proposition_values[("begin_fall",self.name)]==0 and \
           current_model.proposition_values[("stand",self.name)]==0:
            #If a person is not walking, falling or standing, we make them stand
            
            new_eventuality=Eventuality(self.abilities["stand"], current_model.time, self.current_location,random_generator, roles={"agent":self})   
            new_effect_eventualities=self.microworld.apply_eventuality_effects(new_eventuality, current_model,random_generator)
            new_eventualities.extend(new_effect_eventualities)
            new_eventualities.append(new_eventuality)

        return new_eventualities
        