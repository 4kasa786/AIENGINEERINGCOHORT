from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

messages_example = [
    {
        "role":"system",
        "content":""" 
         You are a Time and Space Complexity Analysis Assistant.

         Your job:
         - Analyze the time complexity and space complexity of code or algorithms.
         - Explain the reasoning in simple terms.
         - Use Big-O notation clearly.
         - If there are loops, recursion, sorting, hashing, or extra data structures, mention their impact.

         Guardrails:
         - Do not write a full solution unless explicitly asked.
         - Do not optimize the algorithm unless the user asks for optimization.
         - Do not explain unrelated DSA concepts.
         - If the input code is incomplete, say what assumption you are making.
         - Keep the answer begineer-friendly and consise.

         Output Format:
         1. Time Complexity:
         2. Space Complexity:
         3. Explanation:
        """
    },
    {
        "role":"user",
        "content":"""
        What is the time and space complexity of this code?

        def find_sum(arr):
            total = 0
            for num in arr:
                total+=num
            
            return total
        """
    },
    {
        "role":"assistant",
        "content":"""
         1. Time Complexity: O(n)
         2. Space Complexity: O(1)
         3. Explanation: The time complexity is O(n) because the function iterates through the array once. The space complexity is O(1) because no extra space is used beyond the variable total.
        """
    },
    {
        # This dictionary contains an actual question from the user to the llm.
        "role":"user",
        "content":"""
        what is the time and space complexity of this code?

        def binary_search(arr,target):
            left,right = 0,len(arr)-1
            while left<=right:
                mid = (left+right)//2
                if arr[mid]==target:
                    return mid
                else if arr[mid]<target:
                    left = mid+1
                else:
                    right = mid-1
            return -1
        """
       
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages = messages_example,
)

print(response)