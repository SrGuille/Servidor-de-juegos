import random
from servidor.classes import Actor
from typing import List
from openai import OpenAI
from . import secret
client = OpenAI(
    api_key = secret.api_key
)

SYSTEM_PROMPT = """Quiero que me ayudes a generar una frase absurda y graciosa de entre 7 y 9 palabras. 
Te diré requisitos específicos, por ejemplo que aparezcan unos protagonistas, a veces con 
características sobre ellos para que puedas hablar sobre ello en la frase, o que se repita una cierta letra más de lo habitual para que sea más absurdo. 
No utilices palabras poco frecuentes, debe poder entenderlas cualquier persona. Intenta que la palabra que representa la característica no aparezca literalmente 
en la frase si no es necesario, solo representa la idea. Si hay más de un protagonista intenta que la frase sea una interacción entre ellos."""

REPEATED_LETTERS = ['z', 'f', 'q', 'j', 'ñ', 'x']

def generate_prompt(actors: List[Actor], repeated_letter: str):
    """
        Generate a prompt that can have 1 or 2 actors (with their characteristics) and can have a repeated letter
    """
    actor1 = actors[0]
    prompt = 'Los parámetros para esta frase son:'
    prompt += f'Protagonista 1: {actor1.name}, Característica: {actor1.attribute}'
    if len(actors) == 2:
        actor2 = actors[1]
        prompt += f', Protagonista 2: {actor2.name}, Característica: {actor2.attribute}'
    if repeated_letter is not None:
        prompt += f', Letra repetida: {repeated_letter}'
        
    print(prompt)
    return prompt

def generate_sentence(prompt: str):
    """
        Call GPT-4 to generate a phrase with the given prompt
    """
    sentence = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4",
    )
    print(sentence)
    return sentence.choices[0].message.content.replace('"', '').replace('.', '') # Remove the quotes and the final dot

if __name__ == '__main__':
    repeated_letter = random.choice(REPEATED_LETTERS)
    prompt = generate_prompt('Guille', 'guitarra', 'Carmen', 'dibujante', repeated_letter)
    phrase = generate_sentence(prompt)
    print(phrase)
