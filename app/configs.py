
configs = {
    'system_prompt_code_reviewer': """
    You are an expert code reviewer. Provide constructive feedback on code snippets. Focus on code quality, best practices, potential bugs, and improvements. Be concise but helpful.
""", 
    'llm_model': "gpt-3.5-turbo", 
    'prompt_review_code': """Please review this {language} code snippet{lines_info}:

```{language}
{code}
```

Where you identify that the provided code is not written in a programming language, you should return "Not Code" for the summary, suggestions and rating fields.
Provide your review in the following JSON format. return no other text and only the JSON. :
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

Rating should be 1-10 where 10 is excellent code.""",

    'max_retries': 3,
    'code_review_expected_schema': {
        "summary": "string",
        "suggestions": "string",
        "rating": "numeric"
    }

}