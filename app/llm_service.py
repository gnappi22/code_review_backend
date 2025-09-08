import openai
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv


class LLMService:
    '''Service to interact with the LLM (OpenAI). all code review functionality sits outside this class in the service specific function'''
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"


    async def run_llm_workflow(self, prompt: str, system_prompt: str, expected_schema: dict, max_retry: int = 3) -> str:
        """
        Calls generate_llm_response and ensures the output is valid JSON.
        Retries up to max_retry times if the output is not valid JSON.
        """
        for attempt in range(max_retry):
            response = await self.generate_llm_response(prompt, system_prompt)
            try:
                print(f"[DEBUG] LLM Response Attempt {attempt + 1}: {response}")
                parsed_response = self._parse_response(response, expected_schema)
                return parsed_response
            except json.JSONDecodeError:
                print(f"[WARNING] Attempt {attempt + 1} failed to parse JSON. Retrying...")
                if attempt == max_retry - 1:
                    print(f"[ERROR] All attempts failed. Returning raw response.")
                    return response
        return response

    async def generate_llm_response(self, prompt: str, system_prompt: str) -> str:        
        """
        Generate a response from the LLM given a prompt
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Error generating response from LLM."

    def _parse_response(self, llm_response: str, expected_schema: dict) -> Dict[str, Any]:
        """Parse the LLM response and extract structured review. Raises if parsing fails."""
        start_idx = llm_response.find('{')
        end_idx = llm_response.rfind('}') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = llm_response[start_idx:end_idx]
            parsed = json.loads(json_str)

            # Validate the structure
            if all(key in parsed for key in expected_schema):
                result = {}
                for key, typ in expected_schema.items():
                    if typ == "numeric":
                        result[key] = float(parsed[key])
                    elif typ == "string":
                        result[key] = str(parsed[key])
                    else:
                        result[key] = parsed[key]
                return result
        # If parsing fails, raise an error so the caller can retry
        raise json.JSONDecodeError("Could not parse review as valid JSON.", llm_response, 0)


if __name__ == '__main__':
    import asyncio
    llm_service = LLMService()

    # Quick test for run_llm_workflow
    async def test_llm_workflow():
        prompt = (
            "Please review this Python code snippet:\n"
            "```python\ndef foo():\n    return 'bar'\n```\n"
            "Provide your review in the following JSON format:\n"
            "{\n"
            '    "summary": "Brief summary",\n'
            '    "suggestions": ["Improve naming"],\n'
            '    "rating": 8.5\n'
            "}"
        )
        system_prompt = "You are an expert code reviewer. Respond in the specified JSON format."
        expected_schema = {
            "summary": "string",
            "suggestions": "string",  # Accepts list, but will be cast to string for test
            "rating": "numeric"
        }
        result = await llm_service.run_llm_workflow(prompt, system_prompt, expected_schema)
        print("LLM Workflow Test Result:", result)

    asyncio.run(test_llm_workflow())

