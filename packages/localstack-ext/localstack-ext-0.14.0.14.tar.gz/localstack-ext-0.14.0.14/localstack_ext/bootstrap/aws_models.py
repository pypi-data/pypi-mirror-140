from localstack.utils.aws import aws_models
qMTpc=super
qMTpD=None
qMTpR=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  qMTpc(LambdaLayer,self).__init__(arn)
  self.cwd=qMTpD
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.qMTpR.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(RDSDatabase,self).__init__(qMTpR,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(RDSCluster,self).__init__(qMTpR,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(AppSyncAPI,self).__init__(qMTpR,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(AmplifyApp,self).__init__(qMTpR,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(ElastiCacheCluster,self).__init__(qMTpR,env=env)
class TransferServer(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(TransferServer,self).__init__(qMTpR,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(CloudFrontDistribution,self).__init__(qMTpR,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,qMTpR,env=qMTpD):
  qMTpc(CodeCommitRepository,self).__init__(qMTpR,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
