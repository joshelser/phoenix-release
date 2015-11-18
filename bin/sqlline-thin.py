#!/usr/bin/env python
############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
############################################################################

import os
import subprocess
import sys
import phoenix_utils
import atexit
import urlparse

global childProc
childProc = None
def kill_child():
    if childProc is not None:
        childProc.terminate()
        childProc.kill()
        if os.name != 'nt':
            os.system("reset")
atexit.register(kill_child)

phoenix_utils.setPath()

url = "localhost:8765"
sqlfile = ""

def usage_and_exit():
    sys.exit("usage: sqlline-thin.py [host[:port]] [sql_file]")

def cleanup_url(url):
    parsed = urlparse.urlparse(url)
    if parsed.scheme == "":
        url = "http://" + url
        parsed = urlparse.urlparse(url)
    if ":" not in parsed.netloc:
        url = url + ":8765"
    return url


if len(sys.argv) == 1:
    pass
elif len(sys.argv) == 2:
    if os.path.isfile(sys.argv[1]):
        sqlfile = sys.argv[1]
    else:
        url = sys.argv[1]
elif len(sys.argv) == 3:
    url = sys.argv[1]
    sqlfile = sys.argv[2]
else:
    usage_and_exit()

url = cleanup_url(url)

if sqlfile != "":
    sqlfile = "--run=" + sqlfile

colorSetting = "true"
# disable color setting for windows OS
if os.name == 'nt':
    colorSetting = "false"

java_cmd = 'java -cp "' + phoenix_utils.hbase_conf_dir + os.pathsep + phoenix_utils.phoenix_thin_client_jar + \
    os.pathsep + phoenix_utils.hadoop_conf + os.pathsep + phoenix_utils.hadoop_classpath + '" -Dlog4j.configuration=file:' + \
    os.path.join(phoenix_utils.current_dir, "log4j.properties") + \
    " sqlline.SqlLine -d org.apache.phoenix.queryserver.client.Driver " + \
    " -u jdbc:phoenix:thin:url=" + url + \
    " -n none -p none --color=" + colorSetting + " --fastConnect=false --verbose=true " + \
    " --isolation=TRANSACTION_READ_COMMITTED " + sqlfile

exitcode = subprocess.call(java_cmd, shell=True)
sys.exit(exitcode)
