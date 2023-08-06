import logging
bhlJd=bool
bhlJM=Exception
bhlJw=str
bhlJB=None
bhlJS=True
bhlJs=isinstance
bhlJk=NotImplementedError
bhlJm=super
import os
import threading
from abc import ABC
from functools import lru_cache
from typing import List,Optional,Union
from localstack.utils import common
from localstack.utils.common import in_docker,is_command_available,is_debian,rm_rf,run
INSTALL_LOCK=threading.RLock()
POSTGRES_RPM_REPOSITORY="https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
LOG=logging.getLogger(__name__)
@lru_cache()
def is_redhat()->bhlJd:
 return "rhel" in common.load_file("/etc/os-release","")
class PackageInstallationException(bhlJM):
 pass
class SystemNotSupportedException(PackageInstallationException):
 pass
class PackageInstaller(ABC):
 def __init__(self,log_package_name:Optional[bhlJw]):
  self.log_package_name=log_package_name
  self.logger=logging.getLogger(f"{__name__}.{log_package_name}")
  if log_package_name is bhlJB:
   self.logger.setLevel(logging.CRITICAL+1)
 def install(self,raise_on_error:bhlJd=bhlJS)->bhlJB:
  try:
   if not self._check_if_available():
    try:
     self.logger.debug("Preparing the installation of %s.",self.log_package_name)
     self._prepare_installation()
     self.logger.debug("Starting to install %s.",self.log_package_name)
     self._install_package()
     self.logger.debug("Executing post-processing of %s.",self.log_package_name)
     self._post_process()
    except bhlJM as e:
     if bhlJs(e,PackageInstallationException):
      raise
     else:
      suffix=(f" ({self.log_package_name})." if self.log_package_name is not bhlJB else ".")
      raise PackageInstallationException(f"The installation failed{suffix}")from e
    self._verify_installation()
    self.logger.debug("Successfully installed %s.",self.log_package_name)
   else:
    self.logger.debug("%s is already available.",self.log_package_name)
  except PackageInstallationException as e:
   if raise_on_error:
    raise
   else:
    if self.logger.isEnabledFor(logging.DEBUG):
     self.logger.exception("Error while installing package %s.",self.log_package_name)
    else:
     self.logger.error(e)
 def _check_if_available(self)->bhlJd:
  raise bhlJk
 def _prepare_installation(self)->bhlJB:
  pass
 def _install_package(self)->bhlJB:
  raise bhlJk
 def _post_process(self)->bhlJB:
  pass
 def _verify_installation(self)->bhlJB:
  if not self._check_if_available():
   package_info=(f" of {self.log_package_name}" if self.log_package_name is not bhlJB else "")
   raise PackageInstallationException(f"The installation{package_info} failed (verification failed).")
class MultiPackageInstaller(PackageInstaller):
 def __init__(self,log_package_name:Optional[bhlJw],package_installers:Union[PackageInstaller,List[PackageInstaller]]):
  bhlJm(MultiPackageInstaller,self).__init__(log_package_name=log_package_name)
  self.package_installers=(package_installers if bhlJs(package_installers,List)else[package_installers])
 def install(self,raise_on_error:bhlJd=bhlJS):
  for package_installer in self.package_installers:
   package_installer.install(raise_on_error=raise_on_error)
class OSSpecificPackageInstaller(MultiPackageInstaller):
 def __init__(self,debian_installers:PackageInstaller,redhat_installers:PackageInstaller):
  package_installers=[]
  if is_debian():
   package_installers=debian_installers
  elif is_redhat():
   package_installers=redhat_installers
  bhlJm(OSSpecificPackageInstaller,self).__init__(log_package_name=self.__class__.__name__,package_installers=package_installers)
 def install(self,raise_on_error:bhlJd=bhlJS):
  try:
   if not in_docker():
    raise SystemNotSupportedException("OS level packages are only installed within docker containers.")
   elif not is_debian()and not is_redhat():
    raise SystemNotSupportedException("The current operating system is currently not supported.")
   else:
    bhlJm(OSSpecificPackageInstaller,self).install(raise_on_error=raise_on_error)
  except PackageInstallationException as e:
   if raise_on_error:
    raise
   else:
    if self.logger.isEnabledFor(logging.DEBUG):
     self.logger.exception("Error while installing package %s.",self.log_package_name)
    else:
     self.logger.error(e)
class DebianPackageInstaller(PackageInstaller,ABC):
 def __init__(self,package_name:bhlJw):
  bhlJm(DebianPackageInstaller,self).__init__(log_package_name=package_name)
 def _install_os_packages(self,packages:Union[bhlJw,List[bhlJw]]):
  packages=packages if bhlJs(packages,List)else[packages]
  with INSTALL_LOCK:
   run(["apt-get","update"])
   run(["apt-get","install","-y","--no-install-recommends"]+packages)
class RedHatPackageInstaller(PackageInstaller,ABC):
 def __init__(self,package_name:bhlJw):
  bhlJm(RedHatPackageInstaller,self).__init__(log_package_name=package_name)
 def _install_os_packages(self,packages:Union[bhlJw,List[bhlJw]]):
  packages=packages if bhlJs(packages,List)else[packages]
  with INSTALL_LOCK:
   run(["dnf","install","-y"]+packages)
DEBIAN_POSTGRES_LIB_FOLDER="/usr/lib/postgresql/11/lib"
REDHAT_POSTGRES_LIB_FOLDER="/usr/pgsql-11/lib"
class DebianPostgres11Installer(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianPostgres11Installer,self).__init__("postgres11")
 def _check_if_available(self)->bhlJd:
  return is_command_available("psql")
 def _install_package(self)->bhlJB:
  self._install_os_packages("postgresql-11")
class RedHatPostgres11Installer(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatPostgres11Installer,self).__init__("postgres11")
 def _check_if_available(self)->bhlJd:
  return is_command_available("psql")
 def _prepare_installation(self)->bhlJB:
  self._install_os_packages(POSTGRES_RPM_REPOSITORY)
 def _install_package(self)->bhlJB:
  self._install_os_packages(["postgresql11-devel","postgresql11-server"])
 def _post_process(self)->bhlJB:
  run("ln -s /usr/pgsql-11/bin/pg_config /usr/bin/pg_config")
class DebianPlPythonInstaller(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianPlPythonInstaller,self).__init__("plpython3")
 def _check_if_available(self)->bhlJd:
  return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/plpython3.so")
 def _install_package(self)->bhlJB:
  self._install_os_packages("postgresql-plpython3-11")
class RedHatPlPythonInstaller(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatPlPythonInstaller,self).__init__("plpython3")
 def _check_if_available(self)->bhlJd:
  return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/plpython3.so")
 def _install_package(self)->bhlJB:
  self._install_os_packages("postgresql11-plpython3")
postgres_installer=OSSpecificPackageInstaller(debian_installers=MultiPackageInstaller("PostgreSQL",[DebianPostgres11Installer(),DebianPlPythonInstaller()]),redhat_installers=MultiPackageInstaller("PostgreSQL",[RedHatPostgres11Installer(),RedHatPlPythonInstaller()]))
class DebianMariaDBInstaller(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianMariaDBInstaller,self).__init__("MariaDB")
 def _check_if_available(self)->bhlJd:
  return is_command_available("mysqld")
 def _install_package(self)->bhlJB:
  self._install_os_packages(["mariadb-server","mariadb-client"])
class RedHatMariaDBInstaller(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatMariaDBInstaller,self).__init__("MariaDB")
 def _check_if_available(self)->bhlJd:
  return is_command_available("mysqld")
 def _install_package(self)->bhlJB:
  raise PackageInstallationException("MariaDB currently cannot be installed on RedHat")
mariadb_installer=OSSpecificPackageInstaller(debian_installers=DebianMariaDBInstaller(),redhat_installers=RedHatMariaDBInstaller())
class DebianTimescaleDBInstaller(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianTimescaleDBInstaller,self).__init__("timescaledb")
 def _check_if_available(self)->bhlJd:
  return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/timescaledb.so")
 def _install_package(self)->bhlJB:
  self._install_os_packages(["gcc","cmake","gcc","git"])
  ts_dir="/tmp/timescaledb"
  tag="2.0.0-rc4"
  run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
  run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
  rm_rf("/tmp/timescaledb")
class RedHatTimescaleDBInstaller(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatTimescaleDBInstaller,self).__init__("timescaledb")
 def _check_if_available(self)->bhlJd:
  return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/timescaledb.so")
 def _install_package(self)->bhlJB:
  self._install_os_packages(["gcc","cmake","gcc","git","redhat-rpm-config"])
  ts_dir="/tmp/timescaledb"
  tag="2.0.0-rc4"
  run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
  run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
  rm_rf("/tmp/timescaledb")
timescaledb_installer=OSSpecificPackageInstaller(debian_installers=DebianTimescaleDBInstaller(),redhat_installers=RedHatTimescaleDBInstaller())
class DebianRedisInstaller(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianRedisInstaller,self).__init__("Redis")
 def _check_if_available(self)->bhlJd:
  return is_command_available("redis-server")
 def _install_package(self)->bhlJB:
  self._install_os_packages("redis-server")
class RedHatRedisInstaller(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatRedisInstaller,self).__init__("Redis")
 def _check_if_available(self)->bhlJd:
  return is_command_available("redis-server")
 def _install_package(self)->bhlJB:
  raise PackageInstallationException("Redis currently cannot be installed on RedHat")
redis_installer=OSSpecificPackageInstaller(debian_installers=DebianRedisInstaller(),redhat_installers=RedHatRedisInstaller())
class DebianMosquittoInstaller(DebianPackageInstaller):
 def __init__(self):
  bhlJm(DebianMosquittoInstaller,self).__init__("Mosquitto")
 def _check_if_available(self)->bhlJd:
  return is_command_available("mosquitto")
 def _install_package(self)->bhlJB:
  self._install_os_packages("mosquitto")
class RedHatMosquittoInstaller(RedHatPackageInstaller):
 def __init__(self):
  bhlJm(RedHatMosquittoInstaller,self).__init__("Mosquitto")
 def _check_if_available(self)->bhlJd:
  return is_command_available("mosquitto")
 def _install_package(self)->bhlJB:
  raise PackageInstallationException("Mosquitto currently cannot be installed on RedHat")
mosquitto_installer=OSSpecificPackageInstaller(debian_installers=DebianMosquittoInstaller(),redhat_installers=RedHatMosquittoInstaller())
# Created by pyminifier (https://github.com/liftoff/pyminifier)
