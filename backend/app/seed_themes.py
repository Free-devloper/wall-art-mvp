"""Seed the database with default themes for demo/development.

Run with:  python -m app.seed_themes
Or via:    make seed
"""

import asyncio
import uuid
from datetime import datetime, timezone

from app.database import AsyncSessionLocal, engine, Base
from app.models.theme import Theme
from sqlalchemy import select


SEED_THEMES = [
    {
        "name": "Superhero Original",
        "description": "Transform into a unique, original superhero character with a dynamic pose and custom suit design. No copyrighted characters — this is 100% you!",
        "prompt_template": "A portrait of the person as an original superhero character with a unique custom-designed suit, dynamic heroic pose, comic book art style, vibrant colours, city skyline background, dramatic lighting, highly detailed",
        "price_cents": 4999,
        "sort_order": 1,
        "max_regenerations": 3,
    },
    {
        "name": "Fantasy Warrior",
        "description": "Become a legendary fantasy warrior with armour, sword, and an epic magical battlefield behind you.",
        "prompt_template": "A portrait of the person as a fantasy warrior wearing ornate medieval armour, holding a glowing magical sword, standing on a dramatic fantasy battlefield with castles and dragons in the background, epic lighting, painterly style, highly detailed",
        "price_cents": 4999,
        "sort_order": 2,
        "max_regenerations": 3,
    },
    {
        "name": "Space Explorer",
        "description": "Venture into the cosmos as a futuristic astronaut exploring alien worlds with stunning nebulae and planets.",
        "prompt_template": "A portrait of the person as a futuristic space explorer wearing a sleek sci-fi spacesuit, standing on an alien planet surface, beautiful nebula and planets in the sky, cinematic lighting, photorealistic, highly detailed",
        "price_cents": 4999,
        "sort_order": 3,
        "max_regenerations": 3,
    },
    {
        "name": "Pop Art Icon",
        "description": "Get the Andy Warhol treatment — bold colours, halftone dots, and striking pop art style.",
        "prompt_template": "A portrait of the person in bold pop art style, vibrant contrasting colours, halftone dot pattern, thick black outlines, inspired by 1960s pop art movement, striking and eye-catching, gallery quality",
        "price_cents": 3999,
        "sort_order": 4,
        "max_regenerations": 3,
    },
    {
        "name": "Anime Hero",
        "description": "Step into the world of anime as a powerful original character with dramatic action lines and vibrant colours.",
        "prompt_template": "A portrait of the person as an original anime character, Japanese anime art style, dramatic action pose, vibrant colours, speed lines, detailed shading, expressive eyes, anime background with cherry blossoms",
        "price_cents": 3999,
        "sort_order": 5,
        "max_regenerations": 3,
    },
    {
        "name": "Renaissance Portrait",
        "description": "A classical oil painting masterpiece — imagine yourself painted by the great masters of the Renaissance.",
        "prompt_template": "A portrait of the person in the style of a Renaissance oil painting, classical composition, rich warm tones, dramatic chiaroscuro lighting, ornate gilded frame effect, museum-quality fine art, inspired by Rembrandt and Vermeer",
        "price_cents": 5499,
        "sort_order": 6,
        "max_regenerations": 3,
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if themes already exist
        result = await db.execute(select(Theme).limit(1))
        if result.scalar_one_or_none():
            print("Themes already seeded — skipping.")
            return

        for theme_data in SEED_THEMES:
            theme = Theme(
                id=uuid.uuid4(),
                name=theme_data["name"],
                description=theme_data["description"],
                prompt_template=theme_data["prompt_template"],
                price_cents=theme_data["price_cents"],
                sort_order=theme_data["sort_order"],
                max_regenerations=theme_data["max_regenerations"],
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(theme)

        await db.commit()
        print(f"Seeded {len(SEED_THEMES)} themes successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
