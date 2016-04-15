Code: Python3 that implements mistake-bound 'Percepton' algorithm for multi-class
classification. It uses Kesler's construction as outlined in
http://l2r.cs.illinois.edu/~danr/Teaching/CS446-15/Lectures/07-LecMulticlass.pdf.
The update rule is 'conservative', the definition of which is provided on
slide-32 of this pdf.

Dataset: http://www.start.umd.edu/gtd/
"The Global Terrorism Database (GTD) is an open-source database including
information on terrorist events around the world from 1970 through 2014 (with
annual updates planned for the future)."

Problem: Using 'features' associated with an incident like location, weapon-type etc.
to predict the group (outfit) associated or responsible for the incident. The
current implementation uses 25 features out of many provided at the source link.

(Prel. results):
The following results are using the 2011-14 data-file provided at the source
link. The perceptron algorithm is run on labeled data (with assigned groups -
19075 out of 42373). 80-20 cross-validation is used. The accuracies seen after 10000
iterations and a learning rate of 0.005 are:

Training accuracy=0.773
Test accuracy=0.747

ErrorPlot.png is the graph showing the drop in error with number of iterations.
The file 'eval.txt' contains the predictions for the data that was not labeled in
the input (23298 out of 42373). The incidents are identified by the eventid field provided in source. 
