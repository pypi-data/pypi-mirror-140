from datetime import datetime
dvaXC=str
dvaXG=int
dvaXI=super
dvaXk=False
dvaXl=isinstance
dvaXm=hash
dvaXH=bool
dvaXN=True
dvaXF=list
dvaXo=map
dvaXB=None
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class CPVCSObj:
 def __init__(self,hash_ref:dvaXC):
  self.hash_ref:dvaXC=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={dvaXC(MAIN):API_STATES_DIR,dvaXC(DDB):DYNAMODB_DIR,dvaXC(KINESIS):KINESIS_DIR}
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:dvaXC,rel_path:dvaXC,file_name:dvaXC,size:dvaXG,service:dvaXC,region:dvaXC,account_id:dvaXC,serialization:Serialization):
  dvaXI(StateFileRef,self).__init__(hash_ref)
  self.rel_path:dvaXC=rel_path
  self.file_name:dvaXC=file_name
  self.size:dvaXG=size
  self.service:dvaXC=service
  self.region:dvaXC=region
  self.account_id:dvaXC=account_id
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,account_id=self.account_id,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return dvaXk
  if not dvaXl(other,StateFileRef):
   return dvaXk
  return(self.hash_ref==other.hash_ref and self.account_id==other.account_id and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return dvaXm((self.hash_ref,self.account_id,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->dvaXH:
  if not other:
   return dvaXk
  if not dvaXl(other,StateFileRef):
   return dvaXk
  return(self.region==other.region and self.account_id==self.account_id and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->dvaXH:
  for other in others:
   if self.congruent(other):
    return dvaXN
  return dvaXk
 def metadata(self)->dvaXC:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:dvaXC,state_files:Set[StateFileRef],parent_ptr:dvaXC):
  dvaXI(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:dvaXC=parent_ptr
 def state_files_info(self)->dvaXC:
  return "\n".join(dvaXF(dvaXo(lambda state_file:dvaXC(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:dvaXC,head_ptr:dvaXC,message:dvaXC,timestamp:dvaXC=dvaXC(datetime.now().timestamp()),delta_log_ptr:dvaXC=dvaXB):
  self.tail_ptr:dvaXC=tail_ptr
  self.head_ptr:dvaXC=head_ptr
  self.message:dvaXC=message
  self.timestamp:dvaXC=timestamp
  self.delta_log_ptr:dvaXC=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:dvaXC,to_node:dvaXC)->dvaXC:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:dvaXC,state_files:Set[StateFileRef],parent_ptr:dvaXC,creator:dvaXC,rid:dvaXC,revision_number:dvaXG,assoc_commit:Commit=dvaXB):
  dvaXI(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:dvaXC=creator
  self.rid:dvaXC=rid
  self.revision_number:dvaXG=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(dvaXo(lambda state_file:dvaXC(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:dvaXC,state_files:Set[StateFileRef],parent_ptr:dvaXC,creator:dvaXC,comment:dvaXC,active_revision_ptr:dvaXC,outgoing_revision_ptrs:Set[dvaXC],incoming_revision_ptr:dvaXC,version_number:dvaXG):
  dvaXI(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(dvaXo(lambda stat_file:dvaXC(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
