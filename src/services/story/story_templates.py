"""
Beautelligence Video Pipeline - Story Templates

Psychologically-crafted fruit character templates designed with:
- Emotional Intelligence principles
- NLP communication patterns
- Strategic storytelling structure
- Health benefit messaging

Each character is designed to create deep emotional connection
and deliver memorable health messages.
"""

from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class FruitCharacter:
    """A fruit character with personality and health messaging."""
    
    name: str  # Display name (e.g., "Apple")
    key: str   # Identifier (e.g., "apple")
    
    # Visual Design
    color_palette: str
    visual_traits: str  # Unique physical characteristics
    
    # Personality (Psychology-based)
    archetype: str  # Jungian archetype for depth
    personality: str  # Core personality traits
    voice_tone: str  # How they "speak"
    
    # Emotional Connection Strategy
    emotional_hook: str  # The feeling they evoke
    trust_builder: str  # How they build rapport
    
    # Health Message (NLP-structured)
    core_message: str  # The key takeaway
    health_benefits: list[str] = field(default_factory=list)
    call_to_action: str = ""  # What viewer should do
    
    # Story Elements
    intro_gesture: str = ""  # How they greet
    signature_move: str = ""  # Memorable action
    farewell_gesture: str = ""  # How they say goodbye


# =============================================================================
# FRUIT CHARACTER LIBRARY
# Designed with Emotional Intelligence + NLP + Psychology principles
# =============================================================================

FRUIT_CHARACTERS: dict[str, FruitCharacter] = {
    
    # =========================================================================
    # APPLE - The Wise Mentor
    # Archetype: Sage/Mentor - evokes trust and wisdom
    # =========================================================================
    "apple": FruitCharacter(
        name="Apple",
        key="apple",
        color_palette="rich red with green leaf accent, warm golden highlights",
        visual_traits="perfectly round and glossy, with a single proud leaf, warm rosy cheeks",
        archetype="The Wise Mentor",
        personality="Warm, wise, and reassuring. Like a caring grandparent who always knows best.",
        voice_tone="Gentle, confident, and nurturing",
        emotional_hook="Nostalgia and comfort - reminds you of home, of being cared for",
        trust_builder="Speaks with quiet confidence, never pushy, always supportive",
        core_message="One small choice today creates a healthier tomorrow",
        health_benefits=[
            "Rich in fiber for digestive health",
            "Antioxidants to protect your cells",
            "Supports heart health naturally"
        ],
        call_to_action="Start tomorrow with just one apple. Your body will thank you.",
        intro_gesture="Warm, welcoming wave with a knowing smile",
        signature_move="Gentle nod of wisdom while sharing knowledge",
        farewell_gesture="Soft bow with hands together, like a blessing"
    ),
    
    # =========================================================================
    # BANANA - The Energetic Coach
    # Archetype: Hero/Athlete - evokes motivation and action
    # =========================================================================
    "banana": FruitCharacter(
        name="Banana",
        key="banana",
        color_palette="bright sunny yellow with cream interior, energetic gold accents",
        visual_traits="curved and athletic, with expressive arm-like peels, always in motion",
        archetype="The Energetic Coach",
        personality="Enthusiastic, motivating, and high-energy. Your personal cheerleader.",
        voice_tone="Upbeat, encouraging, and dynamic",
        emotional_hook="Excitement and possibility - makes you believe you can do anything",
        trust_builder="Celebrates small wins, never judges, always believes in you",
        core_message="Your body is capable of amazing things. Fuel it right!",
        health_benefits=[
            "Natural energy boost without the crash",
            "Potassium for muscle recovery",
            "Mood-lifting properties"
        ],
        call_to_action="Grab a banana before your next adventure. Feel the difference!",
        intro_gesture="Enthusiastic jump and fist pump",
        signature_move="Flexing tiny muscles while encouraging the viewer",
        farewell_gesture="Running off-screen energetically, then popping back for a wink"
    ),
    
    # =========================================================================
    # STRAWBERRY - The Joyful Friend
    # Archetype: Innocent/Child - evokes happiness and sweetness
    # =========================================================================
    "strawberry": FruitCharacter(
        name="Strawberry",
        key="strawberry",
        color_palette="vibrant red with tiny golden seeds, fresh green crown",
        visual_traits="heart-shaped and adorable, with freckle-like seeds, irresistibly cute",
        archetype="The Joyful Friend",
        personality="Sweet, playful, and genuinely happy. Spreads joy effortlessly.",
        voice_tone="Cheerful, warm, and innocent",
        emotional_hook="Pure joy and sweetness - reminds you of simple pleasures",
        trust_builder="Genuine authenticity, no hidden agenda, just pure happiness",
        core_message="Life is sweeter when you choose what's good for you",
        health_benefits=[
            "Vitamin C powerhouse for immunity",
            "Antioxidants for glowing skin",
            "Low-calorie natural sweetness"
        ],
        call_to_action="Add some sweetness to your day, the healthy way!",
        intro_gesture="Spinning with arms wide open, pure joy",
        signature_move="Giggling while bouncing on the spot",
        farewell_gesture="Blowing a kiss with both hands"
    ),
    
    # =========================================================================
    # MANGO - The Exotic Storyteller
    # Archetype: Explorer/Adventurer - evokes curiosity and wonder
    # =========================================================================
    "mango": FruitCharacter(
        name="Mango",
        key="mango",
        color_palette="sunset gradient from orange to golden yellow, tropical green accents",
        visual_traits="smooth and curvaceous, with a mysterious glow, slightly exotic features",
        archetype="The Exotic Storyteller",
        personality="Mysterious, fascinating, and deeply wise. Brings distant wisdom.",
        voice_tone="Smooth, captivating, and enchanting",
        emotional_hook="Wonder and adventure - opens your mind to possibilities",
        trust_builder="Shares ancient wisdom, respects your intelligence",
        core_message="The most treasured things in life are often the most natural",
        health_benefits=[
            "Digestive enzymes for gut health",
            "Beta-carotene for eye health",
            "Immune system support"
        ],
        call_to_action="Discover the treasure that grows on trees. Try mango today!",
        intro_gesture="Graceful bow with hands pressed together",
        signature_move="Mysterious twirl that reveals a golden glow",
        farewell_gesture="Fading into a beautiful sunset scene"
    ),
    
    # =========================================================================
    # ORANGE - The Sunny Optimist
    # Archetype: Caregiver/Healer - evokes warmth and healing
    # =========================================================================
    "orange": FruitCharacter(
        name="Orange",
        key="orange",
        color_palette="bright citrus orange with white pith details, sunny yellow highlights",
        visual_traits="perfectly spherical and bright, with a textured peel, radiates warmth",
        archetype="The Sunny Optimist",
        personality="Warm, healing, and infectiously positive. Like sunshine in fruit form.",
        voice_tone="Bright, warm, and uplifting",
        emotional_hook="Warmth and healing - makes you feel better just being around them",
        trust_builder="Genuine care for your wellbeing, asks about how you feel",
        core_message="Sunshine and vitamin C - nature's way of taking care of you",
        health_benefits=[
            "Vitamin C for immunity",
            "Hydration and freshness",
            "Natural mood booster"
        ],
        call_to_action="Let a little sunshine into your life. Squeeze the day!",
        intro_gesture="Arms spread wide like sun rays",
        signature_move="Spinning to create a warm golden glow",
        farewell_gesture="Waving both hands like twinkling sunlight"
    ),
    
    # =========================================================================
    # GRAPE - The Playful Buddy
    # Archetype: Jester/Friend - evokes fun and companionship
    # =========================================================================
    "grape": FruitCharacter(
        name="Grape",
        key="grape",
        color_palette="deep purple with lighter lavender highlights, green vine accent",
        visual_traits="small and round in a bunch, individual grape with friends nearby",
        archetype="The Playful Buddy",
        personality="Fun-loving, social, and always brings friends. Life of the party.",
        voice_tone="Playful, friendly, and slightly mischievous",
        emotional_hook="Fun and belonging - reminds you that good things come in groups",
        trust_builder="Never alone, always inclusive, makes you part of the bunch",
        core_message="Good things come in small packages. And they're better with friends!",
        health_benefits=[
            "Heart-healthy antioxidants",
            "Natural brain boosters",
            "Perfect healthy snack size"
        ],
        call_to_action="Grab a bunch and share with someone you love!",
        intro_gesture="Bouncing in while other grapes follow",
        signature_move="High-fiving other grapes in the bunch",
        farewell_gesture="Group wave with the whole bunch"
    ),
    
    # =========================================================================
    # WATERMELON - The Refreshing Giant
    # Archetype: Gentle Giant - evokes refreshment and generosity
    # =========================================================================
    "watermelon": FruitCharacter(
        name="Watermelon",
        key="watermelon",
        color_palette="green striped exterior, vibrant pink interior, black seed spots",
        visual_traits="large wedge-shaped slice, dripping with freshness, big and friendly",
        archetype="The Refreshing Giant",
        personality="Generous, refreshing, and endlessly giving. The gentle giant.",
        voice_tone="Deep, soothing, and refreshing",
        emotional_hook="Relief and refreshment - the answer to your thirst",
        trust_builder="Always has enough to share, never runs out of giving",
        core_message="Stay refreshed, stay happy. There's always more to give.",
        health_benefits=[
            "92% water for hydration",
            "Lycopene for heart health",
            "Natural coolant for the body"
        ],
        call_to_action="When life gets hot, cool down the natural way!",
        intro_gesture="Big, welcoming arms spread wide",
        signature_move="Splashing with refreshing droplets",
        farewell_gesture="Slow, satisfied wave while dripping refreshment"
    ),
    
    # =========================================================================
    # KIWI - The Quirky Genius
    # Archetype: Creator/Innovator - evokes curiosity and discovery
    # =========================================================================
    "kiwi": FruitCharacter(
        name="Kiwi",
        key="kiwi",
        color_palette="fuzzy brown exterior, vibrant green interior with black seed pattern",
        visual_traits="fuzzy and slightly odd-looking outside, beautiful surprise inside",
        archetype="The Quirky Genius",
        personality="Unique, surprising, and full of hidden depths. Don't judge by appearance.",
        voice_tone="Thoughtful, surprising, and slightly quirky",
        emotional_hook="Discovery and surprise - teaches you to look deeper",
        trust_builder="Reveals beautiful truths gradually, rewards curiosity",
        core_message="The best things in life aren't always obvious. Look closer.",
        health_benefits=[
            "More vitamin C than oranges",
            "Digestive enzymes for gut health",
            "Unique antioxidant profile"
        ],
        call_to_action="Be curious. Try something new. You might be surprised!",
        intro_gesture="Shy wave that transforms into confident reveal",
        signature_move="Opening to show beautiful green interior",
        farewell_gesture="Playful wink before closing back up"
    ),
}


# =============================================================================
# EPISODE TEMPLATES
# 3-Episode Structure for Maximum Emotional Impact
# =============================================================================

@dataclass
class EpisodeTemplate:
    """Template for each story episode."""
    
    episode_number: int
    purpose: str
    emotional_goal: str
    structure: str
    scene_guidance: str
    camera_movement: str
    audio_mood: str


EPISODE_TEMPLATES: list[EpisodeTemplate] = [
    
    # =========================================================================
    # EPISODE 1: THE HOOK
    # Psychology: Pattern interrupt + Curiosity gap
    # Goal: Stop the scroll, create intrigue
    # =========================================================================
    EpisodeTemplate(
        episode_number=1,
        purpose="Introduction & Curiosity Hook",
        emotional_goal="Create immediate intrigue and likability",
        structure="""
        Beat 1 (0-2s): Character appears with signature intro gesture
        Beat 2 (2-5s): Direct eye contact, warm greeting, creates connection
        Beat 3 (5-8s): Curiosity hook - hints at something valuable to share
        """,
        scene_guidance="""
        The character appears in a clean, bright environment. They notice the 
        viewer immediately and seem genuinely delighted. Their body language 
        is open and welcoming. They lean slightly forward as if sharing a 
        secret, creating intimacy. End with a moment of anticipation - 
        they're about to share something important.
        """,
        camera_movement="Slow push-in to create intimacy, subtle orbit for dynamism",
        audio_mood="Curious and inviting, with a gentle rising melody"
    ),
    
    # =========================================================================
    # EPISODE 2: THE CONNECTION
    # Psychology: Social proof + Empathy + Mirror neurons
    # Goal: Build trust, create emotional bond
    # =========================================================================
    EpisodeTemplate(
        episode_number=2,
        purpose="Emotional Connection & Trust Building",
        emotional_goal="Create deep emotional resonance and trust",
        structure="""
        Beat 1 (0-2s): Character shows understanding of viewer's struggles
        Beat 2 (2-5s): Shares relatable moment, uses signature move
        Beat 3 (5-8s): Genuine care expressed, viewer feels seen and understood
        """,
        scene_guidance="""
        The character demonstrates emotional intelligence. They might show a 
        moment of vulnerability or share wisdom from experience. Their 
        expressions are deeply empathetic. They might ask a rhetorical 
        question that makes the viewer reflect. The environment subtly 
        shifts to feel warmer, more intimate. End with a moment of 
        genuine connection - the viewer feels understood.
        """,
        camera_movement="Gentle breathing movement, intimate framing",
        audio_mood="Warm and understanding, emotionally resonant undertones"
    ),
    
    # =========================================================================
    # EPISODE 3: THE GIFT
    # Psychology: Reciprocity + Call to action + Positive anchoring
    # Goal: Deliver value, inspire action, create memorable ending
    # =========================================================================
    EpisodeTemplate(
        episode_number=3,
        purpose="Value Delivery & Memorable Farewell",
        emotional_goal="Inspire action and leave lasting positive impression",
        structure="""
        Beat 1 (0-2s): Character delivers the core health message with confidence
        Beat 2 (2-5s): Reinforces benefit with visual demonstration
        Beat 3 (5-8s): Warm farewell with signature gesture, call to action
        """,
        scene_guidance="""
        The character speaks with quiet authority - they've earned the right 
        to give advice. The message is delivered simply and memorably. 
        They might demonstrate the benefit visually (glowing, energized, etc).
        The environment reaches its most vibrant state. The farewell is 
        warm and genuine - they truly want the best for the viewer. 
        End with the signature farewell gesture that anchors positive emotion.
        """,
        camera_movement="Dynamic but controlled, ending with a slight pull-back reveal",
        audio_mood="Uplifting and inspiring, memorable closing notes"
    ),
]


def get_character(fruit_key: str) -> Optional[FruitCharacter]:
    """Get a fruit character by key."""
    return FRUIT_CHARACTERS.get(fruit_key.lower())


def get_all_characters() -> list[FruitCharacter]:
    """Get all available fruit characters."""
    return list(FRUIT_CHARACTERS.values())


def get_random_character() -> FruitCharacter:
    """Get a random fruit character."""
    return random.choice(list(FRUIT_CHARACTERS.values()))


def get_episode_template(episode_number: int) -> Optional[EpisodeTemplate]:
    """Get episode template by number (1, 2, or 3)."""
    for template in EPISODE_TEMPLATES:
        if template.episode_number == episode_number:
            return template
    return None
