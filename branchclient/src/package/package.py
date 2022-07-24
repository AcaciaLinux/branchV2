import main
import json
from log import blog
from bsocket import connect 
from package import build 

def checkout_package(pkg_name):
    s = connect.connect(main.B_NAME, main.B_TYPE)
    
    bpb_resp = connect.send_msg(s, "CHECKOUT_PACKAGE {}".format(pkg_name))
    
    # check if package is valid
    if(bpb_resp == "INV_PKG_NAME"):
        blog.error("The specified package could not be found.")
        return
    
    json_bpb = json.loads(bpb_resp)
    bpb = build.parse_build_json(json_bpb)
    build.create_pkg_workdir(bpb)

def submit_package():
    s = connect.connect(main.B_NAME, main.B_TYPE)
    
    bpb = build.parse_build_file("package.bpb")
    json_str = build.pack_json(bpb)
    resp = connect.send_msg(s, "SUBMIT_PACKAGE {}".format(json_str))
    
    if(resp == "CMD_OK"):
        blog.info("Package submission accepted by server.")
    else:
        blog.error("An error occured: {}".format(resp))
    
