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

'''
Created on Jan 25, 2022

@author: jesus calvillo
'''
import copy
from formal_model import Formal_Model
from eventualities import Eventuality


class Microworld(object):
    '''
    An entity that contains participants, things, locations, and where eventualities occur. 
    With the "run" method, we can let the microworld run n timesteps, generating n observations.
    ''' 
    def __init__(self):
        self.participants = {}
        self.things={}
        self.location_map=None
        self.eventuality_types={}
        self.propositions=[]
        self.probability_distros={}
        self.eventuality_agenda=[]
    
    def print_participants(self):
        for par in self.participants.values():par.print_me()    
        
    def print_eventualities(self):
        for ev in self.eventuality_types.values():ev.print_me()
        
    def print_propositions(self):
        for prop in self.propositions:
            if len(prop)==1:print(prop[0]+"()")
            elif len(prop)==2:print(prop[0]+"("+prop[1]+")")
            elif len(prop)==3:print(prop[0]+"("+prop[1]+","+prop[2]+")")
            
    def set_probability_distros(self, probability_distros):
        self.probability_distros=probability_distros
     
        for ev_type_name, prob_distro in probability_distros.items():
            self.eventuality_types[ev_type_name].add_probability_distribution(prob_distro)
    
    def relocate_participant(self,participant,new_location):
        '''
        Moves a participant to a different location.
        '''
        self.location_map(participant.current_location).participants.remove(participant)
        participant.current_location=new_location
        self.location_map(new_location).participants.append(participant)
        

    def apply_eventuality_effects(self,eventuality,formal_model,random_generator,effects=None):
        '''
        Apply the effects of a given eventuality into the current state of affairs.
        Returns a list of new eventualities that are to be created (if any).
        '''
        if effects is None: effects=eventuality.get_effects(formal_model.time)
        
        #Interruptions are not handled here.
        #There are 2 types of interruptions: by hitting or falling. Hitting is handled in the main run method, when we check if patients are interrupted
        #Falling occurs in 2 time steps, in the first one people start to fall, while their other activities may continue
        #In the second time step, the interruptions occur, that's why the interruption is handled also in the run method before the participants create new eventualities

        formal_model.apply_values(effects.proposition_values)
        for part,new_loc in effects.new_locations.items():self.relocate_participant(self.participants[part], new_loc)
            
        new_eventualities=[]
        for (prop,duration) in effects.new_eventualities:
            ev_type=self.eventuality_types[prop[0]]
            initial_time=formal_model.time
            roles={"agent":self.participants[prop[1]]}
            if len(prop)>2:
                if "patient" in ev_type.roles.keys():
                    second_role="patient"
                    #Patients can be people or things
                    if prop[2] in self.things.keys():second_argument=self.things[prop[2]]
                    else: second_argument=self.participants[prop[2]]
                                
                else: 
                    second_role="destination"
                    second_argument=self.location_map(prop[2])
                    
                roles[second_role]=second_argument
            initial_location=self.participants[prop[1]].current_location    
        
            if duration!=0: #If duration is not 0, it means it was predefined and passed as a parameter 
                new_eventuality=Eventuality(ev_type,initial_time,initial_location,random_generator,duration=duration, roles=roles) 
                
            elif initial_time==eventuality.initial_time:#If the effect begins with the original eventuality, it has the same duration,
                new_eventuality=Eventuality(ev_type,initial_time,initial_location,random_generator,duration=eventuality.duration, roles=roles)
                
            else:#otherwise it follows its random distribution
                new_eventuality=Eventuality(ev_type,initial_time,initial_location,random_generator, roles=roles)
            
            new_eventualities.append(new_eventuality)
            new_triggered_eventualities=self.apply_eventuality_effects(new_eventuality, formal_model,random_generator)
            new_eventualities.extend(new_triggered_eventualities)
            
        return new_eventualities
    
    def deactivate_participant_eventualities(self,participant,agenda,indices=None):
        '''
        Creates a boolean list of indices signaling the eventualities in the agenda where the participant is NOT the agent,
        deactivating (assigning them to 0) those where the participant is the agent.
        At the same time the abilities are returned to the participant, so they can initiate new eventualities of those types.
        This cancels ONGOING eventualities.
        '''
        if indices is None:indices=[1 for i in range(len(agenda))]
                        
        for ev_index in range(len(agenda)):
            if agenda[ev_index].roles["agent"].name==participant.name:
                indices[ev_index]=0
                if agenda[ev_index].type.name not in participant.current_abilities:
                    participant.current_abilities.append(agenda[ev_index].type.name)
        return indices
    
    def cancel_new_participant_eventualities(self,participant,new_agenda):
        '''
        Similar to the method above, except that here the eventualities are cancelled before they begin, when they are still
        in the agenda for the next time step.
        '''
        new_new_agenda=[]   
        for ag_eventuality in new_agenda:
            if ag_eventuality.roles["agent"].name!= participant.name: new_new_agenda.append(ag_eventuality)
            elif ag_eventuality.type.name not in participant.current_abilities:
                participant.current_abilities.append(ag_eventuality.type.name)       
        return new_new_agenda
    
    def run(self,time_steps,random_generator):
        '''
        Returns a list of observations with lenght==time_steps. 
        It initializes the microworld and incrementally (one step at a time) generates the required observations.
        Each observation depends on the previous ones.
        '''
        
        previous_formal_model=Formal_Model(0,self.propositions)
        
        previous_formal_model.proposition_values[("rain",)]=random_generator.choice([0,1])#initial weather
        #we put the participants in their initial location/home
        for part in self.participants.values():part.initialize(previous_formal_model)
    
        previous_formal_model.print_me()
        all_formal_models=[previous_formal_model]
        #Then we let the world "run" for n-1 time steps (step 0 was the initialization)  
        self.eventuality_agenda=[]      
        for time_step in range(1,time_steps):
            new_formal_model=Formal_Model(time_step,self.propositions) 
            
            #We set the weather:
            new_rain=self.eventuality_types["rain"].get_probability_value([previous_formal_model, new_formal_model],"none",random_generator)
            new_formal_model.proposition_values[("rain",)]=new_rain
            
            #We put each participant in their current location:
            for participant in self.participants.values():
                new_formal_model.proposition_values[("place",participant.name,participant.current_location)]=1
            
            #then we process items in the agenda
            new_agenda=[]
            active=[1 for i in range(len(self.eventuality_agenda))] #This is a flag, an eventuality can become inactive due to another eventuality that causes an interruption
            for i in range(len(self.eventuality_agenda)):
                if active[i]:
                    
                    eventuality=self.eventuality_agenda[i]
                    ev_effects=eventuality.get_effects(time_step)     
                    for partic in ev_effects.interruptions:
                        partic.reset_propositions(new_formal_model)
                        #We deactivate all the evts in the previous agenda related to that participant (so that they are no longer processed)
                        active=self.deactivate_participant_eventualities(partic, self.eventuality_agenda, active)
                        #We remove from the new agenda, the evts related to that participant that might have been initiated 
                        new_agenda=self.cancel_new_participant_eventualities(partic, new_agenda)
                        partic.interrupted=True #We don't let the interrupted participant initiate evnts in this time step
                    
                    possibly_new_eventualities=self.apply_eventuality_effects(eventuality,new_formal_model,random_generator,ev_effects)
                    new_agenda.extend(possibly_new_eventualities)
                    
                    if eventuality.initial_time + eventuality.duration > time_step: #If the eventuality hasn't finished yet
                        new_agenda.append(eventuality)
                    elif eventuality.type.name not in eventuality.roles["agent"].current_abilities: #If it finished, we give the ability to the participant back
                        eventuality.roles["agent"].current_abilities.append(eventuality.type.name)
                        
            #Then we let each participant start eventualities
            participants=list(self.participants.values())
            random_generator.shuffle(participants)   
            for i in range(len(participants)):
                participant =participants[i]
                #We ignore participants that fell or were hit in the current time step
                if participant.interrupted:
                    participant.interrupted=False
                    continue
                
                new_eventualities=participant.start_eventualities([previous_formal_model,new_formal_model],random_generator)
                
                caused_interruptions=[ev for ev in new_eventualities if ev.type.interrupts_patient] #hitting occurs in a single time step, therefore the effects are immediate
                for interr in caused_interruptions:
                    patient=interr.roles["patient"]
                    if patient.interrupted: continue
                    new_agenda=self.cancel_new_participant_eventualities(patient, new_agenda)
                    patient.reset_propositions(new_formal_model)
                    
                    part_index=participants.index(patient)
                    if part_index>i: patient.interrupted=True

                new_agenda.extend(new_eventualities)
        
            self.eventuality_agenda=new_agenda    
            
            all_formal_models.append(new_formal_model)
            previous_formal_model=new_formal_model
            
            new_formal_model.print_me()
        
        return all_formal_models

            
            
if __name__ == '__main__':

    world = Microworld()

        
        
    