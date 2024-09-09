import requests
import subprocess
import json
import pandas as pd
import re
import openai
import os

def call_Lambda_Summary_GenAI(context):
    openai.api_key = os.getenv('API_KEY')
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Summarize this: {context} and limit to 20 words"}
        ]
    )

    summary = response.choices[0].message['content'].strip()
    print(summary)
    return summary



def call_Lambda_Mitre_attack_GenAI(context): 
    openai.api_key = os.getenv('API_KEY')
    base_dir = os.getenv('PROJECT_BASE_PATH', '/default/path/to/project')
    data_dir = os.path.join(base_dir, 'data', 'database')
    output_dir = os.path.join(base_dir, 'src', 'flask_to_lambda')

    def call_Mitre_one(context):
        with open(os.path.join(output_dir,"Cybersecurity_Classification_define.json"), "r") as f: 
            Cybersecurity_Classification_define = f.read()

        instruction = "Please help me select the Cybersecurity Classification from content based on cybersecurity classification, and return them in JSON format. Only tell me the category names."
        prompt = f"prompt : {instruction} ; context: {context}\n\n Mitre_Attack Tactics definition : {Cybersecurity_Classification_define} \n Answer : "
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        mitre_one_response = response.choices[0].message['content'].strip().split("Answer : ")[-1]
        mitre_one_list = []
        for key in json.loads(Cybersecurity_Classification_define): 
            match = re.search(key, mitre_one_response)
            if match:
                mitre_one_list.append(match.group())

        mitre_one_list = list(set(mitre_one_list))
        return mitre_one_list


    def call_Mitre_two(context):
        Cybersecurity_Question_list = [
        "Active Scanning", "Gather Victim Host Information", "Gather Victim Identity Information",
        "Gather Victim Network Information", "Gather Victim Org Information", "Phishing for Information",
        "Search Closed Sources", "Search Open Technical Databases", "Search Open Websites/Domains",
        "Acquire Infrastructure", "Compromise Accounts", "Compromise Infrastructure", "Develop Capabilities",
        "Establish Accounts", "Obtain Capabilities", "Stage Capabilities", "Phishing", "Supply Chain Compromise",
        "Valid Accounts", "Command and Scripting Interpreter", "Inter-Process Communication", "Scheduled Task/Job",
        "System Services", "User Execution", "Account Manipulation", "Boot or Logon Autostart Execution",
        "Boot or Logon Initialization Scripts", "Create Account", "Create or Modify System Process",
        "Event Triggered Execution", "Hijack Execution Flow", "Modify Authentication Process",
        "Office Application Startup", "Pre-OS Boot", "Server Software Component", "Traffic Signaling",
        "Abuse Elevation Control Mechanism", "Access Token Manipulation", "Domain or Tenant Policy Modification",
        "Process Injection", "Execution Guardrails", "File and Directory Permissions Modification", "Hide Artifacts",
        "Impair Defenses", "Indicator Removal", "Masquerading", "Modify Cloud Compute Infrastructure",
        "Modify System Image", "Network Boundary Bridging", "Obfuscated Files or Information", "Subvert Trust Controls",
        "System Binary Proxy Execution", "System Script Proxy Execution", "Trusted Developer Utilities Proxy Execution",
        "Use Alternate Authentication Material", "Virtualization/Sandbox Evasion", "Weaken Encryption",
        "Adversary-in-the-Middle", "Brute Force", "Credentials from Password Stores", "Forge Web Credentials",
        "Input Capture", "OS Credential Dumping", "Steal or Forge Kerberos Tickets", "Unsecured Credentials",
        "Account Discovery", "Permission Groups Discovery", "Software Discovery", "System Location Discovery",
        "System Network Configuration Discovery", "Remote Service Session Hijacking", "Remote Services",
        "Archive Collected Data", "Data from Configuration Repository", "Data from Information Repositories",
        "Data Staged", "Email Collection", "Application Layer Protocol", "Data Encoding", "Data Obfuscation",
        "Dynamic Resolution", "Encrypted Channel", "Proxy", "Web Service", "Automated Exfiltration",
        "Exfiltration Over Alternative Protocol", "Exfiltration Over Other Network Medium", "Exfiltration Over Physical Medium",
        "Exfiltration Over Web Service", "Data Manipulation", "Defacement", "Disk Wipe", "Endpoint Denial of Service",
        "Network Denial of Service"
    ]

        instruction = "Please help me select the Cybersecurity Questions from content based on cybersecurity classification, and return them in JSON format. Only tell me the category names.Please provide me with the five category names."
        prompt = f"prompt: {instruction}; context: {context}\n\n Cybersecurity_Question_list: {Cybersecurity_Question_list}\n Answer: "

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        mitre_two_response = response.choices[0].message['content'].strip().split("Answer : ")[-1]

        mitre_two_list = []
        for key in Cybersecurity_Question_list:
            match = re.search(key, mitre_two_response)
            if match:
                mitre_two_list.append(match.group())

        return list(set(mitre_two_list))
    mitre_one_response = call_Mitre_one(context)
    mitre_two_response = call_Mitre_two(context)

    df = pd.read_json(os.path.join(data_dir,"Mitre_Attack_GenAI_related_table.json"))
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
    mitre_table.to_json(os.path.join(output_dir,"call_Lambda_Mitre_attack_GenAI_output.json"))

    # Mitre_att&ck_TID_table
    with open(os.path.join(output_dir,"call_Lambda_Mitre_attack_GenAI_output.json"), "r") as f :  
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