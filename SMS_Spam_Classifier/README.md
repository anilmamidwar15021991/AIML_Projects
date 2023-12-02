**#Spam classifier using Multiple classifier models**
1) First train the multiple classifier models(NB,SVM,KNN,RF,Voting,Stacking)
2) then save the model as pickle file
3) For EC2 deployment - 
    1) create the flask app and call pickle file(saved model)
    2) deploy the flask app files and pickle files in AWS ec2 instance using SSH client or ant other ftp clients
4) For Streamli deployment -
   1) create the streamlit app "streamlit_app.py" and call the pickle file (save model)
   2) psuh the code to github and then use streamlit cloud deployment 
    
