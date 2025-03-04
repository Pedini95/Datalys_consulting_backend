def MESSAGE_SUCCESS():
    response = {'message': "OPERATION SUCCESSFULLY", "code": 200}
    return response

def MESSAGE_DATA_EMPTY():
    response = {'message': "DATA EMPTY", "code": 400}    
    return response

def MESSAGE_DATA_NOT_EXIST():
    response = {'message': "DATA NOT EXIST", "code": 400}
    return response

def MESSAGE_DATA_DUPLICATE(field):
    response = {'message': f"DATA DUPLICATE {field}", "code": 400}
    return response

def MESSAGE_OPERATION_FORBIDEN():
    response = {'message': "OPERATION FORBIDEN", "code": 400}
    return response

def MESSAGE_ACCESS_DENIED():
    response = {'message': "ACCESS DENIED", "code": 400}
    return response

def MESSAGE_FIELD_EMPTY(field):
    response = {'message': "MISSING FIELD {}".format(field), "code": 400}
    return response