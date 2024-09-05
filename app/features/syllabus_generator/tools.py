from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../')))

from app.services.logger import setup_logger

logger = setup_logger(__name__)
model = GoogleGenerativeAI(model="gemini-1.0-pro")


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()
class Syllabus(BaseModel):
    grade_level: str = Field(description="The grade level of the course (K-12 or university)")
    subject: str = Field(description="The subject of the course")
    course_description: str = Field(description="A description of the course")
    course_objectives: str = Field(description="Objectives of the course")
    required_materials: str = Field(description="Materials required for the course")
    grading_policy: str = Field(description="Grading policy for the course")
    class_policies: str = Field(description="Class policies and exceptions")
    course_outline: str = Field(description="Weekly course outline")
    additional_customizations: Optional[str] = Field(description="Any additional customizations for the syllabus")

def generate_syllabus(grade_level, subject, additional_customizations):
    try:
        input_data = {
            "grade_level": grade_level,
            "subject": subject,
            "additional_customizations": additional_customizations
        }

        try:
            json.dumps(input_data)
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid JSON data: {e}")

        template = read_text_file("prompt/syllabus-prompt.txt")
        logger.debug(f"Template: {template}")
        parser = JsonOutputParser(pydantic_object=Syllabus)
        prompt = PromptTemplate(
            template= template,
            input_variables=["grade_level", "subject", "additional_customizations"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        logger.debug(f"Prompt: {prompt}")
        chain= prompt | model | parser
        logger.debug(f"Chain: {chain}")
        response = chain.invoke(input_data)
        logger.debug(f"Response: {response}")
    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate syllabus from LLM")
    return response
