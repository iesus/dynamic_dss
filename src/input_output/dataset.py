import numpy as np
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import itertools
import pickle
import torch

from dataclasses import dataclass
from typing import List, Optional, Generator

@dataclass
class Training_Element: 
    '''
    Single unit used for training. Each Training_Element is related to one sentence in the corpus.
    Contains the semantic representation, a list of other Training_Elements with equivalent semantics, among other information
    '''  
    sentence: str
    semantics: str           #semantic representation in propositional logic
    vector: List[float]
    #w_indices: List[int] not added at initialization, contains the sentence converted to indices in the vocabulary
    #equivalent_sentences #Attribute added not on initialization, contains other Training Elements with the same semantic vector
        
    def print_me(self):
        print(self.sentence)
        print(self.semantics)
        print(self.vector)
        
@dataclass
class Situation:
    '''
    A situation refers to a semantic representation. It is usually linked to several sentences (Training_Elements)
    ''' 
    vector: List[float] #semantic vector related to the situation
    elements: List[Training_Element]


def one_hot_encoding(value: str,
                     possible_values: List[str]
                    ) -> List[int]:
    """ Encode a single label into a one-hot vector given a sorted list of all
        possible values.

              value: A single label
    possible_values: All labels, including the given one
    """
    return [1 if i == value else 0 for i in possible_values]

def index_2_one_hot(ind: int,
                    length: int
                    )->List[int]:
    '''
    Converts an index into a one-hot vector with the given length
    '''
    return [1 if i ==ind else 0 for i in range(length)]
    
    

def load_prolog_situation_space_matrix(filename):
    '''
    Loads the file containing the situation space matrix concatenating the vectors of the basic propositions
    Returns also a list containing all basic propositions
    '''
    situation_matrix=[]
    
    with open(filename,'r') as file:
        basic_props = file.readline().split()
        
        for line in file:
            vector=[int(x) for x in line.split()]
            situation_matrix.append(vector)    
        situation_matrix=np.asarray(situation_matrix)
    
    return situation_matrix,basic_props

def print_prior_probs(matrix,basic_props):
    #Each row in the matrix (matrix.shape[0])is one observation, each column is one basic proposition (matrix.shape[1])
    for i in range(matrix.shape[1]):
        prior=np.sum(matrix[:,i])/matrix.shape[0]
        print(i,basic_props[i],prior)
        
        
def get_web_heatmap(data,x_labels,y_labels,graph_title,x_title="X",y_title="Y",filename=""):

    fig = go.Figure(data=go.Heatmap(
                       z=data,
                       x=x_labels,
                       y=y_labels,
                       colorscale="hot",
                       hoverongaps = False))
    
    fig.update_layout(
        title=graph_title,
        xaxis_title=x_title,
        yaxis_title=y_title)
    
    if filename: fig.write_html(filename)
    else:fig.show()
    

def get_conditional_joint_probs(matrix):
    condps=np.zeros((matrix.shape[1],matrix.shape[1]), dtype=float)
    jointps=np.zeros((matrix.shape[1],matrix.shape[1]), dtype=float)

    for i in range(matrix.shape[1]):
        for j in range(matrix.shape[1]):
            intersection=np.dot(matrix[:,i],matrix[:,j])
            jointp=intersection/matrix.shape[0]
            if np.sum(matrix[:,i])>0:condp=intersection/np.sum(matrix[:,i])
            else: condp=0
            #print(basic_props[i],basic_props[j],jointp,condp)
            jointps[i,j]=jointp
            condps[i,j]=condp
    
    return jointps,condps


def slide_time(vector,timesteps):
    '''
    Given a binary vector with ordered values, moving in time can be performed by sliding the vector to the left (back in time) or to the right (future)
    timesteps: # of steps we go backward (if <0) or forward (if >0)
    '''
    #Going backwards we slide the vector to the left (removing the values at the beginning) and pad with zeros at the end
    if timesteps<0:
        vector=vector[timesteps*-1:]
        vector=np.pad(vector, (0,timesteps*-1),'constant')
    #Going forwards we slide the vector to the right (removing the values at the end) and adding zeros at the beginning
    elif timesteps>0:
        vector=vector[:-timesteps]
        vector=np.insert(vector,0,[0]*timesteps)
    
    return vector

def dss_jointp(vector_A,vector_B):
    intersection=np.dot(vector_A,vector_B)
    return intersection/len(vector_A)

def dss_condp(vector_A,given_vector_B):
    prior_B=np.sum(given_vector_B)
    if prior_B==0:return 0
    
    intersection=np.dot(vector_A,given_vector_B)
    return intersection/prior_B
            
            
#############################################################################################################
#### LOAD AND OBTAIN CORPUS FROM RAW PROLOG-OUTPUT FILES
#############################################################################################################
def load_prolog_corpus_belief(input_path, matrix_path,output_filename):
    '''
    Takes a file containing the output of the prolog file with dss-sentences and the full 30K situation vectors
    Returns a list of TrainingElement instances, where each of the latter is a sentence with its information
    It computes the belief vector directly and puts it into each TrainingElement
    '''
    dss_matrix,basic_props=load_prolog_situation_space_matrix(matrix_path)
    
    map_sentence_training_elem={}
    corpus=[]  
    impossible_corpus=[] #Contains sentences of situations that are not allowed by the microworld or that never occurred during sampling
    with open(input_path,'r') as prolog_corpus_file:
        sentence_line=prolog_corpus_file.readline().strip()
        
        while sentence_line:
            sentence_line=sentence_line.replace("\"","")
            sentence_line=sentence_line.replace("women was","women were")
            sentence_line+=" ."
            print(sentence_line)
            
            semantics_line=prolog_corpus_file.readline().strip()
            print(semantics_line)
            
            vector_line=prolog_corpus_file.readline().strip()
            vector_line=[int(x) for x in vector_line.split()]
            vector_line=np.asarray(vector_line)
            print(vector_line)
            
            training_item=Training_Element(sentence_line,semantics_line,vector_line)
            map_sentence_training_elem[sentence_line]=training_item
                 
            training_item.belief_vector=np.dot(vector_line,dss_matrix)
            prior_v=np.sum(vector_line)
            if prior_v:
                training_item.belief_vector=training_item.belief_vector/prior_v
                corpus.append(training_item)
            else:impossible_corpus.append(training_item)
                
            print(training_item.belief_vector)
            sentence_line=prolog_corpus_file.readline().strip()
            
    #Get the vocabulary
    all_sents=[te.sentence for te in corpus]
    vocab=list(set(itertools.chain.from_iterable(map(str.split, all_sents))))
    vocab=["pad"]+vocab
    
    #Convert sentences to sequences of indices
    for te in corpus:te.w_indices=[vocab.index(word) for word in te.sentence.split()]
    for te in impossible_corpus: te.w_indices=[vocab.index(word) for word in te.sentence.split()] 
    #We assume the vocabulary in impossible corpus is fully contained in corpus
    
    with open(output_filename, 'wb') as f:
        pickle.dump(corpus, f)
        pickle.dump(impossible_corpus,f)
        pickle.dump(map_sentence_training_elem,f)
        pickle.dump(vocab,f)
        pickle.dump(basic_props,f)
    
    return corpus,impossible_corpus,map_sentence_training_elem,vocab,basic_props

def get_collapsed_corpus(normal_corpus):
    '''
    Takes a list of TrainingElement instances, obtained from load_prolog_corpus_belief
    Puts all semantically equivalent sentences into one Situation object, which is also put into a list
    '''
    collapsed_corpus=[]
    for training_element in normal_corpus:
        match=False
        for situation in collapsed_corpus:
            if np.array_equal(situation.vector,training_element.vector):
                match=True
                situation.elements.append(training_element)
                break
                            
        if not match:
            new_situation=Situation(training_element.vector,[training_element])
            collapsed_corpus.append(new_situation)
            
    return collapsed_corpus

def get_corpus_sentence_observations(corpus_belief, obs_matrix,max_obs=300):
    '''
    Having a corpus obtained with load_prolog_corpus_belief, which is a list of TrainingElement with their semantic vectors,
    and a matrix of observations ( a list of observations), we build a corpus where each sentence is paired to each observation where that sentence is true
    (if the sentence is true in 20 observations, there will be 20 pairs sentence-observation)
    Some sentences are related to a very large number of observations, that's why we set a maximum (max_obs)
    '''
    import copy
    print(len(corpus_belief))
    print(len(obs_matrix))
    
    corpus_sent_obs=[]
    for item in corpus_belief:
        index_obs=[i for i,val in enumerate(item.vector) if val]
        #print(len(index_obs))
        if len(index_obs)>max_obs:index_obs=index_obs[:max_obs]
        s_obs=[obs_matrix[i] for i in index_obs]
        
        for ind in index_obs:
            new_item=copy.copy(item)
            new_item.observation=obs_matrix[ind]
            corpus_sent_obs.append(new_item)
            
    print("new corpus with elements:",len(corpus_sent_obs))
    return corpus_sent_obs
        
    


def get_condps_through_time(target_vector,matrix,side_size=7,interest_indices=[]):
    steps=list(range(-side_size,side_size+1,1))
    if not interest_indices:interest_indices=range(matrix.shape[1])
    
    condps=np.zeros((len(interest_indices),len(steps)), dtype=float)
    
    for time in steps:
        vector=slide_time(target_vector, time)    
        for y,j in enumerate(interest_indices):
            prop_vector=matrix[:,j]
            condps[y,time+side_size]=dss_condp(prop_vector,vector)
    return condps
    
def get_all_basic_props_heatmaps_through_time(matrix,basic_props,side_size=7):
    for i in range(matrix.shape[1]):
        ref_prop=matrix[:,i]
        prop_flatname=basic_props[i].replace("(","_").replace(")","").replace(",","_")
        graph_filename="../outputs/websites/"+prop_flatname+".html"
        
        get_heatmap_through_time(ref_prop, matrix, basic_props[i], basic_props, graph_filename, side_size)
                
def get_heatmap_through_time(target_vector,matrix,graph_label,y_labels,filename,side_size=7,interest_indices=[]):
    steps=list(range(-side_size,side_size+1,1))
    step_labels=["t="+str(i) for i in steps]
    
    condps=get_condps_through_time(target_vector, matrix, side_size,interest_indices)
        
    graph_title="Conditional Probs P( Y | "+graph_label+" )"
    get_web_heatmap(condps,  step_labels, y_labels, graph_title, "Time Steps","Basic Proposition Y",filename)
    
    line="* ["+graph_label+"](https://iesus.github.io/dynamic-dss-websites/across_time/"+filename+")"
    print(line) #This prints out code that we can put in a github readme file

def get_vector_visualizations_through_time(target_vector,matrix,label,y_labels,filename,side_size=7,interest_indices=[]):
    steps=list(range(-side_size,side_size+1,1))
    step_labels=["t="+str(i) for i in steps]
    label=label.split("---")
    
    condps=get_condps_through_time(target_vector, matrix, side_size, interest_indices)
    graph_title="P( Y | "+label[0]+" )  "+label[1]
    
    colors=[tuple(np.random.choice(range(256), size=3)) for i in range(len(y_labels))]
    colors=['rgb'+str(col) for col in colors]

    x_data = np.vstack((np.asarray(steps),)*condps.shape[0])
    y_data = condps
    
    fig = go.Figure()
    
    for i in range(condps.shape[0]):
        fig.add_trace(go.Scatter(x=x_data[i], y=y_data[i], mode='lines',
            name=y_labels[i],
            line=dict(color=colors[i]),# width=line_size[i]),
            connectgaps=True,
        ))
    
    fig.update_layout(
        xaxis=dict(
            showline=False,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=False,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True,
        plot_bgcolor='white'
    )
    
    annotations = []
    # Adding labels
    for y_trace, y_label in zip(y_data, y_labels):
        annotations.append(dict(xref='paper', x=0.05, y=y_trace[0],
                                      xanchor='right', yanchor='middle',
                                      text=y_label + ' {:.2f}'.format(y_trace[0]),
                                      font=dict(family='Arial',
                                                size=16),
                                      showarrow=False))
    # Title
    annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                                  xanchor='left', yanchor='bottom',
                                  text=graph_title,
                                  font=dict(family='Arial',
                                            size=30,
                                            color='rgb(37,37,37)'),
                                  showarrow=False))
    
    fig.update_layout(annotations=annotations)
    fig.update_xaxes(title_text='Time Steps',
                     ticktext=step_labels,
                     tickvals=steps
                    )
    
    
    line="* [Line plots, only selected basic propositions](https://iesus.github.io/dynamic-dss-websites/across_time/"+filename+")"
    print(line) #This prints out code that we can put in a github readme file

    if filename: fig.write_html(filename)
    else:fig.show()







if __name__ == '__main__':

    import sys
    sys.path.insert(0,'/Users/jesus/eclipse-workspace/Luuk_Hana_Jesus/src')

    matrix_path="../outputs/street_life_model/observations/street_life30K.observations"
    prolog_corpus_path="../outputs/street_life_model/street_life_model.simple.set"
    
    
    matrix,basic_props=load_prolog_situation_space_matrix(matrix_path)
    
    seq_size=15
    seqs=[]
    for i in range(len(matrix)-seq_size):
        i_seq=matrix[i:i+seq_size]
        o_seq=matrix[i+1:i+seq_size+1]
        seqs.append([i_seq,o_seq])
        
    from neural_models.event_comp import EventComprehensionDataset
    
    event_dataset=EventComprehensionDataset(seqs,basic_props)
    
    
    john_bus_indices=list(range(15))+list(range(27,49))+list(range(147,161))+list(range(163,169))
    john_indices=list(range(15))+list(range(27,49))+[160]
    john_crossing=list(range(7))+list(range(10,13))#+list(range(27,39)
    john_falling=list(range(7))+list(range(10,15))+list(range(31,35))
    #print(john_indices)
    #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 168]
    #print(len(john_indices))#57
       
    #for i in john_indices:print(i,basic_props[i])
    
    #jointps,condps=get_conditional_joint_probs(matrix)
    
    #get_web_heatmap(jointps,basic_props, basic_props, "Joint Probabilities P(X,Y)",filename="joint_probs.html")
    #get_web_heatmap(condps, basic_props, basic_props, "Conditional Probabilities P(X|Y)",filename="cond_probs.html")
    
    #get_all_basic_props_heatmaps_through_time(matrix,basic_props,side_size=7)
    

    #corpus,impossible,map_sent_trainelem,vocab,bprops=load_prolog_corpus_belief(prolog_corpus_path, matrix_path,'prolog_corpus.pickle')
    
    
    with open('prolog_corpus.pickle','rb') as f:
        corpus = pickle.load(f)
        impossible=pickle.load(f)
        map_sent_trainelem=pickle.load(f)
        vocab=pickle.load(f)    

    
    #get_corpus_sentence_observations(corpus, matrix)
    
    
    #collapsed_corpus=get_collapsed_corpus(corpus)
    #print(len(corpus))           #983
    #print(len(collapsed_corpus)) #720
    #print(len(impossible))       #121
    print(vocab)
    #['pad', 'it', 'everyone', 'sad', 'hit', 'intersection', 'cola', 'arrived', 'raining', 'a', 'falling', 'smiling', 'at', 's', 'arriving', 'women', 'side', 'drinking', 'to', 'sandwich', 'walked', 'ate', 'eating', 'man', '.', 'woman', 'the', 'smiled', 'henrietta', 'and', 'south', 'was', 'mary', 'street', 'someone', 'fries', 'tea', 'crossed', 'drove', 'crossing', 'standing', 'john', 'some', 'rained', 'glad', 'house', 'bus', 'food', 'fell', 'were', 'driving', 'north', 'drank', 'stood', 'front', 'walking']

    
    comp_dataset=SentenceComprehensionDataset(corpus,vocab)
    
    
    #sentences=["john was crossing the street .","john crossed the street ."]
    sentences=["john was walking to henrietta s house .","john walked to henrietta s house ."]
    sentences= ["john fell .", "john was falling ."]
    interest_indices=john_falling
    
    for sent in sentences:
        filename_prefix="../outputs/websites/"+sent.replace(" .","").replace(" ","_")
        telem=map_sent_trainelem[sent]
        graph_title=telem.sentence+"---"+telem.semantics
        print(telem.semantics)
        print(telem.vector)        
        
        #Heatmap with ALL basic props
        get_heatmap_through_time(telem.vector, matrix, graph_title,basic_props, filename_prefix+"_HM_all.html")
        
        #Heatmap only john-related props
        y_labels=[basic_props[j] for j in john_indices]
        get_heatmap_through_time(telem.vector, matrix, graph_title,y_labels, filename_prefix+"_HM_john.html",interest_indices=john_indices)
        
        #Heatmap with only crossing the street
        y_labels=[basic_props[j] for j in interest_indices]
        get_vector_visualizations_through_time(telem.vector, matrix, graph_title,y_labels, filename_prefix+"_lines_cross.html",interest_indices=interest_indices)
        
        
        #get_vector_visualizations_through_time(telem.vector, matrix, basic_props,sent, filename)
                
         
            
            
            
            
    