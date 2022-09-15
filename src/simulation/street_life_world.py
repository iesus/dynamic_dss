
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

if __name__ == '__main__':

    import copy
    
    from microworld import Microworld
    from location_layout import Location_Map
    from eventualities import Eventuality_Type
    from participants import Participant, Thing
    
    import random  
    random.seed(10)
    
    world = Microworld()
    
    ###LOCATIONS###
    # jm_house -- jm_front -- intersection -- h_front -- h_house 
    #    [0,-2]      [0,-1]       [0,0]        [0,1]       [0,2]
    # intersection is the part of the street where people cross and where they can be hit by the bus
    # the street has this layout:    street_south --- intersection --- street_north
    #                                    [-1,0]             [0,0]            [1,0]
    location_names_coords = [("jm_house",(0,-2)), ("jm_front",(0,-1)),("intersection",(0,0)),("h_front",(0,1)),("h_house",(0,2)),
                             ("street_south",(-1,0)),("street_north",(1,0))]
    location_names=[name for (name,coord) in location_names_coords]
    
    location_map=Location_Map(location_names_coords)
 
    location_constraints={}
    location_constraints["people"]=["jm_house", "jm_front", "h_house", "h_front", "intersection"]
    location_constraints["vehicles"]=["street_north","street_south", "intersection"]
    
    for part_type in location_constraints.keys():location_map.set_trajectories(location_constraints[part_type])

    world.location_map=location_map          
    
    
    #ONTOLOGY
    ontology={}
    ontology["people"] = ["john", "mary", "henrietta"]
    ontology["vehicles"] = ["bus"]
    ontology["food"]=["fries","sandwich"]
    ontology["refreshments"]=["cola","tea"]
    
    #Here we establish where participants appear at the beginning of the simulation or after they "die"
    initial_locations={"john":"jm_house", "mary":"jm_house","henrietta":"h_house","bus":"street_north"}
    #Speeds have to be at least 3, so that even if a person moves to an adjacent place, there are still 3 phases 
    #(2 without actual movement, and the result where the person is in the desired location)
    speeds={"john":3, "mary":3,"henrietta":3,"bus":3}
    
    #Participants are entities that can be agents in the microworld
    participant_types=["people","vehicles"]
    for participant_type in participant_types:
        part_locations={loc_name:world.location_map(loc_name) for loc_name in location_constraints[participant_type]}
        
        for participant in ontology[participant_type]:
            new_participant=Participant(participant,participant_type,world,part_locations)
            new_participant.initial_location=initial_locations[new_participant.name]
            new_participant.speed=speeds[new_participant.name]
            
            world.participants[participant]=new_participant
            
    #So far "things" are things that can be patients of some verbs like drink or eat, they cannot start eventualities, so they don't need much functionality 
    thing_types=["food","refreshments"]
    for thing_type in thing_types:
        for thingy in ontology[thing_type]:
            world.things[thingy]=Thing(thingy,thing_type,world)
    
    
    ###EVENTUALITITES### 
    #(eventuality_name, duration_mean, duration_variation) duration_variation gives the range of values the eventuality can last (duration_mean+-duration_variation)
    #NOTE: mean_duration>variation  otherwise we end up with durations of 0 
    all_eventuality_types={}
    all_eventuality_types["state"]=[("stand",2,1),("glad",2,1),("sad",2,1)]
    all_eventuality_types["process"]=[("walk",2,1),("smile",1,0),("rain",3,1),("drive",3,1)]
    all_eventuality_types["happening"]=[("hit",1,0)]
    all_eventuality_types["culmination"]=[("arrive",2,0),("fall",2,0)]
    #The durations of walk_to, cross_street and drive_to depend on the distance, so the duration is not really relevant here
    all_eventuality_types["accomplishment"]=[("eat",4,1),("drink",4,1),("walk_to",4,1),("cross_street",5,2),("drive_to",5,1),]
                           
    for aspectual_type in all_eventuality_types.keys():
        for (ev_t,dur_mean,dur_variation) in all_eventuality_types[aspectual_type]:
            world.eventuality_types[ev_t]=Eventuality_Type(ev_t,aspectual_type,dur_mean,dur_variation)

    
    #LOCATIONS WHERE EACH PREDICATE/EVENTUALITY CAN BEGIN
    standard_people_initial_locations=["fall","glad","sad","smile","drink","eat","arrive"]
    for predicate in standard_people_initial_locations:
        world.eventuality_types[predicate].initial_locations=location_constraints["people"]
        
    world.eventuality_types["walk"].initial_locations=["jm_house","jm_front","h_front","h_house"]
    world.eventuality_types["cross_street"].initial_locations=["jm_front","h_front"]
    world.eventuality_types["stand"].initial_locations=["jm_house","jm_front","h_front","h_house"]
    world.eventuality_types["walk_to"].initial_locations=["jm_house","jm_front","h_front","h_house"]
    
    standard_vehicle_initial_locations=["drive","drive_to","arrive"]
    for predicate in standard_vehicle_initial_locations:
        world.eventuality_types[predicate].initial_locations=location_constraints["vehicles"]
    world.eventuality_types["hit"].initial_locations=["intersection"]
    
    world.eventuality_types["hit"].interrupts_patient=True
    world.eventuality_types["fall"].interrupts_agent=True
    
    #"me" stands for the agent's name
    #"any_location" means the requirement is fulfilled if at least for one location the proposition has the required value
    #"all_locations" is similar but with an all relationship
    world.eventuality_types["fall"].requirements=[(("walk","me"),1)]#if someone falls, they must have been walking
    world.eventuality_types["stand"].requirements=[(("place","me","intersection"),0),# one cannot stand at the intersection
                                                   (("walk","me"),0)] #and one cannot stand and walk at the same time
    #One cannot start walking if there is an standing, crossing the street or walking going on 
    world.eventuality_types["walk_to"].requirements=[(("stand","me"),0),(("walk","me"),0)]
                                                           #(("walk_to","me","all_locations"),0)]
    world.eventuality_types["smile"].requirements=[(("glad","me"),1)]#people only smile when they are glad
    world.eventuality_types["glad"].requirements=[(("sad","me"),0)]#one cannot be sad and glad simultaneously
    world.eventuality_types["sad"].requirements=[(("glad","me"),0)]
    #The decision of crossing the street can only happen if there isn't an ongoing walking
    #world.eventuality_types["cross_street"].requirements=[(("stand","me"),0), (("walk","me"),0)]
 

    #Some eventualities trigger other eventualities, when they begin (b) or end (e)
    world.eventuality_types["walk_to"].consequences=[(("b","walk","me"),1)]#, (("e","middle_walk_to","me","location"),1)]
    world.eventuality_types["cross_street"].consequences=[(("b","walk","me"),1)]
    world.eventuality_types["drive_to"].consequences=[(("b","drive","me"),1)]
    #We can also use "patient", similar to "me" to refer to the patient of the eventuality
    

    agent_predicates={}
    agent_predicates["people"]=["walk","stand","glad","sad","smile",
                       "cross_street","fall", "eat","drink","walk_to","arrive"]    
    agent_predicates["vehicles"]=["drive","drive_to","hit","arrive"]

    for agent_type,predicates in agent_predicates.items():
        for predicate in predicates:
            world.eventuality_types[predicate].add_role_fillers("agent",ontology[agent_type])
            
            for agent_string in ontology[agent_type]: #We also make a link from each participant to their eventualities
                world.participants[agent_string].abilities[predicate]=world.eventuality_types[predicate]
                world.participants[agent_string].current_abilities.append(predicate)
        
    world.eventuality_types["eat"].add_role_fillers("patient",ontology["food"])
    world.eventuality_types["drink"].add_role_fillers("patient",ontology["refreshments"])
    world.eventuality_types["hit"].add_role_fillers("patient",ontology["people"])
    world.eventuality_types["walk_to"].add_role_fillers("destination",location_constraints["people"])  
    world.eventuality_types["walk_to"].roles["destination"].remove("intersection")
    
    world.eventuality_types["drive_to"].add_role_fillers("destination",location_constraints["vehicles"])
    world.eventuality_types["arrive"].add_role_fillers("destination",location_names)
    

    for participant in world.participants.values():
        participant.get_possible_propositions()
        participant.current_possible_propositions=copy.deepcopy(participant.abilities)
        world.propositions.extend(participant.propositions)
    world.propositions.append(("rain",))

    #world.print_participants()
    #world.print_eventualities()
    #print(len(world.propositions))
    #world.print_propositions()
    
    ###PROBABILITIES###
    prob_distros={}
    
    #Rain only depends on whether it was raining at the previous time step
    prob_distros["rain"]={}
    prob_distros["rain"][(("p","rain"),1)]  ={0:0.3, 1:0.7}
    prob_distros["rain"][(("p","rain"),0)]  ={0:0.7, 1:0.3}
    
    prob_distros["smile"]={0:0.6,1:0.4}
    
    prob_distros["eat"]={}
    prob_distros["eat"][(("p","result_eat","me","fries"),0,("p","result_eat","me","sandwich"),0)]  ={"fries":0.2, "sandwich":0.2, "none":0.6}
    prob_distros["eat"][(("p","result_eat","me","fries"),1,("p","result_eat","me","sandwich"),0)]  ={"fries":0.1, "sandwich":0.1, "none":0.8}
    prob_distros["eat"][(("p","result_eat","me","fries"),0,("p","result_eat","me","sandwich"),1)]  ={"fries":0.1, "sandwich":0.1, "none":0.8}
    
    prob_distros["drink"]={}
    prob_distros["drink"][(("p","result_drink","me","cola"),0,("p","result_drink","me","tea"),0)]  ={"cola":0.15,"tea":0.15,"none":0.7}
    prob_distros["drink"][(("p","result_drink","me","cola"),1,("p","result_drink","me","tea"),0)]  ={"cola":0.1, "tea":0.2, "none":0.7}
    prob_distros["drink"][(("p","result_drink","me","cola"),0,("p","result_drink","me","tea"),1)]  ={"cola":0.2, "tea":0.1, "none":0.7}
    
    #People's mood only depends on the current weather and the person's mood at the previous time step
    prob_distros["glad"]={}
    prob_distros["sad"]={}
    
    prob_distros["glad"][(("rain",),1,("p","glad","me"),1,("p","sad", "me"),0)]     ={0:0.6, 1:0.4}
    prob_distros["sad"] [(("rain",),1,("p","glad","me"),1,("p","sad", "me"),0)]     ={0:0.6, 1:0.4}
    
    prob_distros["glad"][(("rain",),1,("p","glad","me"),0,("p","sad", "me"),1)]     ={0:0.8, 1:0.2}
    prob_distros["sad"] [(("rain",),1,("p","glad","me"),0,("p","sad", "me"),1)]     ={0:0.4, 1:0.6}
    
    prob_distros["glad"][(("rain",),1,("p","glad","me"),0,("p","sad", "me"),0)]     ={0:0.7, 1:0.3}
    prob_distros["sad"] [(("rain",),1,("p","glad","me"),0,("p","sad", "me"),0)]     ={0:0.5, 1:0.5}
    
    prob_distros["glad"][(("rain",),0,("p","glad","me"),1,("p","sad", "me"),0)]     ={0:0.4, 1:0.6}
    prob_distros["sad"] [(("rain",),0,("p","glad","me"),1,("p","sad", "me"),0)]     ={0:0.8, 1:0.2}
        
    prob_distros["glad"][(("rain",),0,("p","glad","me"),0,("p","sad", "me"),1)]     ={0:0.6, 1:0.4}
    prob_distros["sad"] [(("rain",),0,("p","glad","me"),0,("p","sad", "me"),1)]     ={0:0.6, 1:0.4}
            
    prob_distros["glad"][(("rain",),0,("p","glad","me"),0,("p","sad", "me"),0)]     ={0:0.4,1:0.6}
    prob_distros["sad"] [(("rain",),0,("p","glad","me"),0,("p","sad", "me"),0)]     ={0:0.8,1:0.2}
    
    #Falling depends on the current weather
    prob_distros["fall"]={}
    prob_distros["fall"][(("rain",),1)]  ={0:0.8, 1:0.2}
    prob_distros["fall"][(("rain",),0)]  ={0:0.9, 1:0.1}
    
    prob_distros["stand"]       ={0:0.6,1:0.4}
    prob_distros["walk_to"]={"jm_house":0.18, "jm_front":0.18, "h_house":0.18, "h_front":0.18, "none":0.28}
    prob_distros["drive_to"]    ={"street_north":0.2,"street_south":0.2, "intersection":0.2, "none":0.4}
     
    #As with falling, the bus is more likely to hit people if it's raining
    prob_distros["hit"]={}
    prob_distros["hit"][(("rain",),1)]  ={0:0.5, 1:0.5}
    prob_distros["hit"][(("rain",),0)]  ={0:0.7, 1:0.3}
    
    world.set_probability_distros(prob_distros)
  
    #We let the world run for n=30,000 time steps
    models=world.run(30000,random)
    
    #Then we save the generated observations into files
    
    with open("../outputs/street_life_model/street_life30K.observations",'w') as output_file:
        models[0].print_basic_propositions(file=output_file) 
        for model in models: model.print_binary_vector(file=output_file)
    
    #The file street_life.observations can be used to test that nothing has changed during refactoring:
    #If something changes, the output with random seed=10 would be different
    
    exit()
    #The files that can be generated below are quite verbosed, so they are mostly used for debugging because they can become huge if we sample say 10,000 observations
    with open("../outputs/street_life_model/formal_models1000.txt",'w') as output_file: 
        for model in models:
            model.print_me(only_true=False,file=output_file)
            output_file.write("\n")
            
    with open("../outputs/street_life_model/formal_models_onlytrue1000.txt",'w') as output_file: 
        for model in models:
            model.print_me(file=output_file)
            output_file.write("\n")
            