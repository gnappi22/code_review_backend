import openai
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

class LLMService:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"


    async def generate_llm_response(self, prompt: str) -> str:        
        """
        Generate a response from the LLM given a prompt
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides code reviews. Focus on code quality, best practices, potential bugs, and improvements."
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
    
    async def review_code(self, language: str, code: str, lines: str = None) -> Dict[str, Any]:
        """
        Generate a code review using OpenAI's API
        """
        prompt = self._build_prompt(language, code, lines)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Provide constructive feedback on code snippets. Focus on code quality, best practices, potential bugs, and improvements. Be concise but helpful."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            review_text = response.choices[0].message.content
            return self._parse_review(review_text)
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return {
                "summary": "Unable to generate review due to API error.",
                "suggestions": ["Please check your OpenAI API key and try again."],
                "rating": 0.0
            }
    
    def _build_prompt(self, language: str, code: str, lines: str = None) -> str:
        """Build the prompt for the LLM"""
        lines_info = f" (lines {lines})" if lines else ""
        
        prompt = f"""Please review this {language} code snippet{lines_info}:

```{language}
{code}
```

Provide your review in the following JSON format:
{{
    "summary": "Brief summary of the code quality and main issues",
    "suggestions": ["List of specific improvement suggestions"],
    "rating": 8.5
}}

Focus on:
- Code quality and readability
- Best practices for {language}
- Potential bugs or issues
- Performance considerations
- Maintainability

Rating should be 1-10 where 10 is excellent code."""
        
        return prompt
    
    def _parse_review(self, review_text: str) -> Dict[str, Any]:
        """Parse the LLM response and extract structured review"""
        try:
            # Try to extract JSON from the response
            start_idx = review_text.find('{')
            end_idx = review_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = review_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate the structure
                if all(key in parsed for key in ['summary', 'suggestions', 'rating']):
                    return {
                        "summary": parsed['summary'],
                        "suggestions": parsed['suggestions'],
                        "rating": float(parsed['rating'])
                    }
            
            # Fallback: create a structured response from the text
            return self._fallback_parse(review_text)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            return self._fallback_parse(review_text)
    
    def _fallback_parse(self, review_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        lines = review_text.strip().split('\n')
        summary = lines[0] if lines else "Code review completed"
        
        # Extract suggestions (look for bullet points or numbered lists)
        suggestions = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith(('-', '*', '•', '1.', '2.', '3.')):
                suggestions.append(line.lstrip('-*•123456789. '))
        
        if not suggestions:
            suggestions = ["Review the code for potential improvements"]
        
        return {
            "summary": summary,
            "suggestions": suggestions[:5],  # Limit to 5 suggestions
            "rating": 7.0  # Default rating
        }


if __name__ == '__main__':
    import asyncio
    llm_service = LLMService()
    print(llm_service.client)
    print(llm_service._build_prompt("Python", "def foo():\n    return 'bar'", "1-2"))
