from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from fastapi import HTTPException
from typing import Optional
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../')))
from app.services.logger import setup_logger


logger = setup_logger(__name__)
model = GoogleGenerativeAI(model="gemini-1.0-pro")


def read_text_file(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
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

    model_config = {
        "json_schema_extra": {
            "examples": """
                {
                  "grade_level": "University",
                  "subject": "Introduction to Machine Learning",
                  "course_description": "This syllabus covers the basics of machine learning, including algorithms and applications.",
                  "course_objectives": "Understand key concepts in machine learning, such as supervised and unsupervised learning.",
                  "required_materials": "Textbook: Machine Learning by Tom Mitchell, Notebook, Python environment",
                  "grading_policy": "Homework: 40%, Midterm: 30%, Final Exam: 30%",
                  "class_policies": "Attendance required, no late submissions",
                  "course_outline": "Week 1: Introduction, Week 2: Supervised Learning, ...",
                  "additional_customizations": "Guest lectures, field trips"
                }
            """
        }
    }


def generate_syllabus(grade_level, subject, additional_params):
    
    try:
        template = read_text_file("prompt/syllabus-prompt.txt")
        parser = JsonOutputParser(pydantic_object=Syllabus)
        prompt = PromptTemplate(
            template= template,
            input_variables=["grade_level", "subject", "additional_params"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        ) 
        
        chain= prompt | model | parser
        response = chain.invoke({
                   "grade_level": grade_level,
                  "subject": subject,
                 "additional_params": additional_params
                })

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate syllabus from LLM")
    
    return response

