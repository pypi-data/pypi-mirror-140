from typing import Dict
fChVp=staticmethod
fChVL=None
fChVk=str
fChVc=False
from localstack.services.cloudformation.deployment_utils import(generate_default_name_without_stack,params_list_to_dict)
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class QLDBLedger(GenericBaseModel):
 @fChVp
 def cloudformation_type():
  return "AWS::QLDB::Ledger"
 def get_physical_resource_id(self,attribute=fChVL,**kwargs):
  return self.props.get("Name")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("qldb")
  ledger_name=self.resolve_refs_recursively(stack_name,self.props.get("Name"),resources)
  result=client.describe_ledger(Name=ledger_name)
  return result
 @fChVp
 def add_defaults(resource:Dict,stack_name:fChVk):
  props=resource["Properties"]
  if not props.get("Name"):
   props["Name"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 @fChVp
 def get_deploy_templates():
  def _delete_ledger(resource_id,resources,*args,**kwargs):
   qldb=aws_stack.connect_to_service("qldb")
   props=resources[resource_id]["Properties"]
   ledger_name=props.get("Name")
   qldb.update_ledger(Name=ledger_name,DeletionProtection=fChVc)
   qldb.delete_ledger(Name=ledger_name)
  return{"create":{"function":"create_ledger","parameters":["KmsKey","DeletionProtection","Name","PermissionsMode",{"Tags":params_list_to_dict("Tags")}]},"delete":{"function":_delete_ledger}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
