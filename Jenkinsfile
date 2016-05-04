node("nenskins14docker") {
   stage "Checkout"
   checkout scm

   stage "Build"
   sh "python bootstrap.py"
   sh "bin/buildout"

   stage "Test"
   sh "bin/test | true"
   step $class: 'JUnitResultArchiver', testResults: 'nosetests.xml'
   publishHTML target: [reportDir: 'htmlcov', reportFiles: 'index.html', reportName: 'Coverage report']
}
