import logging
RCBXk=bool
RCBXp=hasattr
RCBXx=set
RCBXY=True
RCBXq=False
RCBXo=isinstance
RCBXL=dict
RCBXm=getattr
RCBXn=None
RCBXa=str
RCBXr=Exception
RCBXQ=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
KINESIS_DIR="kinesis"
DYNAMODB_DIR="dynamodb"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[RCBXk,Set]:
 if RCBXp(obj,"__dict__"):
  visited=visited or RCBXx()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return RCBXY,visited
  visited.add(wrapper)
 return RCBXq,visited
def get_object_dict(obj):
 if RCBXo(obj,RCBXL):
  return obj
 obj_dict=RCBXm(obj,"__dict__",RCBXn)
 return obj_dict
def is_composite_type(obj):
 return RCBXo(obj,(RCBXL,OrderedDict))or RCBXp(obj,"__dict__")
def api_states_traverse(api_states_path:RCBXa,side_effect:Callable[...,RCBXn],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    sub_dirs=os.path.normpath(dir_name).split(os.sep)
    region=sub_dirs[-1]
    service_name=sub_dirs[-2]
    account_id=sub_dirs[-3]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,account_id=account_id,mutables=mutables)
   except RCBXr as e:
    msg=(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    LOG.warning(msg)
    if LOG.isEnabledFor(logging.DEBUG):
     LOG.exception(msg)
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with RCBXQ(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except RCBXr as e:
   LOG.debug("Unable to read pickled persistence file %s: %s",state_file,e)
def persist_object(obj,state_file):
 with RCBXQ(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
