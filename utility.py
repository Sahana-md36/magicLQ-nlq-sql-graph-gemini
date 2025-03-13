


def write_code_to_file(code):
    # Open a file in write mode ('w')
    with open('gemini_generated_code.py', 'w') as file:
        # Write content into the file
        file.write(code)

def read_code_from_file():
    with open('gemini_generated_code.py', 'r') as file:
        code_read=file.read()
        print (f'CODE READ FROM gemini_generated_code.py ============== \n {code_read} \n================')
        return code_read
