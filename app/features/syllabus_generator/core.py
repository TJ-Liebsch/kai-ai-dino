from typing import Any, Dict, Optional
from services.logger import setup_logger

# Initialize logger
logger = setup_logger()

def executor(
    grade_level: str,
    topic: str,
    context: Optional[Dict[str, Any]] = None,
    additional_params: Optional[Dict[str, Any]] = None
) -> str:
   
    try:
        logger.info("Starting execution with parameters: %s", {
            'grade_level': grade_level,
            'topic': topic,
            'context': context,
            'additional_params': additional_params
        })

        # Initialize default values for context and additional_params if not provided
        if context is None:
            context = {}
        if additional_params is None:
            additional_params = {}

       
        prompt_template = create_prompt_template(grade_level, topic, context, additional_params)

      
        processed_result = process_template(prompt_template, context)

      
        final_result = invoke_processing_chain(processed_result)

        logger.info("Execution completed successfully. Result: %s", final_result)
        return final_result

    except Exception as e:
        logger.error("An error occurred during execution: %s", str(e))
        return f"Error: {str(e)}"