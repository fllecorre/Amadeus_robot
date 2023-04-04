node {
  deleteDir()
  checkout scm
  docker.withRegistry('http://docker-release-qtools-nce.nce.dockerhub.rnd.amadeus.net', 'IZ_USER') {   
    docker.image('docker-release-qtools-nce.nce.dockerhub.rnd.amadeus.net/a2ewhale_act:latest').inside('-u root --privileged --entrypoint= -v /remote/tmp/weekly/a2ewhale_results:/remote/tmp/weekly/a2ewhale_results -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY')
    {
      stage('Build Environment'){
        sh "chmod 777 /remote/tmp/weekly/a2ewhale_results"        
        sh "echo \"To connect remotely to the container, type: docker -H tcp://\$(echo \$NODE_NAME | cut -d'-' -f2):1061 exec -ti \$(cat /proc/self/cgroup | head -n 1 | cut -d '/' -f3) /bin/bash\""
        sh "echo \"PAUSED FOR 30s to let you press Pause button\""
        sh "sleep 30s"
        try {
          sh "a2ewhale -v dir pom.xml -p maven_cmd:\"antrun:run@Build_test_env\""
        }
        catch(Exception e){
          println("Exception: ${e}")
        }
      }
      stage('Execute E2E tests'){
        try {
          sh "echo \"Ready to go\""
          sh "chmod 777 /remote/tmp/weekly/a2ewhale_results"
          withCredentials([
                    file(credentialsId: 'PAY_CYBERARK_CERTIFICATE', variable: 'CERT'),
                    file(credentialsId: 'PAY_CYBERARK_KEY', variable: 'CKEY')]){
                      sh "a2ewhale -v dir pom.xml -p maven_cmd:\"clean antrun:run@launch_QCP_tests\""
                    }
        }
        catch(Exception e){
          println("Exception: ${e}")
        } 
        junit '**/result.xml' 
      }
      stage('Set Regression final result') {
        sh "echo \"RESULT: ${currentBuild.currentResult}\""
        if (currentBuild.result == "UNSTABLE") {
          currentBuild.result = "FAILURE"
        }
      }
    } 
  }
}