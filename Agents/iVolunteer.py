import random
from datetime import datetime
from uuid import uuid4

from openai import OpenAI
from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Message models
class DoctorRequest(Model):
    category: str

class DoctorResponse(Model):
    available: bool
    message: str

class VolunteerRegistry(Model):
    data: dict

# Constants
DOCTOR_SEED = "doctor_seed"

# Agent
doctor = Agent(name="FindAPatient", port=8000, seed=DOCTOR_SEED, endpoint=["http://127.0.0.1:8000/submit"])

# ASI-1 client
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key='sk_47dbfae6905943759c8f952266ca2d78120fddfd56d34eb893582d87c4836df1',
)

# Chat protocol
chat_proto = Protocol(name="chat", spec=chat_protocol_spec)

@doctor.on_event("startup")
async def start(ctx: Context):
    ctx.storage.set("patient_found", False)
    ctx.storage.set("contacted_patients", [])
    ctx.storage.set("category", "")
    ctx.storage.set("chat_sender", None)
    ctx.storage.set("authenticated", False)

@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))

    user_input = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            user_input += item.text.strip()

    authenticated = ctx.storage.get("authenticated") or False

    if not authenticated:
        if "fetch" in user_input.lower():
            ctx.storage.set("authenticated", True)
            await ctx.send(sender, ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[TextContent(type="text", text="Password accepted. How can I help you?")]
            ))
        else:
            await ctx.send(sender, ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[TextContent(type="text", text="Please provide the password to proceed.")]
            ))
        return

    # Load registry and send to ASI-1 model
    registry = ctx.storage.get("volunteer_registry") or {}

    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical assistant AI.\n"
                        "You are given a dictionary of patient records grouped by agent addresses.\n"
                        "Each person has fields like category, gender, age, contact.\n"
                        "Given a user query like 'find patients under 30 years old', "
                        "analyze the patient records and respond with matching patients in natural language.\n"
                        f"Here is the patient data:\n{registry}"
                    )
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
        )

        answer = r.choices[0].message.content.strip()

    except Exception as e:
        ctx.logger.exception(f"Error querying ASI-1: {e}")
        answer = "There was an error processing your request."

    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=answer)],
    ))

@doctor.on_interval(period=5)
async def send_offer(ctx: Context):
    if ctx.storage.get("patient_found") or not ctx.storage.get("category"):
        return

    contacted = ctx.storage.get("contacted_patients")
    uncontacted = []  # Placeholder for future logic

    if not uncontacted:
        ctx.logger.info("No uncontacted patients remaining.")
        return

    random_address = random.choice(uncontacted)
    category = ctx.storage.get("category")
    await ctx.send(random_address, DoctorRequest(category=category))
    contacted.append(random_address)
    ctx.storage.set("contacted_patients", contacted)

@doctor.on_message(model=DoctorResponse)
async def response_handler(ctx, sender: str, msg: DoctorResponse):
    status = "Accepted" if msg.available else "Declined"
    ctx.logger.info(f"agent {sender} : {status}")

    if msg.available:
        ctx.storage.set("patient_found", True)
        contacted = ctx.storage.get("contacted_patients")
        chat_user = ctx.storage.get("chat_sender")
        if chat_user:
            await ctx.send(chat_user, ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[
                    TextContent(type="text", text=f"{msg.message}\nTotal patients contacted: {len(contacted)}"),
                    EndSessionContent(type="end-session"),
                ]
            ))

@doctor.on_message(model=VolunteerRegistry)
async def handle_registry(ctx: Context, sender: str, msg: VolunteerRegistry):
    ctx.logger.info(f"Received volunteer registry from {sender}")
    ctx.storage.set("volunteer_registry", msg.data)

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    # Optional: Reset authentication when a session ends
    ctx.storage.set("authenticated", False)

doctor.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    doctor.run()