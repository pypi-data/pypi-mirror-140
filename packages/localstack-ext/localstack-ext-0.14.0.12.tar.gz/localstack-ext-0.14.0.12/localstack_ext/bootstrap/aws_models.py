from localstack.utils.aws import aws_models
XdYen=super
XdYeK=None
XdYef=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  XdYen(LambdaLayer,self).__init__(arn)
  self.cwd=XdYeK
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.XdYef.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(RDSDatabase,self).__init__(XdYef,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(RDSCluster,self).__init__(XdYef,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(AppSyncAPI,self).__init__(XdYef,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(AmplifyApp,self).__init__(XdYef,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(ElastiCacheCluster,self).__init__(XdYef,env=env)
class TransferServer(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(TransferServer,self).__init__(XdYef,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(CloudFrontDistribution,self).__init__(XdYef,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,XdYef,env=XdYeK):
  XdYen(CodeCommitRepository,self).__init__(XdYef,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
