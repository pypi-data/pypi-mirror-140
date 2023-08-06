"""

Contains exceptions shared by members of the Inspyre-Toolbox package.

"""
import inspect


class ArgumentConflictError(Exception):
    def __init__(self, arg_1_name, arg_2_name,  message=None):
        """
        
        To be raised when a single function has been passed values to two or more of its arguments that logically
        conflict.
        
        """
        caller = inspect.stack()[1].function
        
        con_args_statement = f"Caller: {caller} | Conflicting Arguments: {arg_1_name}, {arg_2_name}"
        
        self.message = con_args_statement
        
        if message is not None:
            self.message += f'\nMore info: {message}'
            
        print(self.message)
