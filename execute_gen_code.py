#from gemini_generated_code import generated_code

def execute_code(code):
   
    # Execute the provided code
   
    print(f'EXECUTING CODE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {code}')

    #generated_code()
    exec(code, globals())
    print(f'EXECUTED CODE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')