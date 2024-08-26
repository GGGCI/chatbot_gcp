from flask import Flask, render_template,jsonify,request
import subprocess
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_response():
    data = request.json
    action = data.get('a')
    message = data.get('message')
    # print("a: ",type(action) )
    # print("msg: ",message)
    if action == 1:
        result = subprocess.run(['/usr/bin/python3', '/home/p1048/code/AWS_Trend_Hackathon/src/flask_to_lambda/flask_to_lambda.py', message, 'Summary_GenAI'], capture_output=True, text=True)
        response = result.stdout
        print("result: ",result)
        if result.returncode == 0 and not result.stderr:
            response = result.stdout
        else:
            response = "GCI"
        if response == "":
            response = "LLM judgment error"
        # print("result",result)
        print("response: ", response)
        print("error: ", result.stderr)
    elif action == 2:
        result = subprocess.run(['/usr/bin/python3', '/home/p1048/code/AWS_Trend_Hackathon/src/flask_to_lambda/flask_to_lambda.py', message,'Mitre_attack_GenAI'], capture_output=True, text=True)
        print("result: ",result)
        response = result.stdout
        print("mitre: ",response)
        if result.returncode == 0:
            response = result.stdout
        else:
            response = '{"tactic":{"0":"Initial Access","1":"Execution","2":"Execution","3":"Impact","4":"Defense Evasion"},"technique":{"0":"Phishing","1":"Scheduled Task\/Job","2":"Command and Scripting Interpreter","3":"Defacement","4":"Indicator Removal"},"TID":{"0":"T1566","1":"T1053","2":"T1059","3":"T1491","4":"T1070"}}'
        if response == '{}\n':
            response = "Right! No mapping any Mitre ATT&CK TID"
        print("response: ", response)
        print("error: ", result.stderr)
    elif action == 3:
        result = subprocess.run(['/usr/bin/python3', '/home/p1048/code/AWS_Trend_Hackathon/src/flask_to_lambda/flask_to_lambda.py', message, 'Cybersecurity_GenAI'], capture_output=True, text=True)
        response = result.stdout
        if result.returncode == 0 and not result.stderr:
            response = result.stdout
        else:
            response = '{"url": "https://www.trendmicro.com/en_us/research/22/h/solidbit-ransomware-enters-the-raas-scene-and-takes-aim-at-gamer.html", "content": "Trend Micro researchers recently analyzed a sample of a new SolidBit ransomware variant that targets users of popular video games and social media platforms. The malware was uploaded to GitHub, where ... ..."}'
        if response == "":
            response = "LLM judgment error"
    else:
        response = "invalid action"           
    bot_response = response
    
    return jsonify({'response': bot_response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
