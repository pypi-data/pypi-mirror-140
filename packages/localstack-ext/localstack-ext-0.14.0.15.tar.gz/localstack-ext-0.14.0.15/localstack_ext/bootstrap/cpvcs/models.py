from datetime import datetime
OkCBs=str
OkCBD=int
OkCBr=super
OkCBm=False
OkCBI=isinstance
OkCBW=hash
OkCBa=bool
OkCBx=True
OkCBb=list
OkCBo=map
OkCBi=None
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class CPVCSObj:
 def __init__(self,hash_ref:OkCBs):
  self.hash_ref:OkCBs=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={OkCBs(MAIN):API_STATES_DIR,OkCBs(DDB):DYNAMODB_DIR,OkCBs(KINESIS):KINESIS_DIR}
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:OkCBs,rel_path:OkCBs,file_name:OkCBs,size:OkCBD,service:OkCBs,region:OkCBs,account_id:OkCBs,serialization:Serialization):
  OkCBr(StateFileRef,self).__init__(hash_ref)
  self.rel_path:OkCBs=rel_path
  self.file_name:OkCBs=file_name
  self.size:OkCBD=size
  self.service:OkCBs=service
  self.region:OkCBs=region
  self.account_id:OkCBs=account_id
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,account_id=self.account_id,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return OkCBm
  if not OkCBI(other,StateFileRef):
   return OkCBm
  return(self.hash_ref==other.hash_ref and self.account_id==other.account_id and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return OkCBW((self.hash_ref,self.account_id,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->OkCBa:
  if not other:
   return OkCBm
  if not OkCBI(other,StateFileRef):
   return OkCBm
  return(self.region==other.region and self.account_id==self.account_id and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->OkCBa:
  for other in others:
   if self.congruent(other):
    return OkCBx
  return OkCBm
 def metadata(self)->OkCBs:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:OkCBs,state_files:Set[StateFileRef],parent_ptr:OkCBs):
  OkCBr(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:OkCBs=parent_ptr
 def state_files_info(self)->OkCBs:
  return "\n".join(OkCBb(OkCBo(lambda state_file:OkCBs(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:OkCBs,head_ptr:OkCBs,message:OkCBs,timestamp:OkCBs=OkCBs(datetime.now().timestamp()),delta_log_ptr:OkCBs=OkCBi):
  self.tail_ptr:OkCBs=tail_ptr
  self.head_ptr:OkCBs=head_ptr
  self.message:OkCBs=message
  self.timestamp:OkCBs=timestamp
  self.delta_log_ptr:OkCBs=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:OkCBs,to_node:OkCBs)->OkCBs:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:OkCBs,state_files:Set[StateFileRef],parent_ptr:OkCBs,creator:OkCBs,rid:OkCBs,revision_number:OkCBD,assoc_commit:Commit=OkCBi):
  OkCBr(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:OkCBs=creator
  self.rid:OkCBs=rid
  self.revision_number:OkCBD=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(OkCBo(lambda state_file:OkCBs(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:OkCBs,state_files:Set[StateFileRef],parent_ptr:OkCBs,creator:OkCBs,comment:OkCBs,active_revision_ptr:OkCBs,outgoing_revision_ptrs:Set[OkCBs],incoming_revision_ptr:OkCBs,version_number:OkCBD):
  OkCBr(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(OkCBo(lambda stat_file:OkCBs(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
