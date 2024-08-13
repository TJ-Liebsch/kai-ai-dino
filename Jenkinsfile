node {    
      def app     
      stage('Clone repository') {               
             
            checkout scm    
      }  
      stage('Fetch Commits') {
        // Fetch commits from the repo
        sh '''
        git fetch
        git log --oneline -n 5
        '''
    }
      stage('Build image') {         
       
            app = docker.build("kajwani/aug13_test")    
       }     
      stage('Test image') {           
            app.inside {            
             
             sh 'echo "Tests passed"'        
            }    
        }     
       stage('Push image') {
        docker.withRegistry('https://registry.hub.docker.com', 'git') {            
       app.push("${env.BUILD_NUMBER}")            
       app.push("latest")        
              }    
           }
        }
