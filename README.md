# chatbot_gcp

1. setting enviroment variables
```
export API_KEY="your_openai_key"
export PROJECT_BASE_PATH="your_project_base_path"
```
2. docker build and run
```
cd "your chatbot_gcp directory"
docker build --network host -t mychatbot-image .
docker run -e API_KEY=${API_KEY} -e PROJECT_BASE_PATH="/chatbot" --net host --name mychatbot mychatbot-image:latest
```
