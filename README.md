​![tag : innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
# uAgent-Based-Medical-Trial-Matching

A Fetch.ai [AgentVerse](https://docs.fetch.ai/) application using two uAgents — one representing doctors and the other representing patients/volunteers — to automate and simplify the matching process for medical and drug trials.

##  Overview

This system is built around two autonomous agents:

- [**`FindAPatient`**](test-agent://agent1qwg3rr7km9z980ummuq2uynhyph9kcjju39j072l5kxj2rf76h6cvxwaw64): Acts as a doctor agent searching for suitable patients for a medical or drug trial.
- [**`iVolunteer`**](test-agent://agent1qw8mgv2rqz2ulzaz8x6tksf2eqmrrulmxjf4mmw0j7733qkzp2dyk23zf5m): Acts as a patient/volunteer agent that registers interest and availability for trials based on category.

The agents communicate via [uAgents](https://github.com/fetchai/uAgents) and leverage **ASI-1 MINI (ASI-MINI)**, a powerful AI model, to intelligently analyze patient data and handle natural language queries from doctors.

---

##  Core Functionality

### 1. **Patient Registration (`iVolunteer.py`)**
- Registers patient/volunteer details such as name, age, gender, contact info, and trial category.
- Responds to doctor trial matching requests.
- Sends registration data to the doctor agent upon startup.

### 2. **Doctor Query & Matching (`FindAPatient.py`)**
- Receives volunteer registry from iVolunteer.
- Accepts chat-based queries from doctors using natural language (e.g., "Find patients under 30").
- Processes queries via **ASI-MINI**, returning relevant matches based on age, category, etc.
- Sends trial invitations to matching patients.

### 3. **Authentication & Security**
- Doctor agent requires a keyword (e.g., "fetch") to start a session before processing queries.

---

## How to Use

### Prerequisites
- Python 3.9+
- uAgents
- openai Python client (used for ASI-1)

### Installation
```bash
pip install uagents openai
```

###  ASI-1 API Key
Replace the placeholder in `FindAPatient.py` with your actual ASI-1 API key:

```python
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key='your_asi1_api_key_here'
)
```

### Running the Agents

In one terminal:
```bash
python iVolunteer.py
```

In another terminal:
```bash
python FindAPatient.py
```

### Chatting with the Doctor Agent
Once running, you can initiate a session and send queries using the chat protocol:

- Send the password (e.g., `"fetch"`) to authenticate.
- Then send natural language queries like:
  - `"Find patients over 60 years old"`
  - `"I need female patients for a cancer trial"`

The system responds with matches and initiates contact with patients if available.

---

## File Structure

```bash
.
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── agents/
    ├── FindAPatient.py    # Doctor agent handling queries and matching
    └── iVolunteer.py      # Volunteer agent for patient data registration
```

---

## Function Summary

### FindAPatient.py
- `start`: Initializes storage variables.
- `handle_chat`: Manages authentication and processes doctor queries using ASI-1.
- `send_offer`: Periodically attempts to contact uncontacted patients.
- `response_handler`: Handles responses from patients.
- `handle_registry`: Receives patient registry from volunteer.
- `handle_ack`: Resets authentication when chat session ends.

---

## 📈 Business Case

Clinical trials and medical studies face major challenges in recruiting suitable patients quickly and effectively. Many volunteers are either unaware of relevant trials or are matched inefficiently, leading to delays and increased costs.

This system solves these problems by:
- Automating patient-trial matching with intelligent agents.
- Reducing the overhead and manual effort for both researchers and patients.
- Enhancing outreach using chat-based interaction and smart LLM query handling.
- Allowing decentralized deployment using Fetch.ai's AgentVerse.

**Target Users**:
- Clinical researchers
- Hospitals and pharmaceutical companies
- Independent medical trial organizations

**Benefits**:
- Faster patient acquisition
- Improved targeting of relevant candidates
- Reduced administrative overhead
- Scalable and customizable agent framework

---

## 💰 ROI Analysis

| Factor                             | Traditional Approach         | Agent-Based System                  |
|------------------------------------|------------------------------|--------------------------------------|
| Patient Acquisition Time           | Weeks to months              | Minutes to hours                     |
| Human Resources                    | Multiple recruiters needed   | 1–2 operators + agents               |
| Cost per Patient Match             | High ($100–$1000+)           | Low (near-zero per query)           |
| Trial Drop-out Risk                | Higher due to poor matching  | Lower with intelligent filtering     |
| Scalability                        | Limited                      | Easily scalable across geographies   |

**Estimated ROI Over 6 Months**:
- 60–80% cost reduction in patient recruitment
- 3–5x faster onboarding times
- Better data for targeted trial design

With minimal deployment cost and integration effort, this agent-based approach can transform clinical trial logistics into a more agile, intelligent, and cost-effective process.

---

##  Powered By

- [Fetch.ai AgentVerse](https://agentverse.ai/)
- [uAgents framework](https://github.com/fetchai/uAgents)
- [ASI-1 MINI LLM](https://asi1.ai)

---

##  License

This project is licensed under the MIT License.
