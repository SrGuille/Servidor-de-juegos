import os
import os
import sys

from pyparsing import List
# Añadir el directorio 'servidor' al path para ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from games.palabrazo.use_openai_api import generate_sentence
from classes import PalabrazoActor

def generate_input_data(actors: List[PalabrazoActor]):
    """
        Generate the input data for the prompt that can have 1 or 2 actors (with their characteristics) and can have a repeated letter
    """
    actor1 = actors[0]
    input_data = '\n\nLos parámetros para esta frase son:'
    if len(actors) == 1:
        input_data += f'\n-{actor1.name}: {", ".join(actor1.attributes)}.'
    else:
        actor2 = actors[1]
        input_data += f'\n-{actor1.name}: {actor1.attributes[0]}.'
        input_data += f'\n-{actor2.name}: {actor2.attributes[0]}.'
    print(input_data)
    return input_data

if __name__ == "__main__":
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    prompt_1_actor_path = os.path.join(prompts_dir, 'prompt_1_actor.md')
    prompt_2_actors_path = os.path.join(prompts_dir, 'prompt_2_actors.md')
    with open(prompt_1_actor_path, encoding='utf-8') as f:
        PROMPT_1_ACTOR = f.read()
    with open(prompt_2_actors_path, encoding='utf-8') as f:
        PROMPT_2_ACTORS = f.read()

    """
    actors = [PalabrazoActor('Rafa', ['Se dedica a los seguros', 'Pinta en la pared de su salón']),
              PalabrazoActor('Nayla', ['Tiene muchos trabajos', 'Siempre regala cosas hechas a mano'])]
    input_data = generate_input_data(actors)
    print(generate_sentence(PROMPT_2_ACTORS, input_data))
    """

    """
    actors = [PalabrazoActor('Rafa', ['Se dedica a los seguros', 'Pinta en la pared de su salón'])]
    input_data = generate_input_data(actors)
    print(generate_sentence(PROMPT_1_ACTOR, input_data))

    actors = [PalabrazoActor('Nayla', ['Tiene muchos trabajos', 'Siempre regala cosas hechas a mano'])]
    input_data = generate_input_data(actors)
    print(generate_sentence(PROMPT_1_ACTOR, input_data))
    """

    actors = [PalabrazoActor('Stef', ['Le gusta Inazuma Eleven', 'Es búlgara'])]
    input_data = generate_input_data(actors)
    print(generate_sentence(PROMPT_1_ACTOR, input_data))
  