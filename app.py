# app.py
from flask import Flask, render_template, request, jsonify, flash
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), 
)

# Configuration constants
ENVIRONMENTS = ['Arctic', 'Desert', 'Forest', 'Plains', 'Jungle', 'Mountain', 'Swamp', 'Cavern', 'Underwater', 'Urban']
SIZES = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Enormous']
ENEMY_TYPES = ['Humanoid', 'Beast', 'Demonic', 'Construct', 'Elemental', 'Fey', 'Phantasmal', 'Eldritch', 'Corrupted', 'Ethereal']

@app.route('/', methods=['GET'])
def index():
    """Render the main form page"""
    return render_template('index.html',
                         environments=ENVIRONMENTS,
                         sizes=SIZES,
                         enemy_types=ENEMY_TYPES)

@app.route('/generate', methods=['POST'])
def generate_encounter():
    """Handle form submission and generate monster encounter."""
    try:
        # Get form data
        num_enemies = int(request.form.get('num_enemies', 1))
        difficulty = int(request.form.get('difficulty', 1))
        environment = request.form.get('environment')
        size = request.form.get('size')
        enemy_type = request.form.get('enemy_type')
        additional_details = request.form.get('additional_details', '')

        # Validate inputs
        if not (1 <= num_enemies <= 5 and 1 <= difficulty <= 5):
            flash('Invalid number of enemies or difficulty rating')
            return render_template('index.html',
                                   environments=ENVIRONMENTS,
                                   sizes=SIZES,
                                   enemy_types=ENEMY_TYPES)

        # Construct prompt for OpenAI
        prompt = f"""Generate a TTRPG monster encounter with the following specifications:
        - Number of enemies: {num_enemies}
        - Challenge rating: {difficulty}
        - Environment: {environment}
        - Size: {size}
        - Enemy Type: {enemy_type}
        - Additional Details: {additional_details}

        For each monster, include:
        1. Detailed physical description reflecting the {environment} environment
        2. Complete stat block with HP, AC, attacks, and abilities
        3. Special abilities influenced by {enemy_type} type
        4. Combat tactics and behavior patterns
        5. Appropriate loot for challenge rating {difficulty}

        Format the response as a JSON object with a "monsters" key containing a list of monsters. For each monster, include:
        1. "description": A detailed physical description reflecting the {environment} environment.
        2. "stats": A dictionary with:
        - "HP": Hit Points
        - "AC": Armor Class
        - "Attacks": A list of attacks, each with name, damage, and range
        - "Saving Throws": Saving throw modifiers
        - "Skills": Skill modifiers
        - "Speed": Movement speed
        - "Initiative": Initiative bonus
        3. "abilities": A list of special abilities and their effects.
        4. "tactics": A summary of combat tactics and behavior patterns.
        5. "loot": A list of loot items or rewards, each with a brief description.

        Ensure the "monsters" key contains exactly {num_enemies} monsters. Each monster should reflect its type ({enemy_type}) and environment ({environment}) in its stats, abilities, and tactics.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",  # Update to the desired model
            messages=[
                {"role": "system", "content": "You are a TTRPG game master expert at creating balanced and interesting monster encounters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Correctly extract the content
        encounter_data = json.loads(response.choices[0].message.content)

        # Generate images for each monster
        for monster in encounter_data['monsters']:
            image_prompt = f"Fantasy-style illustration of {monster['description']}."
            try:
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                # Add the image URL to the monster data
                monster['image_url'] = image_response.data[0].url
            except Exception as e:
                monster['image_url'] = None  # Handle errors gracefully

        response = client.images.generate(
                    model="dall-e-3",
                    prompt="a white siamese cat",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
        
        print(encounter_data)
        return render_template('encounter.html', encounter=encounter_data)

    except Exception as e:
        flash(f'Error generating encounter: {str(e)}')
        return render_template('index.html',
                               environments=ENVIRONMENTS,
                               sizes=SIZES,
                               enemy_types=ENEMY_TYPES)


if __name__ == '__main__':
    app.run(debug=True)




