nvidia api key integration for later

step 0-(run one by one in terminal, if error occur run that command again)
commands-

python -m venv venv
venv\Scripts\activate


//
#path may start from (venv)
//

step 1-
pip install -r requirements.txt


step 2-
make .env file (just like .env.example) and replace `{API_KEY_GOOGLE_AI_STUDIO}` with actual apikey

step 3-
uvicorn main:app --reload


step 4-
http://localhost:8000/docs