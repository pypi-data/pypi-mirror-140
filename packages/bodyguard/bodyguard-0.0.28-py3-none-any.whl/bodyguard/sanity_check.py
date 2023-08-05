#------------------------------------------------------------------------------
# Libraries
#------------------------------------------------------------------------------
from .exceptions import WrongInputTypeException,WrongInputException
from .tools import isin
#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
# Sanity checks
def check_type(x,allowed_type,name="x"):
    
    # Check; allowed_type
    if not isinstance(allowed_type,(type,tuple)):
        raise WrongInputTypeException(input_name="allowed_type",
                                      provided_input=allowed_type,
                                      allowed_inputs=[type,tuple])
        
    # Check; allowed_type
    if not isinstance(name, str):
        raise WrongInputTypeException(input_name="name",
                                      provided_input=name,
                                      allowed_inputs=str)
        
    # Perform actual sanity check
    if not isinstance(x,allowed_type):
        raise WrongInputTypeException(input_name=name,
                                      provided_input=x,
                                      allowed_inputs=allowed_type)
        
        
def check_str(x,allowed_input,name="x"):
    
    # Check input
    check_type(x=x,allowed_type=str)
    
    # Check; allowed_input
    if not isinstance(allowed_input,(str,list)):
        raise WrongInputTypeException(input_name="allowed_input",
                                      provided_input=allowed_input,
                                      allowed_inputs=[str,list])
                
    # Check; allowed_input
    if not isinstance(name, str):
        raise WrongInputTypeException(input_name="name",
                                      provided_input=name,
                                      allowed_inputs=str)
        
    # Perform actual sanity check
    if not isin(a=x,b=allowed_input):
        raise WrongInputException(input_name=name,
                                  provided_input=x,
                                  allowed_inputs=allowed_input)
        
        
                