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
Created on March, 3rd 2022

@author: jesus calvillo
'''
from copy import deepcopy


class Location:
    def __init__(self, name,coords):
        self.name = name
        self.coords=coords
        self.paths={}
        self.participants=[]
    
    def __call__(self):
        return self.name
        
    def print_me(self):
        print(self.name)
        print(self.coords)
        print(self.paths)
        
class Location_Map:
    def __init__(self, names_coords):
        self.locations={}
        self.location_coordinates={}
        
        for (name,coords) in names_coords:
            self.locations[name]=Location(name,coords)
            self.location_coordinates[coords]=name
            
    def __call__(self,location_name):
        return self.locations[location_name]
    
    def print_locations(self):
        for loc in self.locations.values():loc.print_me()
            
    def get_trajectory(self, initial_position, destination):
        '''
        Given 2 coordinates in a 2D discrete plane, give one possible trajectory to go from initial_position to destination
        '''
        curr_pos=list(initial_position)#We just make sure that the positions are lists and not tuples
        destination=list(destination)
        
        trajectory=[deepcopy(curr_pos)]
        while curr_pos != destination:
            #Vertical movements
            if curr_pos[0]!=destination[0]:
                if curr_pos[0]>destination[0]: #If current position is above destination
                    curr_pos[0]+=-1
                elif curr_pos[0]<destination[0]:# current position is below destination
                    curr_pos[0]+=1
                trajectory.append(deepcopy(curr_pos))
                
            #Horizontal movements
            if curr_pos[1]!=destination[1]:
                if curr_pos[1]>destination[1]: #If current position is to the right of destination
                    curr_pos[1]+=-1
                elif curr_pos[1]<destination[1]:# current position is to the left of destination
                    curr_pos[1]+=1
                trajectory.append(deepcopy(curr_pos))
        
        return trajectory
    
    def set_trajectories(self,connected_locations):
        '''
        Given a set of locations from which each pair can be connected, attach trajectories between all locations
        '''
        for i in range(len(connected_locations)):
            for j in range(len(connected_locations)):
                if i==j:continue
                initial=self.locations[connected_locations[i]].coords
                final  =self.locations[connected_locations[j]].coords
                trajectory=self.get_trajectory(initial, final)
                trajectory_names=[self.location_coordinates[tuple(step)] for step in trajectory]
                self.locations[trajectory_names[0]].paths[trajectory_names[-1]]=trajectory_names
                
                
if __name__=="__main__":
    
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
                
                
    print(location_map.locations["jm_front"].paths)

            