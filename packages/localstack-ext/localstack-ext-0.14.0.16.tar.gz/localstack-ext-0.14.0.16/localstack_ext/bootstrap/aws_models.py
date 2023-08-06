from localstack.utils.aws import aws_models
tNKBh=super
tNKBj=None
tNKBI=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  tNKBh(LambdaLayer,self).__init__(arn)
  self.cwd=tNKBj
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.tNKBI.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(RDSDatabase,self).__init__(tNKBI,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(RDSCluster,self).__init__(tNKBI,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(AppSyncAPI,self).__init__(tNKBI,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(AmplifyApp,self).__init__(tNKBI,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(ElastiCacheCluster,self).__init__(tNKBI,env=env)
class TransferServer(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(TransferServer,self).__init__(tNKBI,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(CloudFrontDistribution,self).__init__(tNKBI,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,tNKBI,env=tNKBj):
  tNKBh(CodeCommitRepository,self).__init__(tNKBI,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
