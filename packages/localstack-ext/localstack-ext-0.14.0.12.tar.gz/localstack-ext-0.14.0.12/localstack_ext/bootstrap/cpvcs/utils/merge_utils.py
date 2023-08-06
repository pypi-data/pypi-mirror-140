import os
VnXlB=staticmethod
VnXlg=bool
VnXlL=isinstance
VnXlC=str
VnXlG=Exception
import zipfile
from typing import Dict
from localstack.utils.common import mkdir,new_tmp_dir
from localstack.utils.generic.singleton_utils import SubtypesInstanceManager
from moto.s3.models import FakeBucket
from moto.sqs.models import Queue
from localstack_ext.bootstrap.cpvcs.models import Serialization
from localstack_ext.bootstrap.state_merge import(merge_dynamodb,merge_kinesis_state,merge_object_state)
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,api_states_traverse,load_persisted_object,persist_object)
ROOT_FOLDERS_BY_SERIALIZATION=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
class CPVCSMergeManager(SubtypesInstanceManager):
 @VnXlB
 def _is_special_case(obj)->VnXlg:
  return VnXlL(obj,(Queue,FakeBucket))
 def two_way_merge(self,from_state_files:VnXlC,to_state_files):
  raise VnXlG("Not implemented")
 def three_way_merge(self,common_ancestor_state_files:VnXlC,from_state_files:VnXlC,to_state_files:VnXlC):
  raise VnXlG("Not implemented")
class CPVCSMergeManagerDynamoDB(CPVCSMergeManager):
 @VnXlB
 def impl_name()->VnXlC:
  return Serialization.DDB.value
 def two_way_merge(self,from_state_files:VnXlC,to_state_files):
  merge_dynamodb(from_state_files,to_state_files)
 def three_way_merge(self,common_ancestor_state_files:VnXlC,from_state_files:VnXlC,to_state_files:VnXlC):
  merge_dynamodb(from_state_files,to_state_files)
class CPVCSMergeManagerKinesis(CPVCSMergeManager):
 @VnXlB
 def impl_name()->VnXlC:
  return Serialization.KINESIS.value
 def two_way_merge(self,from_state_files:VnXlC,to_state_files):
  merge_kinesis_state(to_state_files,from_state_files)
 def three_way_merge(self,common_ancestor_state_files:VnXlC,from_state_files:VnXlC,to_state_files:VnXlC):
  self.two_way_merge(to_state_files,from_state_files)
class CPVCSMergeManagerMain(CPVCSMergeManager):
 @VnXlB
 def impl_name()->VnXlC:
  return Serialization.MAIN.value
 @VnXlB
 def _merge_three_way_dir_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  account_id=kwargs.get("account_id")
  fname=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  mutables=kwargs.get("mutables")
  other=mutables[0]
  ancestor=mutables[1]
  src_state_file_path=os.path.join(dir_name,fname)
  ancestor_state_dir=os.path.join(ancestor,account_id,service_name,region)
  ancestor_state_file_path=os.path.join(ancestor_state_dir,fname)
  dst_state_dir=os.path.join(other,account_id,service_name,region)
  dst_state_file_path=os.path.join(dst_state_dir,fname)
  src_state=load_persisted_object(src_state_file_path)
  ancestor_state=load_persisted_object(ancestor_state_file_path)
  special_case=CPVCSMergeManager._is_special_case(src_state)
  if os.path.isfile(dst_state_file_path):
   if not special_case:
    dst_state=load_persisted_object(dst_state_file_path)
    merge_object_state(dst_state,src_state,ancestor_state)
    persist_object(dst_state,dst_state_file_path)
  else:
   mkdir(dst_state_dir)
   persist_object(src_state,dst_state_file_path)
 @VnXlB
 def _merge_two_state_dir_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  account_id=kwargs.get("account_id")
  fname=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  mutables=kwargs.get("mutables")
  other=mutables[0]
  src_state_file_path=os.path.join(dir_name,fname)
  dst_state_dir=os.path.join(other,account_id,service_name,region)
  dst_state_file_path=os.path.join(dst_state_dir,fname)
  src_state=load_persisted_object(src_state_file_path)
  special_case=CPVCSMergeManager._is_special_case(src_state)
  if os.path.isfile(dst_state_file_path):
   if not special_case:
    dst_state=load_persisted_object(dst_state_file_path)
    merge_object_state(dst_state,src_state)
    persist_object(dst_state,dst_state_file_path)
  else:
   mkdir(dst_state_dir)
   persist_object(src_state,dst_state_file_path)
 def two_way_merge(self,from_state_files:VnXlC,to_state_files):
  api_states_traverse(api_states_path=to_state_files,side_effect=CPVCSMergeManagerMain._merge_two_state_dir_func,mutables=[from_state_files])
 def three_way_merge(self,common_ancestor_state_files:VnXlC,from_state_files:VnXlC,to_state_files:VnXlC):
  api_states_traverse(api_states_path=to_state_files,side_effect=CPVCSMergeManagerMain._merge_three_way_dir_func,mutables=[from_state_files,common_ancestor_state_files])
def create_tmp_archives_by_serialization_mechanism(archive_dir:VnXlC)->Dict[VnXlC,VnXlC]:
 tmp_root_dir=new_tmp_dir()
 with zipfile.ZipFile(archive_dir)as archive:
  archive.extractall(tmp_root_dir)
 result={"root":tmp_root_dir}
 for serialization_mechanism_root_dir in ROOT_FOLDERS_BY_SERIALIZATION:
  tmp_root_dir_for_serialization_mechanism=os.path.join(tmp_root_dir,serialization_mechanism_root_dir)
  mkdir(tmp_root_dir_for_serialization_mechanism)
  result[serialization_mechanism_root_dir]=tmp_root_dir_for_serialization_mechanism
 return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
