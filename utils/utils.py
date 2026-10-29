import utils.constants as constants

def res_status_msg(service, status, message=""):
    if status == constants.SUCCESS:
        return message or f"{service} {constants.SUCCESS}"
    elif status == constants.ERROR:
        return message or f"{service} {constants.ERROR}"