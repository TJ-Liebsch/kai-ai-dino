from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union
from app.services.schemas import ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse, SyllabusRequest, SyllabusResponse
from app.utils.auth import key_check
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ErrorResponse
from app.api.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/submit-tool", response_model=Union[ToolResponse, ErrorResponse])
async def submit_tool( data: ToolRequest, _ = Depends(key_check)):     
    try: 
        # Unpack GenericRequest for tool data
        request_data = data.tool_data
        
        requested_tool = load_tool_metadata(request_data.tool_id)
        
        request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])

        result = execute_tool(request_data.tool_id, request_inputs_dict)
        
        return ToolResponse(data=result)
    
    except InputValidationError as e:
        logger.error(f"InputValidationError: {e}")

        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(ErrorResponse(status=400, message=e.message))
        )
    
    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(ErrorResponse(status=e.status_code, message=e.detail))
        )

@router.post("/chat", response_model=ChatResponse)
async def chat( request: ChatRequest, _ = Depends(key_check) ):
    from app.features.Kaichat.core import executor as kaichat_executor
    
    user_name = request.user.fullName
    chat_messages = request.messages
    user_query = chat_messages[-1].payload.text
    
    response = kaichat_executor(user_name=user_name, user_query=user_query, messages=chat_messages)
    
    formatted_response = Message(
        role="ai",
        type="text",
        payload={"text": response}
    )
    
    return ChatResponse(data=[formatted_response])

@router.post("/generate-syllabus", response_model= SyllabusResponse)
async def generate_syllabus( request: SyllabusRequest, _ = Depends(key_check)):
    from app.features.syllabus_generator.core import executor as syllabus_executor
    
    response = []

    for item in request.inputs:
        grade_level = item.grade_level
        subject = item.subject
        additional_customizations = item.additional_customizations

    if grade_level and subject and additional_customizations:
        logger.debug(f"Gathered the inputs")

    response_data = syllabus_executor(
            grade_level=grade_level, 
            subject=subject, 
            additional_customizations=additional_customizations
        )

    if response_data:
        response.append(response_data)
    else:
        logger.error(f"Response data is empty")

    return SyllabusResponse(data= response)