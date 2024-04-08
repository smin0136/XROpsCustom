from pydantic import BaseModel, validator, EmailStr
from datetime import datetime
from typing import List, Union, Optional
from fastapi.responses import JSONResponse, StreamingResponse

import os
import cv2
import json
import re
from fastapi import APIRouter, status, HTTPException, File, Form, UploadFile
from PIL import Image
import user_code

import ast
import inspect

import time

import numpy as np
from io import BytesIO

router = APIRouter(prefix="/custom", 
                   tags=['custom'])


process_list = {}



# class Module(BaseModel):
#     input_info:dict = {}
#     function:dict = {}
#     args:dict= {}


def execute_node(input, info):
    fucntion_obj = info['function']
    function_name = fucntion_obj['name']
    function_params = fucntion_obj['parameters']
    function_args = info['args']
    param_str = ""
    for param in function_params:
        if param['name'] =='input':
            continue
        param_str = param_str + "," + param['name']        
        globals()[param['name']] = function_args[param['name']]

    output = eval(f"user_code.{function_name}(input{param_str})")
    return output



def get_type(arg):
    if arg==None:
        return 'undefined'
    return arg.id


@router.get("/function_list")
def function_list():
    file_path = "./user_code.py"

    with open(file_path, "r") as file:
        file_lines = file.readlines()

    node = ast.parse(''.join(file_lines), filename=file_path)
    functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]

    function_obj_list = []
    for i, func in enumerate(functions):
        function_name = func.name
        parameters = [{"name":arg.arg,"type":get_type(arg.annotation)} for arg in func.args.args]

        start_lineno = func.lineno - 1 
        if i + 1 < len(functions):
            end_lineno = functions[i + 1].lineno - 2
        else:
            end_lineno = len(file_lines)
        function_code = "\n".join(file_lines[start_lineno:end_lineno])

        function_obj_list.append({
            'name': function_name,
            'parameters': parameters,
            'code': function_code
        })
        
    return function_obj_list


@router.post("/run/")
def run_module(
    array:UploadFile = File(...),
    info: str = Form(...)
):
    info_dict = json.loads(info)
    print(info_dict)

    input_bytes = array.file.read()
    input_converted = np.frombuffer(input_bytes, dtype=np.dtype(info_dict['input_info']['dtype'])).reshape(info_dict['input_info']['shape'])

    try:
        output = execute_node(input_converted, info_dict)
    except Exception as e:
        print(e)
        output = input_converted

    if info_dict['input_info']['output'] == "json":
        output_bytes = bytes(output, 'utf-8')
        output_type = 'json'
        output_shape = ""
    elif info_dict['input_info']['output'] == "array":
        output_bytes = output.tobytes()
        output_type = str(output.dtype)
        output_shape = ",".join(map(str, output.shape))
    else:
        output_bytes = output.tobytes()
        output_type = 'else'
        output_shape = ""
    bytes_io = BytesIO(output_bytes)


    headers = {
        "Content-Type": "application/octet-stream",
        "dtype": output_type,
        "shape": output_shape
    }

    return StreamingResponse(bytes_io, headers=headers)

    # return JSONResponse(content={
    #     "array": output_bytes,
    #     "info": {"dtype":str(output.dtype),"shape":output.shape}
    # })
            


@router.get("/progress/{process_id:str}")
def get_progress(
    progress_id
):    
    if process_id in process_list:
        return process_list[process_id]
    
    return None



