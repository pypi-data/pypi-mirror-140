TOPSIS-Python
Source code for TOPSIS optimization algorithm in python.

What is TOPSIS?
Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) came in the 1980s as a multi-criteria-based decision-making method.TOPSIS chooses the alternative 
of shortest the Euclidean distance from the ideal solution and greatest distance from the negative ideal solution.
TOPSIS is a way to allocate the ranks on basis of the weights and impact of the given factors.Weights mean how much a given factor should be taken into consideration 
(default weight = 1 for all factors).Impact means that a given factor has a positive or negative impact.

How to install this package?
pip install topsis-Dhanvi-101903427==0.0.1

To run from command prompt
python <inputdata.csv> <weights> <impacts> <outputfile.csv>
e.g. python input.csv "1,1,1,2,0.5" "+,+,-,+,-" output.csv

Sample Dataset
Model   P1	P2	P3	P4	P5
M1	0.77	0.59	6.2	58.7	16.57
M2	0.6	0.36	3.2	46	12.54
M3	0.68	0.46	4.3	51.5	14.24
M4	0.95	0.9	4.9	38.9	11.41
M5	0.61	0.37	4.7	62.6	17.07
M6	0.63	0.4	4.1	50	13.78
M7	0.69	0.48	5.1	44.1	12.59
M8	0.8	0.64	4.2	51.3	14.24

Output
Model   P1	P2	P3	P4	P5	Topsis Score	Rank
M1	0.77	0.59	6.2	58.7	16.57	0.49740		3
M2	0.6	0.36	3.2	46	12.54	0.361325	6
M3	0.68	0.46	4.3	51.5	14.24	0.402184	5
M4	0.95	0.9	4.9	38.9	11.41	0.533495	2
M5	0.61	0.37	4.7	62.6	17.07	0.465008	4
M6	0.63	0.4	4.1	50	13.78	0.360213	7
M7	0.69	0.48	5.1	44.1	12.59	0.266374	8
M8	0.8	0.64	4.2	51.3	14.24	0.548612	1

The model with highest topsis score is given the best ranking and should be chosen as the ideal solution.

Applications
1.Mobile selection on basis of multiple criteria like looks,storage,camera etc
2.University selection based on multiple factors.





