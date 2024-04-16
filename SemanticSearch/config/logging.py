import logging


process_name='PPL_DocsSearch'
#creates a custom logger based on script-running  name 
logger=logging.get(__name__)

#create handlers
f_handler=logging.FileHandler('logs.log')
f_handler.setLevel(logging.INFO)
c_handler=logging.StreamHandler()
c_handler.setLevel(logging.WARNING)


#create formatters and add it to 