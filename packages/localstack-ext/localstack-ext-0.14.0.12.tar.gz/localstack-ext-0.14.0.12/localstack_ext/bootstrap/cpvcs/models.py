from datetime import datetime
sINlf=str
sINlq=int
sINle=super
sINly=False
sINlF=isinstance
sINlA=hash
sINlH=bool
sINlY=True
sINlz=list
sINlE=map
sINli=None
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class CPVCSObj:
 def __init__(self,hash_ref:sINlf):
  self.hash_ref:sINlf=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={sINlf(MAIN):API_STATES_DIR,sINlf(DDB):DYNAMODB_DIR,sINlf(KINESIS):KINESIS_DIR}
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:sINlf,rel_path:sINlf,file_name:sINlf,size:sINlq,service:sINlf,region:sINlf,account_id:sINlf,serialization:Serialization):
  sINle(StateFileRef,self).__init__(hash_ref)
  self.rel_path:sINlf=rel_path
  self.file_name:sINlf=file_name
  self.size:sINlq=size
  self.service:sINlf=service
  self.region:sINlf=region
  self.account_id:sINlf=account_id
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,account_id=self.account_id,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return sINly
  if not sINlF(other,StateFileRef):
   return sINly
  return(self.hash_ref==other.hash_ref and self.account_id==other.account_id and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return sINlA((self.hash_ref,self.account_id,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->sINlH:
  if not other:
   return sINly
  if not sINlF(other,StateFileRef):
   return sINly
  return(self.region==other.region and self.account_id==self.account_id and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->sINlH:
  for other in others:
   if self.congruent(other):
    return sINlY
  return sINly
 def metadata(self)->sINlf:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:sINlf,state_files:Set[StateFileRef],parent_ptr:sINlf):
  sINle(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:sINlf=parent_ptr
 def state_files_info(self)->sINlf:
  return "\n".join(sINlz(sINlE(lambda state_file:sINlf(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:sINlf,head_ptr:sINlf,message:sINlf,timestamp:sINlf=sINlf(datetime.now().timestamp()),delta_log_ptr:sINlf=sINli):
  self.tail_ptr:sINlf=tail_ptr
  self.head_ptr:sINlf=head_ptr
  self.message:sINlf=message
  self.timestamp:sINlf=timestamp
  self.delta_log_ptr:sINlf=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:sINlf,to_node:sINlf)->sINlf:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:sINlf,state_files:Set[StateFileRef],parent_ptr:sINlf,creator:sINlf,rid:sINlf,revision_number:sINlq,assoc_commit:Commit=sINli):
  sINle(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:sINlf=creator
  self.rid:sINlf=rid
  self.revision_number:sINlq=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(sINlE(lambda state_file:sINlf(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:sINlf,state_files:Set[StateFileRef],parent_ptr:sINlf,creator:sINlf,comment:sINlf,active_revision_ptr:sINlf,outgoing_revision_ptrs:Set[sINlf],incoming_revision_ptr:sINlf,version_number:sINlq):
  sINle(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(sINlE(lambda stat_file:sINlf(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
