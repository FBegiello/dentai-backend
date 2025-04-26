# DentAI - backend
DentAI is a smart agentic dentist assistant allowing dentists to work without distractions - simply dictate your observations or retrieve patient history by voice commands. The assistant support voice inputs during a check-up and offers a final summarisation of visit ready for inclusin in documentation.

Core funtionalities are:
- Voice based interactions with specialised agent,
- Marking of dental state, per tooth, per surface in responce to voice instructions,
- Retrieval of patient dental history and medical operations from included storage,
- Interactive voice agent responding to instructions with voice messages,
- Generation of final notes for submission into the database,

![Main screen](https://github.com/FBegiello/dentai-backend/tree/main/misc/screen-1.png "Main screen")
![Conditions](https://github.com/FBegiello/dentai-backend/tree/main/misc/screen-2.png "Condition selection")

The core agent is built with OpenAI AgentSDK - we use a core agent for base interactions, with dedicated FunctionTool for tooth condition selection based on user voice inputs, and FileSearch over a simple vectore storage containing patient information. Text to speech capabilites are covered using OpenAI Text to speech models - we serve generated audio to the frontend application. User inputs are submitted from frontend, based on a simple VAD functionalities on the browser side. The backed receives only segments containing instructions and notes. After ending the interaction, a final note is generaterd, summing up the visit, that can be appended to the full dental history.

## Futer vision
DentAI platform could be easily integrated with EHR systems, serving the notes using structureg output from LLM in FHIR format, or any other desirable medical notation. Furthermore, using patient medical history and doctor recomendations, we could use the voice agent to make reminder calls, booking visits for patients, or write reminder emails using text mode. By implementing a callendar or callendar app integration (i.e. google callendar) the agent could book visits straight into the dentist schedule, taking into account current visit.

## Project setup
### Prerequisites
- python 3.11+ (can be set up with pyenv)
- poetry (https://python-poetry.org/)

All dependecies are installed through poetry using *poetry install*


### Steps
- clone repo
- $ poetry install

### Config
Config is powered by pydantic
Environment variables are loaded by default from .env file in config folder but can be overriden with building ARG for docker (i.e. ARG DOTFILE=.env.prod)

### Docker
Project can be build with docker compose -f docker/docker-compose.yml build and run with docker compose -f docker/docker-compose.yml up.
There is a Makefile to streamline this process - see commands for details. Core commands are:

- make build:	## Builds docker image
- make run:	## Runs the envionment in detached mode


