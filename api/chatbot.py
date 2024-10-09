from http.server import BaseHTTPRequestHandler
import json
import re
import uuid
import os


# Conversation class remains unchanged
class Conversation:

    def __init__(self):
        self.state = "initial"
        self.current_topic = None
        self.severity = None
        self.files = []


# Store conversation states
conversations = {}

# Updated dictionary of possible inquiries, responses, and follow-up questions
responses = {
    "initial": {
        r"hello|hi|hey":
        "Welcome to the Old English Village GP. How may I assist you today?",
        r"headache|migraine": {
            "response":
            "I see you're experiencing head pain. Can you describe the severity on a scale of 1 to 10?",
            "next_state": "headache_severity"
        },
        r"joint pain|injury": {
            "response":
            "When did your pain begin? (e.g., recently or over a long time)",
            "next_state": "joint_pain_timing"
        },
        r"cold|flu|fever": {
            "response":
            "I'm sorry to hear you're feeling unwell. Do you have a fever?",
            "next_state": "cold_flu_fever"
        },
        r"stomach|digestion|nausea": {
            "response":
            "Stomach troubles can be quite bothersome. Is the discomfort constant or does it come and go?",
            "next_state": "stomach_details"
        },
        r"anxiety|stress|nerves": {
            "response":
            "I understand you're feeling anxious or stressed. Have you experienced any physical symptoms like rapid heartbeat or sweating?",
            "next_state": "anxiety_details"
        },
        r"insomnia|sleep": {
            "response":
            "Difficulty sleeping can be quite troubling. How long have you been experiencing sleep issues?",
            "next_state": "sleep_duration"
        },
        r"pain|ache|sore": {
            "response":
            "I'm sorry to hear you're in pain. Can you point to where it hurts the most?",
            "next_state": "pain_location"
        },
        r"upload|file|document": {
            "response": "You can upload a file. Please provide the file path.",
            "next_state": "file_upload"
        },
        r"mental health|depressed|anxious": {
            "response": "How have you been feeling emotionally lately?",
            "next_state": "mental_health_assessment"
        }
    },
    "headache_severity": {
        r"(\d+)": {
            "response": lambda severity:
            f"I see, a severity of {severity}. For mild headaches (1-3), I recommend rest and hydration. For moderate (4-7), try a cool compress and a tincture of willow bark. For severe headaches (8-10), please seek immediate medical attention.",
            "next_state": "initial"
        }
    },
    "joint_pain_timing": {
        r"recent|today|yesterday": {
            "response": "Can you rate the pain from 1 to 10?",
            "next_state": "joint_pain_severity"
        },
        r"chronic|long time": {
            "response":
            "It seems like you might need support for chronic pain. Are you able to move the affected area?",
            "next_state": "chronic_joint_mobility"
        }
    },
    "joint_pain_severity": {
        r"([8-9]|10)": {
            "response":
            "This sounds quite severe. I recommend visiting Accident & Emergency (A&E) as soon as possible.",
            "next_state": "initial"
        },
        r"([5-7])": {
            "response":
            "You might want to visit a Minor Injuries Unit (MIU) or consult with a First Contact Physiotherapist.",
            "next_state": "initial"
        },
        r"[1-4]": {
            "response":
            "For mild pain, you can try resting and over-the-counter pain relief. If it persists, consult your GP.",
            "next_state": "initial"
        }
    },
    "cold_flu_fever": {
        r"yes|yeah|yep": {
            "response":
            "For fever and flu-like symptoms, I prescribe bed rest, plenty of fluids, and a broth of chicken, garlic, and thyme. A hot toddy of honey, lemon, and a splash of whiskey before bed may also provide relief. If symptoms worsen or persist beyond a few days, please seek further medical attention.",
            "next_state": "initial"
        },
        r"no|nope": {
            "response":
            "Even without a fever, it's important to rest and stay hydrated. Try a tea of elderberry and echinacea to boost your immune system. If symptoms persist or worsen, please consult me again.",
            "next_state": "initial"
        }
    },
    "stomach_details": {
        r"constant": {
            "response":
            "For constant stomach discomfort, I recommend a diet of simple, easily digestible foods. Try a tea of ginger and peppermint to soothe your stomach. If the pain is severe or persists, please seek immediate medical attention.",
            "next_state": "initial"
        },
        r"comes and goes": {
            "response":
            "Intermittent stomach issues could be related to diet or stress. Keep a food diary to identify triggers. In the meantime, try a tincture of gentian root before meals to aid digestion.",
            "next_state": "initial"
        }
    },
    "anxiety_details": {
        r"yes|yeah|yep": {
            "response":
            "Physical symptoms often accompany anxiety. I recommend deep breathing exercises and a tincture of valerian root. Also, consider a daily walk in nature and limiting caffeine intake.",
            "next_state": "initial"
        },
        r"no|nope": {
            "response":
            "Even without physical symptoms, anxiety can be challenging. Try meditation or gentle yoga. A tea of chamomile and lavender before bed may help calm your mind.",
            "next_state": "initial"
        }
    },
    "sleep_duration": {
        r"(\d+)\s*(day|week|month)": {
            "response": lambda duration, unit:
            f"I see you've been having trouble sleeping for {duration} {unit}(s). Establish a calming bedtime routine, avoid screens before bed, and try a warm milk with honey and nutmeg. If the issue persists beyond a fortnight, we may need to explore other remedies.",
            "next_state": "initial"
        }
    },
    "pain_location": {
        r"(head|arm|leg|back|chest)": {
            "response": lambda location:
            f"I understand you're experiencing pain in your {location}. For most aches, I prescribe a warm compress of herbs (rosemary, thyme, and sage) and gentle stretching. If the pain is in your chest, please seek immediate medical attention as it could be serious.",
            "next_state": "initial"
        }
    },
    "file_upload": {
        r"(.+)": {
            "response": lambda file_path:
            f"File '{file_path}' has been uploaded successfully.",
            "next_state": "initial"
        }
    },
    "mental_health_assessment": {
        r"(depressed|anxious|stressed)": {
            "response":
            "Have these feelings been persistent for more than two weeks?",
            "next_state": "persistent_feelings"
        },
        r"(okay|fine|not sure)": {
            "response":
            "It sounds like things may be manageable, but keep monitoring. Are you experiencing any trouble sleeping or anxiety?",
            "next_state": "initial"
        }
    },
    "persistent_feelings": {
        r"yes|yeah": {
            "response":
            "It may help to consult a General Practitioner (GP) or a counselor. Would you like me to guide you to some self-help resources in the meantime?",
            "next_state": "initial"
        },
        r"no|not really": {
            "response":
            "If things change or become overwhelming, don't hesitate to seek support from a professional or reach out to a friend.",
            "next_state": "initial"
        }
    }
}


# Helper function to find best match
def find_best_match(user_input, state):
    user_input = user_input.lower()
    for pattern, response in responses[state].items():
        match = re.search(pattern, user_input)
        if match:
            return response, match
    return None, None


# Handler for Vercel serverless function
class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Read the request data
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        # Get user input and session ID from the request
        user_input = data.get('input', '')
        session_id = data.get('session_id')

        # Handle conversation logic
        if not session_id or session_id not in conversations:
            session_id = str(uuid.uuid4())
            conversations[session_id] = Conversation()

        conversation = conversations[session_id]
        response_data, match = find_best_match(user_input, conversation.state)

        # Create the response
        if response_data:
            if isinstance(response_data, str):
                response = response_data
                conversation.state = "initial"
            else:
                if callable(response_data["response"]):
                    response = response_data["response"](*match.groups())
                else:
                    response = response_data["response"]
                conversation.state = response_data.get("next_state", "initial")
        else:
            response = "I'm not quite sure how to help with that specific issue. As a general recommendation, I suggest a tincture of lavender and a fortnight's rest. If your symptoms persist or worsen, please seek further medical attention."
            conversation.state = "initial"

        # Send JSON response back
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(
            json.dumps({
                'response': response,
                'session_id': session_id
            }).encode())
