from localstack.utils.aws import aws_models
xpuCG=super
xpuCV=None
xpuCM=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  xpuCG(LambdaLayer,self).__init__(arn)
  self.cwd=xpuCV
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.xpuCM.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(RDSDatabase,self).__init__(xpuCM,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(RDSCluster,self).__init__(xpuCM,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(AppSyncAPI,self).__init__(xpuCM,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(AmplifyApp,self).__init__(xpuCM,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(ElastiCacheCluster,self).__init__(xpuCM,env=env)
class TransferServer(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(TransferServer,self).__init__(xpuCM,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(CloudFrontDistribution,self).__init__(xpuCM,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,xpuCM,env=xpuCV):
  xpuCG(CodeCommitRepository,self).__init__(xpuCM,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
