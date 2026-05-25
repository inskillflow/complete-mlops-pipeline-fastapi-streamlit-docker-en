-------------------------
==> COMMANDS
-------------------------

<span style="color:#d32f2f;font-weight:700;">01</span> - git clone https://github.com/inskillflow/complete-mlops-pipeline-fastapi-streamlit-docker-en.git  
<span style="color:#d32f2f;font-weight:700;">02</span> - cd .\complete-mlops-pipeline-fastapi-streamlit-docker-en\  
<span style="color:#d32f2f;font-weight:700;">03</span> - cd .\part-04-mlflow-step-by-step-recap-running-the-training-in-docker\  
<span style="color:#d32f2f;font-weight:700;">04</span> - pwd   
<span style="color:#d32f2f;font-weight:700;">05</span> - Instruction 1 : Please be sure that you've started your docker Desktop (it's not a command)  
<span style="color:#d32f2f;font-weight:700;">06</span> - docker --version  
<span style="color:#d32f2f;font-weight:700;">07</span> - docker compose version  
<span style="color:#d32f2f;font-weight:700;">08</span> - docker ps  
<span style="color:#d32f2f;font-weight:700;">09</span> - docker compose up -d --build mlflow  
<span style="color:#d32f2f;font-weight:700;">10</span> - docker ps  
<span style="color:#d32f2f;font-weight:700;">11</span> - docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1  
<span style="color:#d32f2f;font-weight:700;">11</span> - docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5  
<span style="color:#d32f2f;font-weight:700;">12</span> - docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1  
<span style="color:#d32f2f;font-weight:700;">13</span> - Instruction 2 : Obeserve the result in http://localhost:5000/   
<span style="color:#d32f2f;font-weight:700;">14</span> - Instruction 3 :The experiments are not showing ..explain why? (you may have a look on docker-compose-option2.yml_  
<span style="color:#d32f2f;font-weight:700;">15</span> - docker compose down   
<span style="color:#d32f2f;font-weight:700;">16</span> - docker stop $(docker ps -a -q)  
<span style="color:#d32f2f;font-weight:700;">17</span> - docker rm $(docker ps -a -q)  
<span style="color:#d32f2f;font-weight:700;">18</span> - docker compose -f docker-compose-option2.yml up -d --build  
<span style="color:#d32f2f;font-weight:700;">19</span> - docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.1 --l1_ratio 0.1  
<span style="color:#d32f2f;font-weight:700;">20</span> - docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.5 --l1_ratio 0.5  
<span style="color:#d32f2f;font-weight:700;">21</span> - docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.9 --l1_ratio 0.1  
<span style="color:#d32f2f;font-weight:700;">22</span> - Instruction 4: Obeserve the result in http://localhost:5000/   
<span style="color:#d32f2f;font-weight:700;">23</span> - Instruction 5 : Are the experiments showing now ..What was the error in docker-compose.yml?

docker compose -f docker-compose-option2.yml down


-----------------------------------------------
==> USEFUL COMMANDS FOR TROUBELSHOOTING
-----------------------------------------------
docker compose down  
docker ps -a   
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q)  
docker ps -a   
docker compose up -d --build mlflow
