from localstack.utils.aws import aws_models
NrApE=super
NrApy=None
NrAps=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  NrApE(LambdaLayer,self).__init__(arn)
  self.cwd=NrApy
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.NrAps.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(RDSDatabase,self).__init__(NrAps,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(RDSCluster,self).__init__(NrAps,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(AppSyncAPI,self).__init__(NrAps,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(AmplifyApp,self).__init__(NrAps,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(ElastiCacheCluster,self).__init__(NrAps,env=env)
class TransferServer(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(TransferServer,self).__init__(NrAps,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(CloudFrontDistribution,self).__init__(NrAps,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,NrAps,env=NrApy):
  NrApE(CodeCommitRepository,self).__init__(NrAps,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
