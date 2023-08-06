 # -*- coding: utf-8 -*-
import os,importlib,random


version="0.0.1"
modules_info={}
Exploit_Details={}

def get_modules_info():
    base_dir=os.path.dirname(os.path.realpath(__file__))
    global modules_info
    count_all=0
    module_types=os.listdir(base_dir+os.sep+'modules')
    module_types=list(set(module_types)-set(["__init__.py","__pycache__"]))
    for module_type in module_types:
        modules_list=[i for i in os.listdir(base_dir+os.sep+'modules'+os.sep+module_type) if i[-3:]==".py" and i!="__init__.py"]
        count_all+=len(modules_list)
        modules_info[module_type]={}
        for module_name in modules_list:
            module_name=module_name.replace(".py",'')
            try:
                t=importlib.import_module("mumuzi.modules."+module_type+'.'+module_name)
            except:
                t=importlib.import_module("modules."+module_type+'.'+module_name)
            modules_info[module_type][module_name]=t.info()

    return modules_info,count_all




def get_banner():
    global version
    modules_info,count_all=get_modules_info()
    BANNER = f"""
 
 \033[0;"""+random.choice(['31','32','33','34','35','36'])+"""m██╗  ██╗██╗   ██╗ █████╗ ███╗   ██╗
 ╚██╗██╔╝██║   ██║██╔══██╗████╗  ██║
  ╚███╔╝ ██║   ██║███████║██╔██╗ ██║
  ██╔██╗ ██║   ██║██╔══██║██║╚██╗██║
 ██╔╝ ██╗╚██████╔╝██║  ██║██║ ╚████║
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝\033[0m
                                   
e\033[0;32mX\033[0mtremely \033[0;32mU\033[0mltimate \033[0;31mAnal\33[0mysistical \033[0;32mN\033[0meuron


Disclaimer : Usage of XUAN for attacking targets without prior mutual consent is illegal.
Dev Team   : Neuron-Network on Mumuzi
Version    : """+version+"""

Exploits   : """+str(count_all)+'\n'

    for module_type in modules_info.keys():
        BANNER+="    "+module_type.ljust(5)+" : "+str(len(modules_info[module_type]))+'\n'
    BANNER+="""
*type "help" to get some help.
"""
    return(BANNER)




def command_help(command):
    if command is None:
        return """
Core Commands
=============

    Command       Description
    -------       -----------
    help          Help menu
    exit          Exit the console
    set           Sets a context-specific variable to a value

Module Commands
===============

    Command       Description
    -------       -----------
    info          Displays information about one or current module
    options       Displays options for one or current module
    search        Searches module names and descriptions
    show          Displays modules of a given type, or all modules
    use           Interact with a module by name or search term/index
    run/exploit   Run one or current module
    tao           Taoshen writes a writeup for you (but you maybe cannot understand it)

Examples
========

Xuan:~ > use web/test_for_web
Xuan:web/test_for_web > set url='http://127.0.0.1'
Xuan:web/test_for_web > run

"""

def get_module_fullpath_and_infodata(module_path):
    module_path=module_path.lstrip('/').lstrip('\\')
    if '/' in module_path :
        module=module_path.split('/')
        info_data=modules_info[module[0]][module[1]]
        module_full_path='/'.join(module)
    elif '\\' in module_path:
        module=module_path.split('\\')
        info_data=modules_info[module[0]][module[1]]
        module_full_path='/'.join(module)
    else:
        for module_type in modules_info.keys():
            if module_path in modules_info[module_type].keys():
                info_data=modules_info[module_type][module_path]
                module_full_path=module_type+'/'+module_path
    try:
        return(True,(module_full_path,info_data))
    except:
        return(False,"module name error")



def get_module_info(module_path,Exploit_Details):
    success,result=get_module_fullpath_and_infodata(module_path)
    if success:
        (module_full_path,info_data)=result
    else:
        return(False,"key error")
    s="\n\nModule Path:\n"+'='*20+'\n'
    s+=module_full_path+'\n\n'
    s+="Module Info:\n"+'='*20+'\n'
    for key in info_data.keys():
        if key!="module options":
            s+=key.ljust(6)+" : "+info_data[key]+'\n'
    s+='\n'
    s+="Module options:\n"+'='*20+'\n'
    s+="Name        Current Setting                                   Required  Description\n"
    s+="------      ------------------------------------------------  --------  -----------\n"
    for module_option_line in info_data['module options']:
        s+=module_option_line['name'].ljust(12)
        if module_option_line['name'] in Exploit_Details:
            if len(Exploit_Details[module_option_line['name']])>=48:
                s+=(Exploit_Details[module_option_line['name']][:45]+"...").ljust(50)
            else:
                s+=Exploit_Details[module_option_line['name']].ljust(50)
        else:
            s+=" "*50
        if module_option_line['required']:
            s+='\033[0;32m'+str(module_option_line['required']).ljust(10)+'\033[0m'
        else:
            s+='\033[0;31m'+str(module_option_line['required']).ljust(10)+'\033[0m'
        s+=module_option_line['description']+'\n'
    return(True,s)

def run_module(module_path,Exploit_Details):
    #check is Exploit_Details right
    success,result=get_module_fullpath_and_infodata(module_path)
    if success:
        (module_full_path,info_data)=result
    else:
        return(False,"module name error")
    for option in info_data["module options"]:
        if option["required"] and option["name"] not in Exploit_Details.keys():
            return (False,"Option:"+option["name"]+" not set!")
    try:
        m=importlib.import_module("mumuzi.modules."+module_full_path.replace('/','.'))
    except:
        m=importlib.import_module("modules."+module_full_path.replace('/','.'))
    result=m.exploit(Exploit_Details)
    return(True,result)

def fetch(full_string, query_string):
    return(full_string.replace(query_string, '\033[0;31m%s\033[0m' % query_string))

def search_from_all_modules(query_string):
    result=''
    for module_type in modules_info.keys():
        for module_path in modules_info[module_type]:
            result_tmp=(module_type+'/'+module_path).ljust(34)+modules_info[module_type][module_path]['questname'].ljust(26)+modules_info[module_type][module_path]['platform'].ljust(22)+modules_info[module_type][module_path]['contest']+'\n'
            if query_string in result_tmp:
                result+=fetch(result_tmp,query_string)
    if len(result)==0:
        return(False,"No matches for \""+query_string+"\"!")
    s='\n\nSearch Result:\n'+'='*20+'\n'
    s+='Path                              Name                      Platform              Contest\n'
    s+='============================      ======================    ==================    =================\n'
    s+=result
    return(True,s)




def show_all_modules(module_type):
    if module_type is not None and module_type not in modules_info.keys():
        return(False,"No modules for \""+module_type+"\"!")
    result=''
    if module_type is None:
        for module_type in modules_info.keys():
            for module_path in modules_info[module_type]:
                result+=(module_type+'/'+module_path).ljust(34)+modules_info[module_type][module_path]['questname'].ljust(26)+modules_info[module_type][module_path]['platform'].ljust(22)+modules_info[module_type][module_path]['contest']+'\n'
    else:
        for module_path in modules_info[module_type]:
            result+=(module_type+'/'+module_path).ljust(34)+modules_info[module_type][module_path]['questname'].ljust(26)+modules_info[module_type][module_path]['platform'].ljust(22)+modules_info[module_type][module_path]['contest']+'\n'

    s='\n\nModules Info:\n'+'='*20+'\n'
    s+='Path                              Name                      Platform              Contest\n'
    s+='============================      ======================    ==================    =================\n'
    s+=result
    return(True,s)

def make_wp(module_path):
    success,result=get_module_fullpath_and_infodata(module_path)
    if success:
        (module_full_path,info_data)=result
    else:
        return(False,"module name error")
    try:
        m=importlib.import_module("mumuzi.modules."+module_full_path.replace('/','.'))
    except:
        m=importlib.import_module("modules."+module_full_path.replace('/','.'))
    result=m.make_wp()
    return(True,result)