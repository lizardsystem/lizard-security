node("Docker on the jenkins master machine") {
   checkout scm
   sh "python bootstrap.py"
   sh "bin/buildout"
   sh "bin/test"
}
