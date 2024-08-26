import requests
import subprocess
import json
import pandas as pd
import re
import google.auth.transport.requests
import google.oauth2.id_token

def call_Lambda_Summary_GenAI(context):
    api_gateway_url = "https://us-central1-leafy-racer-428314-t9.cloudfunctions.net/test"
    lambda_url = f"{api_gateway_url}/call_openai_summary"
    
    audience = api_gateway_url
    request = google.auth.transport.requests.Request()
    token = google.oauth2.id_token.fetch_id_token(request, audience)

    payload = {
        "context": context
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(lambda_url, json=payload, headers=headers)
    print(response.text)
    return response.text



def call_Lambda_Mitre_attack_GenAI(context):  
    def call_Mitre_one(context):
        api_gateway_url = "https://call-mitre1-qi454j62ua-uc.a.run.app"
        lambda_url = f"{api_gateway_url}/call_mitre_one"
        audience = api_gateway_url
        request = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(request, audience)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "context": context
        }

        response = requests.post(lambda_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            mitre_one_list = response.json()
            return mitre_one_list
        else:
            print(f"Failed to call Cloud Run: {response.status_code}")
            return []


    def call_Mitre_two(context):
        api_gateway_url = "https://call-mitre2-qi454j62ua-uc.a.run.app"
        lambda_url = f"{api_gateway_url}/call_mitre_two"

        # Authenticated request setup
        audience = lambda_url
        request = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(request, audience)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "context": context
        }

        response = requests.post(lambda_url, json=payload, headers=headers)
        mitre_two_list = response.json()

        return mitre_two_list
    mitre_one_response = call_Mitre_one(context)
    mitre_two_response = call_Mitre_two(context)

    df = pd.read_json("/home/p1048/code/AWS_Trend_Hackathon/data/database/Mitre_Attack_GenAI_related_table.json")
    result_list = []
    for tactic in mitre_one_response : 
        for technique in mitre_two_response : 
            if len(df[(df["tactic"] == tactic) & (df["technique"] == technique)]) != 0 : 
                result = {
                    "tactic" : tactic,
                    "technique" : technique,
                    "TID" : df[(df["tactic"] == tactic) & (df["technique"] == technique)]["TID"].values[0]
                }
                result_list.append(result)

    
    mitre_table = pd.DataFrame(result_list)
    mitre_table.to_json("/home/p1048/code/AWS_Trend_Hackathon/src/flask_to_lambda/call_Lambda_Mitre_attack_GenAI_output.json")

    # Mitre_att&ck_TID_table
    with open("/home/p1048/code/AWS_Trend_Hackathon/src/flask_to_lambda/call_Lambda_Mitre_attack_GenAI_output.json", "r") as f :  
        Mitre_attack_TID_table = f.read()

    print(Mitre_attack_TID_table)

    return Mitre_attack_TID_table


def call_Lambda_Cybersecurity_GenAI(api_gatway_url, deploy_version, context):
    def elasticsearch_data_dump(hostip, pattern_index, dsl_query) : 
        INPUT_URL = f"https://@{hostip}/{pattern_index}" # "https://user:password@hostip/winlogbeat-*"
        OUTPUT_FILE = "elk_dump.json"

        SEARCH_BODY = dsl_query

        # 轉換SEARCH_BODY為JSON字符串
        search_body_json = json.dumps(SEARCH_BODY)

        # 使用subprocess運行elasticdump命令
        subprocess.run([
            "elasticdump",
            "--ssl-allow-unauthorized",
            "--input=" + INPUT_URL,
            "--output=" + OUTPUT_FILE,
            "--type=data",
            "--searchBody=" + search_body_json
        ], check=True)

    lambda_url = f"{api_gatway_url}/{deploy_version}/call_Lambda_Cybersecurity_GenAI_Jim"
    json_body = {
        'inputs': context
    }

    dsl_response = requests.post(lambda_url, data=json_body)
    dsl_response = json.loads(dsl_response.text)[0]["generated_text"]
    print(dsl_response)
    # elk dump Cybersecurity information
    # password 可能要改
    # elasticsearch_data_dump(hostip = "127.0.0.1", pattern_index = "Cybersecurity_information", dsl_query = dsl_response["body"])
    # df = pandas.read_json("elk_dump.json")

    # df_return = df.sample(1)
    # url = df_return["url"].values()[0]
    # content = df_return["content"].values()[0]

    # Cybersecurity_information = {
    #     "url" : url,
    #     "content" : content[0][0:200].replace("\xa0", " ") + "... ...",
    # }
    # print(Cybersecurity_information)