node("docker") {
   stage "Checkout"
   checkout scm

   stage "Build"
   sh "python bootstrap.py"
   sh "bin/buildout"

   stage "Test"
   sh "bin/test"
}
