import json
import os
from openai import OpenAI
from yahoo_finance_demo import get_stock_price
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

TOOL_DEFINITION = [
    {
        "type":"function",
        "function":{
            "name":"get_stock_price",
            "description":"Get the current price of a stock given its ticker symbol",
            "parameters":{
                "type":"object",
                "properties":{
                    "ticke_symbol":{
                        "type":"string",
                        "description":"The ticker symbol of the stock to get the price of e.g. AAPL,TSLA, etc"
                    }
                },
                "required":["ticker_symbol"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are a helpful stock market assistant. When the user asked about a stock price,
think step by step about what you need to do, then call the get_stock_price tool with 
the correct ticker symbol. After receiving the result, present the information in a clear,
and friendly manner.

IMPORTANT: Always call the get_stock_price tool with the correct ticker symbol.Dont pickup the price
from our old conversations as the price keeps on changing. Dont assume the price from previous conversations.
Always whenever a price for a stock is asked, we need to call the relevant tools again.

Always reason out loud before acting so the user can follow your chain of thought.
"""

FEW_SHOT_EXAMPLES = [
    # Example 1: Single stock lookup
    {
        "role": "user",
        "content": "How much is Apple stock right now?"
    },
    {
        "role": "assistant",
        "content": (
            "The user is asking about Apples stock price.Apples ticker symbol is AAPL "
            "Let me fetch the current price of Apple stock."
        ),
        "tool_calls": [
            {
                "id": "tool_call_01",
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "arguments": json.dumps({
                        "ticker_symbol": "AAPL"
                    })
                }
            }
        ]
    },
    {
        "role": "tool",
        "tool_call_id": "tool_call_01",
        "content": json.dumps({
            "ticker": "AAPL",
            "price": 200.3,
            "currency": "USD"
        })
    },
    {
        "role": "assistant",
        "content": (
            "Apple (AAPL) is currently trading at $200.30 per share in USD "
            "Keep in mind this is the last traded price and may shift slightly but the time you check again."
        )
    },
    # Example 2: Multi stock comparison
    {
        "role": "user",
        "content": "Compare the stock prices of Google and Microsoft"
    },
    {
        "role": "assistant",
        "content": (
            "The user wants to compare two stocks. Googles parent company "
            "Alphabet trades under the ticker symbol GOOGL, and Microsoft trades "
            "under the ticker symbol MSFT "
            "Let me fetch the current prices of both stocks."
        ),
        "tool_calls": [
            {
                "id": "tool_call_02",
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "arguments": json.dumps({
                        "ticker_symbol": "GOOGL"
                    })
                }
            },
            {
                "id": "tool_call_03",
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "arguments": json.dumps({
                        "ticker_symbol": "MSFT"
                    })
                }
            }
        ]
    },
    {
        "role": "tool",
        "tool_call_id": "tool_call_02",
        "content": json.dumps({"ticker": "GOOGL", "price": 280.12, "currency": "USD"}),
    },
    {
        "role": "tool",
        "tool_call_id": "tool_call_03",
        "content": json.dumps({"ticker": "MSFT", "price": 235.77, "currency": "USD"}),
    },
    {
        "role": "assistant",
        "content": (
            "Here is the comparison:\n\n"
            "- Alphabet / Google (GOOGL) is trading at $280.12 per share in USD.\n"
            "- Microsoft (MSFT) is trading at $235.77 per share in USD.\n\n"
            "Microsoft stock is currently cheaper that Googles."
        )
    }
]

AVAILABLE_TOOLS = {
    "get_stock_price": get_stock_price
}

def run_agent(user_query: str)-> None:
    """Single turn agentic loop with chain of thought reasoning""" 
    
    messages = [
        {
            "role":"system",
            "content":SYSTEM_PROMPT
        },
        *FEW_SHOT_EXAMPLES,
        {"role":"user","content":user_query},
    ]

    print(f"\n{'='*60}")
    print(f"User: {user_query}")
    print(f"{'='*60}\n")

    while True:
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            tools = TOOL_DEFINITION
        )

        choice = response.choices[0]
        assistant_msg = choice.message

        messages.append(assistant_msg)

        print(f"Assistant(Message): {assistant_msg}")

        if assistant_msg.content:
            print(f"Assistant (thinking): {assistant_msg.content}\n")

        if choice.finish_reason == "stop":
            break
    
        if not assistant_msg.tool_calls:
            break 

        for tool_call in assistant_msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            print(f" [Tool Call] {fn_name}\n")
            print(f" [Tool Call] {fn_args}")


            fn = AVAILABLE_TOOLS[fn_name]
            result = fn(**fn_args)

            print(f" [Tool Result] {result}\n")

            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":result
            })


def main():
    print("Stock price agent (type 'quit' to exit)")
    print("-"*45)

    while True:
        query = input("\nYou: ").strip()
        if not query:
            continue
    
        if(query.lower() in ("quit","exit","q")):
            print("Goodbye!")
            break

        run_agent(query)


if __name__ == "__main__":
    main()