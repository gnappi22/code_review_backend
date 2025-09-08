

from app.llm_service import LLMService
from app.configs import configs
from app.database import CodeSnippet, SQLHandler

class CodeReviewService:
    def __init__(self):
        self.llm_client = LLMService()
        self.sql = SQLHandler()
        self.init_configs()

    def init_configs(self):
        """this in later versions would be pulled from db for user interaction, this way admins can update prompts and models via a frontend"""
        self.configs = configs

    def build_prompt(self, prompt_template, para):
        """Build the prompt for the LLM, generic enough to be used for other purposes"""
        return prompt_template.format(**para)

    async def review_code(self, language: str, code: str, lines: str = None) -> dict:
        """
        Review code using the LLM service
        """
        # retrieve + build prompts
        system_prompt = self.configs['system_prompt_code_reviewer']
        # this will be used for prompt+for writing to sql
        code_review_para = {
            "language": language,
            "code": code,
            "lines": lines,
            "lines_info": f" (lines {lines})" if lines else ""
        }
        prompt_review_code = self.build_prompt(self.configs['prompt_review_code'], code_review_para)
        print(f"[DEBUG] Generated Prompt: {prompt_review_code}")

        response = await self.llm_client.run_llm_workflow(
            prompt=prompt_review_code, 
            system_prompt=system_prompt,
            expected_schema=self.configs['code_review_expected_schema']
        )
        print(f"[DEBUG] LLM Response: {response}")
        # take everything from code_review_para apart from lines_info and create another dict
        sql_para = {k: v for k, v in code_review_para.items() if k != "lines_info"}

        # add LLM response to sql_para
        sql_para.update(
            {
                "review_summary": response.get("summary"),
                "review_suggestions": response.get("suggestions"),
                "review_rating": response.get("rating")
            }
        )

        print(f"[DEBUG] Writing to SQL with parameters: {sql_para}")
        db_record = self.sql.add_record_to_table(CodeSnippet, sql_para)
        return db_record
