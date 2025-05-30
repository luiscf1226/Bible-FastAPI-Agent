"""
Bible Character Agent Prompt Templates

This module contains the prompt templates used by the Bible Character Agent
to generate responses about biblical characters.
"""

from typing import Dict

# Chain 1: Character Information Extraction Template
CHARACTER_INFO_TEMPLATE: str = """
Proporciona información concisa sobre {character_name} en este formato exacto:

Biographical Information:
- Época y lugar: [una línea]
- Antecedentes familiares: [una línea]
- Ocupación principal: [una línea]

Key Events:
1. [evento principal 1]
2. [evento principal 2]
3. [evento principal 3]

Character Traits:
- Rasgos principales: [lista corta]
- Fortalezas: [lista corta]
- Debilidades: [lista corta]
- Relación con Dios: [una línea]

Legacy:
- Influencia histórica: [una línea]
- Lecciones principales: [lista corta]
- Importancia bíblica: [una línea]

Bible Verses:
1. [referencia 1]
2. [referencia 2]
3. [referencia 3]
"""

# Chain 2: Response Generation Template
RESPONSE_TEMPLATE: str = """
Responde como {character_name} al mensaje del usuario. Sé conciso y directo.

Contexto:
{character_context}

Conversación:
{conversation_history}

Mensaje: {user_message}

Responde en español, siendo conciso pero informativo.
"""

def get_character_prompt(character_name: str) -> str:
    """
    Get the formatted character information prompt for a specific biblical character.
    
    Args:
        character_name (str): The name of the biblical character
        
    Returns:
        str: The formatted prompt with the character's name
    """
    return CHARACTER_INFO_TEMPLATE.format(character_name=character_name)

def get_response_prompt(
    character_name: str,
    character_context: Dict,
    conversation_history: str,
    user_message: str
) -> str:
    """
    Get the formatted response prompt for a specific biblical character.
    
    Args:
        character_name (str): The name of the biblical character
        character_context (Dict): The pre-extracted character information
        conversation_history (str): The formatted conversation history
        user_message (str): The current user message
        
    Returns:
        str: The formatted response prompt
    """
    # Format character context into a readable string
    context_str = "\n".join([
        f"{key}: {value}" for key, value in character_context.items()
    ])
    
    return RESPONSE_TEMPLATE.format(
        character_name=character_name,
        character_context=context_str,
        conversation_history=conversation_history,
        user_message=user_message
    ) 