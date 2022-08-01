import json
import os
import main
from log import blog
from localstorage import localstorage
from localstorage import build
from manager import queue

def handle_command(manager, client, command):
    command = command.decode("utf-8")

    cmd_header_loc = command.find(" ")
    cmd_header = ""
    cmd_body = ""

    # One word command
    if(cmd_header_loc == -1):
        cmd_header = command
    else:
        cmd_header = command[0:cmd_header_loc]
        cmd_body = command[cmd_header_loc+1:len(command)]

    #
    # Used by a client to set it's type
    # SET_MACHINE_TYPE <TYPE>
    # (controller, build)
    #
    if(cmd_header == "SET_MACHINE_TYPE"):
        if(cmd_body == "CONTROLLER"):
            blog.info("Machine type assigned. Client '{}' is authenticated as controller client type.".format(client.get_identifier()))
            client.client_type = "CONTROLLER"
        elif(cmd_body == "BUILD"):
            blog.info("Machine type assigned. Client '{}' is authenticated as build client type.".format(client.get_identifier()))
            client.client_type = "BUILD"
        else:
            return "INV_MACHINE_TYPE"

        return "CMD_OK"

    #
    # Used by a client to set it's display name
    # SET_MACHINE_NAME <NAME>
    #
    elif(cmd_header == "SET_MACHINE_NAME"):
        blog.info("Client name changed. Client '{}' is now known as '{}'".format(client.get_identifier(), cmd_body))
        client.client_name = cmd_body
        return "CMD_OK"

    #
    # checkout a package build file
    #
    elif(cmd_header == "CHECKOUT_PACKAGE"):
        storage = localstorage.storage()

        if(cmd_body in storage.packages):
            blog.info("Client {} checked out package '{}'!".format(client.get_identifier(), cmd_body))
            return storage.get_json_bpb(cmd_body)
        else:
            return "INV_PKG_NAME"

    #
    # submit a package build file
    #
    elif(cmd_header == "SUBMIT_PACKAGE"):
        json_bpb = json.loads(cmd_body)
        bpb = build.parse_build_json(json_bpb)
        tdir = build.create_stor_directory(bpb.name)
        
        bpb_file = os.path.join(tdir, "package.bpb")
        if(os.path.exists(bpb_file)):
            os.remove(bpb_file)
       
        

        build.write_build_file(bpb_file, bpb)
    
        return "CMD_OK"
    
    elif(cmd_header == "SIG_READY"):
        blog.info("Client {} is ready for commands.".format(client.get_identifier()))
        client.is_ready = True
        client.send_command("CMD_OK")
        manager.queue.notify_ready(manager)
        return None

    elif(cmd_header == "RELEASE_BUILD"):
        storage = localstorage.storage()
        if(cmd_body in storage.packages):
            blog.info("Controller client requested release build for {}".format(cmd_body))
            res = manager.get_queue().add_to_queue(manager, cmd_body)
            return res
        else:
            blog.info("Controller client requested release build for invalid package.")
            return "INV_PKG_NAME"

    # 
    # Print requesting client object
    #
    elif(cmd_header == "DEBUG_DUMP_VARS"):
        blog.info("Debug dump requested:")
        print(client.__dict__)
        return "CMD_OK"
    
    #
    # Print all clients by type
    #
    elif(cmd_header == "DEBUG_LIST_CLIENTS"):
        blog.info("Debug Client list requested: ")
        print("Controller clients:")
        for cl in manager.get_controller_clients():
            print(cl.get_identifier())
        print("Build clients:")
        for cl in manager.get_build_clients():
            print(cl.get_identifier())
        return "CMD_OK"

    #
    # Returns master server version
    #
    elif(cmd_header == "MASTER_VERSION"):
        return main.B_VERSION

    #
    # Invalid command
    #
    else:
        blog.debug("Received a malformed command from client {}".format(client.client_uuid))
        return "INV_CMD"

