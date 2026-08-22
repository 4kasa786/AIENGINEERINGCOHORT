from dataclasses import dataclass
import os
from typing import Optional
from openai import OpenAI
import json
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Provider:
    """One provider to reliably route requests across all inference providers"""
    name:str
    env_var:str
    is_free:bool
    base_url: Optional[str]
    model:str

PROVIDERS = [
   Provider("Groq","GROQ_API_KEY",True,"https://api.groq.com/openai/v1","openai/gpt-oss-120b"),
   Provider("OpenAI","OPENAI_API_KEY",True,None,"gpt-4o-mini"),    
]

def select_provider() -> Provider:
    for provider in PROVIDERS:
        if os.getenv(provider.env_var):
            return provider

    expected = ", ".join(p.env_var for p in PROVIDERS)
    raise RuntimeError(f"No provider key set, add one of {expected} to your environment variables")

def build_client(provider: Provider) -> OpenAI:


    api_key = os.getenv(provider.env_var)
    if provider.base_url is None:
        return OpenAI(api_key=api_key)

    return OpenAI(
        api_key=api_key,
        base_url=provider.base_url
    )


def have_any_key()->bool:
    return any(os.getenv(p.env_var) for p in PROVIDERS)

print("Found a provider key." if have_any_key() else "No provider key found.")    


def llm_reply(prompt:str)->str:
    provider = select_provider()
    print(provider)
    client = build_client(provider)
    result = client.chat.completions.create(
        model = provider.model,
        max_tokens=200,
        messages=[
            {
                "role":"user",
                "content":prompt,
            }
        ]
    )

    return result.choices[0].message.content


class CotStep(BaseModel):
    """
    A step in the COT process
    """
    content:str
    step_type:Literal["THINKING","FINAL_OUTPUT"] #Thinking -> Plan


def parse_cot_step(raw_reply:str) -> CotStep | str:
    """Parse a raw reply into a CotStep"""
    try:
        parsed = json.loads(raw_reply) # returning a python dict
        return CotStep(**parsed) #converting python dict to a CotStep object
    except:
        return f"Invalid JSON:{raw_reply}"

SYSTEM_PROMPT = """
You are an expert assistant that solves user queries one step at a time.

You have two possible step types:

- THINKING: one short reasoning step toward solving the problem.
- FINAL_OUTPUT: the final answer to the user's question.

IMPORTANT RULES:

1. Each API response MUST contain exactly ONE JSON object.
2. NEVER return multiple JSON objects in a single response.
3. NEVER return an array of JSON objects.
4. NEVER return markdown, code fences, or any text outside the JSON object.
5. Return exactly one step per API response.
6. If more reasoning is needed, return a THINKING step.
7. If the answer is ready, return a FINAL_OUTPUT step.
8. The "step_type" value must be exactly either "THINKING" or "FINAL_OUTPUT".
9. The "content" value must be a string.

Use exactly this JSON format:

{
    "content": "your next reasoning step or final answer",
    "step_type": "THINKING"
}

OR, when the answer is ready:

{
    "content": "your final answer",
    "step_type": "FINAL_OUTPUT"
}

Example:

User question:
Roger has 5 tennis balls. He buys 2 cans of tennis balls. Each can contains 3 tennis balls. How many tennis balls does Roger have now?

For the first API response, return only:

{
    "step_type": "THINKING",
    "content": "Roger starts with 5 tennis balls."
}

On the next API call, return only the next step, for example:

{
    "step_type": "THINKING",
    "content": "Two cans contain 2 × 3 = 6 tennis balls."
}

On a later API call, when the answer is ready, return only:

{
    "step_type": "FINAL_OUTPUT",
    "content": "Roger has 11 tennis balls now."
}

Remember: ONE API CALL = ONE JSON OBJECT = ONE STEP.
"""


def llm_json_reply(messages:list[dict])->str:
    provider = select_provider()
    client = build_client(provider)

    kwargs: dict = {
        "model":provider.model,
        "max_tokens":400,
        "messages":messages,
    }

    result = client.chat.completions.create(**kwargs)
    return result.choices[0].message.content

class CotAssistant:
    """
     An Assistant that solves user queries using chain of thought.
    """

    def __init__(self):
        self.messages:list[dict] = [
            {
                "role":"system",
                "content":SYSTEM_PROMPT
            }
        ]
        self.MAX_STEPS = 15

    def run(self,user_query:str)->str:
        self.messages.append({
            "role":"user",
            "content":user_query
        })
        print(f"user_query:{user_query}\n")

        for _ in range(self.MAX_STEPS):
            raw_reply = llm_json_reply(self.messages) # this will make the llm call and return a string of json format

            self.messages.append({  #we append that raw jsonstring into messages list
                "role":"assistant",
                "content":raw_reply
            })

            parsed = parse_cot_step(raw_reply) # convert the raw json string to a CotStep object

            if isinstance(parsed,CotStep): # check if the parsed is a valid CotStep object
                if parsed.step_type == "THINKING":
                    print(f"parsed_content:{parsed.content}\n")
                    continue

                if parsed.step_type == "FINAL_OUTPUT":
                    print(f"pased_content:{parsed.content}\n")
                    return parsed.content

            else:
                print(f"Not Parsed:{parsed}\n")
                return parsed
        

        # we came out of the loop means we were not able to derive the answer in 15 steps

        return f"Failed to derive the answer in {self.MAX_STEPS} steps."

assistant = CotAssistant()

while True:
    user_query = input("Enter the question")
    if user_query.lower() in ["exit","quit","bye"]:
        break
    answer = assistant.run(user_query)
    print(f"Answer:{answer}")
    



