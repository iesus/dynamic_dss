# Dynamic Distributed Situation Space

This is a Python implementation of a new version of the Distributed Situation Space which differs from other related implementations [2-5] 
in that it samples microworld observations sequentially and with temporal dependencies between them.

A microworld is defined as in [1-5] in terms of a set of basic propositions, which put together can 
characterize the state of affairs of the microworld at any time t. Each observation is a binary vector that encodes the full state of affairs 
of the microworld at a particular moment t, where each dimension encodes whether a given basic proposition is true (with a value of 1) or 
false (with value of 0). Each observation depends on the previous observations at times t-1,t-2,t-3... The length of these dependencies depends on 
the design of the particular microworld. 

The main contribution of this repository is a framework in which microworlds can be defined and simulated in order
to sample observations with temporal continuity. This can be used to build a situation space matrix by putting together the vectors 
of the set of sampled observations in the order in which they were sampled, which encodes the temporal dependencies. 

Having the desired situation space matrix, we use the DSS [dispace](https://github.com/hbrouwer/dispace) implementation of 
Harm Brouwer and colleagues in order to define a grammar to generate sentences and their propositional logic form, and finally, using the 
sampled situation space matrix, the DSS vector representations, which can later be used for computational modeling purposes.

## Related Work
The situation space matrix is an ordered set of observations where the values/state of affairs of an observation at time t depend
on the observation at time t-1. In this aspect, this work is identical to the DSS model described in [1]. However, it differs 
from [2-5], as those frameworks sample observations with no dependencies between them (but they do encode dependencies between 
propositions within a given observation).

After obtaining the collection of ordered observations, this work also differs from [1-3] by avoiding the Self-Organizing-Map 
for dimensionality reduction. In general, this work differs from [1-5] by obtaining belief vectors from the full situation 
state matrix without dimensionality reduction, as in [6].     

## Files
The main definition of the microworld "Street Life" is defined in "street_life_world.py". While most of the code is parameterized, 
such that it is independent of the definition of a particular microworld, there are still parts that need to be adapted for 
each specific microworld:

- in eventualities.py: Eventuality.get_effects() is tailored to some degree to the predicates "walk_to","drive_to","cross_street",
"fall" and "hit".
- in microworld.py: Microworld.run() the weather (proposition "rain") is handled manually because no participant initiates the rain. 
   A microworld with no/different weather dynamics would need to adapt those lines.
- in participants.py: Participant.start_eventualities() is also tailored to the urban setting.

We utilize/adapt the DSS [dispace](https://github.com/hbrouwer/dispace) implementation of Harm Brouwer in order to generate sentences 
with their propositional logic form. We also adapt the quantification rules in [here](https://github.com/hbrouwer/dfs-tools/blob/master/worlds/wollic2019.pl).
The folder [local_dispace](https://github.com/iesus/dynamic_dss/blob/main/src/dss) contains a copy of the dispace repository from 05-April-2022. 
The repository is as taken from the source, except that the file [street_life.pl](https://github.com/iesus/dynamic_dss/blob/main/src/dss/worlds/street_life.pl) was added, which contains the 
definition of our microworld. Additionally, the file [gen_sets.pl](https://github.com/iesus/dynamic_dss/blob/main/src/dss/src/gen/gen_sets.pl) was modified by adding modifications of some 
rules. The original rules were preserved, and the new modified rules were added with the comment "%JESUS CALVILLO" above their definition.


## Usage
This framework mixes the previous DSS Prolog implementation with new Python code in order to define and sample observations of a microworld.
As a first step, we define the microworld in Python and sample observations in order to generate the situation space matrix.
As a second step, we define the grammar that generates sentences about the microworld with their propositional form semantics. The propositions used here
should be the same used for the definition of the microworld.
The final step corresponds to linking the situation space matrix of step 1 with the sentences of the grammar of step 2, in order to generate
a dataset of sentences with their corresponding DSS representations.

The output files generated are not included in the github repository due to limitations of github. However, they can be generated using the instructions below.


### Generating the Situation Space Matrix (Step 1)

In contrast to [2-6], who generate the situation space matrix using a prolog script that samples observations independently from one another, here
we define a microworld in Python such that each observation depends on the previous one.

This is done in the file [street_life_world.py](https://github.com/iesus/dynamic_dss/blob/main/src/simulation/street_life_world.py), which uses
classes and methods from the files in the same directory. 

At the end of the file, the line:
```
  models=world.run(30000,random)
```
initializes the microworld and generates 30000 observations. In this line one can modify this number in order to get more/less observations. 
The code after this line is related to saving the output into files. In particular, the lines
```
   with open("../outputs/street_life_model/street_life30K.observations",'w') as output_file:
        models[0].print_basic_propositions(file=output_file) 
        for model in models: model.print_binary_vector(file=output_file)
```
generate a file that can be read by prolog, in order to be used by the rest of the DSS prolog machinery.
   
### Defining a Grammar that Generates Sentences with Propositional Form Semantics (Step 2)

Similar to [1-6], I use the DSS prolog implementation in order to define a grammar that generates sentences with their propositional logic form semantics.
The grammar for "Street Life" is in the file [street_life.pl](https://github.com/iesus/dynamic_dss/blob//main/src/dss/worlds/street_life.pl).

One can run that file using SWIPL. After loading it, one can generate the sentences and write the to file using the line:
```
  write_sentences.
```
which is a rule at the end of the file where one can specify the type of sentence that one wants and the name of the output file. Right now one can choose between simple sentences
and coordinated sentences. The output file contains sentences with the propositional logic form semantics.


### Generating the Dataset (Sentences with their DSS vectors, Step 3)

Having the situation space matrix defined and saved to a file using the Python code, we can load it in prolog in order to use it with the
DSS code to generate the sentences and link them to their DSS representations. 

In order to do so, one has to first load the file [street_life.pl](https://github.com/iesus/dynamic_dss/blob//main/src/dss/worlds/street_life.pl) with
swipl (this file references code in the whole dss directory). Then run the following line:

```
  dss_read_vectors('street_life30K.observations',SM),gen_set_short('simple',SM,'street_life_model')..
```
where 'street_life.observations' is the file that contains the situation space matrix (generated in Step 1).

This will generate a file "street_life_model.train.localist.set", which contains the sentences with their corresponding DSS vector representations.
The vectors in this file have not gone through a dimensionality reduction, therefore their dimensionality is equal to the number of observations that were
sampled in order to generate the situation space matrix, in our case 30,000.

### Visualizations

Different visualizations for the dataset created with the Street Life microworld can be seen [here](https://github.com/iesus/dynamic-dss-websites)


### Model Architecture

The proposed model architecture at this point is the one in the following image:

![Model Architecture](https://github.com/iesus/dynamic_dss/blob//main/architecute.png)

The model has 3 main parts, the part inside the blue rectangle is essentially the same as the model in Frank et al. (2009): a model of sentence comprehension that maps sentences to their semantic representations, in this case belief vectors. The part inside the green rectangle is very similar to the model of Elman & McRae: given a state-of-affairs, it predicts the next state(s). The part inside the yellow rectangle is identical to the green rectangle, except that it infers the previous state-of-affairs given the current state-of-affairs. Together, the model can receive a sentence and:

- Infer how is the state of the microworld at the moment where the given sentence is true.
- Predict how is going to be the state of the microworld in the next steps.
- Infer how was the state of the microworld in the previous steps.

## References

[1] Frank, S. L., Koppen, M., Noordman, L. G. M., and Vonk, W. (2003).
Modeling knowledge-based inferences in story comprehension. *Cognitive
Science 27*(6), pp. 785-910.

[2] Frank, S. L., Haselager, W. F. G., and van Rooij, I. (2009).
Connectionist semantic systematicity. *Cognition 110*(3), pp. 358-379.

[3] Brouwer, H., Crocker, M. W., and Venhuizen N. J. (2017). Neural
Semantics. In: Wieling, M., Kroon, M., van Noord, G. J. M., and Bouma, G.
(eds.), *From Semantics to Dialectometry: Festschrift for John Nerbonne*,
pp. 75-83. College Publications.

[4] Venhuizen, N. J., Crocker, M. W., and Brouwer, H. (2019).
Expectation-based Comprehension: Modeling the Interaction of World Knowledge
and Linguistic Experience. *Discourse Processes, 56*:3, 229-255.

[5] Venhuizen, N. J., Hendriks, P., Crocker, M. W., and Brouwer, H. (2021). 
Distributional Formal Semantics. *Information and Computation*, 104763.

[6] Calvillo, J., Brouwer, H., & Crocker, M. W. (2021). 
Semantic Systematicity in Connectionist Language Production. *Information*, 12(8), 329.

