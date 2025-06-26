"""Artist presets and layer type definitions for the MIDI generation app."""

from typing import Dict, List

ARTIST_PRESETS = {
    "🔥 Chris Stussy": {
        "description": "Dutch minimal house with warm analog character and jazz influences",
        "prompts": {
            "bassline": [
                "Chris Stussy inspired minimal house bassline with warm analog character, subtle jazz influences, and sophisticated groove. Focus on deep sub frequencies and organic timing variations.",
                "Dutch minimal house bass with classic machine drums, smooth bassline flow, and late-night underground vibes channeling Chris Stussy's signature sound.",
                "Minimal house bassline with raw production aesthetics, rolling groove, and the sophisticated restraint that defines Chris Stussy's style.",
            ],
            "melody": [
                "Jazz-influenced minimal house melody with sophisticated chord progressions and warm analog character, inspired by Chris Stussy's melodic sensibilities.",
                "Minimal house lead with subtle swing and jazz harmony, complementing the warm underground aesthetic of Chris Stussy.",
            ],
            "chords": [
                "Warm analog house chords with jazz influences and subtle progressions, capturing Chris Stussy's sophisticated harmonic approach.",
                "Minimal house chord progressions with organic warmth and underground sophistication.",
            ],
        },
    },
    "⚡ Kolter": {
        "description": "Evolution from deep tech to minimal with breaks and chunky grooves",
        "prompts": {
            "bassline": [
                "Kolter inspired minimal techno bassline with chunky groove elements, evolving from deep tech foundations into experimental minimal territory.",
                "Underground minimal bass with breaks influences and chunky rhythmic patterns, reflecting Kolter's artistic evolution and raw production style.",
                "Minimal techno bassline with deep foundation and experimental edge, capturing Kolter's transition from DJOKO to his current minimal aesthetic.",
            ],
            "melody": [
                "Minimal techno melody with experimental edge and chunky rhythmic elements, inspired by Kolter's evolution from deep house.",
                "Underground minimal lead with breaks influence and raw character.",
            ],
            "chords": [
                "Experimental minimal chords with deep techno foundation and chunky groove elements.",
                "Minimal techno chord progression with underground rawness and artistic evolution.",
            ],
        },
    },
    "🌊 M High": {
        "description": "Deep minimal house with sophisticated underground aesthetics",
        "prompts": {
            "bassline": [
                "M High style deep minimal house bassline with sophisticated underground groove, refined production, and contemporary minimal house aesthetics.",
                "Deep minimal bass with underground sophistication, subtle complexity, and the refined aesthetic that characterizes M High's productions.",
                "Minimal house bassline with deep foundation, sophisticated rhythm patterns, and contemporary underground sensibilities.",
            ],
            "melody": [
                "Sophisticated minimal house melody with deep underground character and refined aesthetic.",
                "Contemporary minimal house lead with sophisticated harmonic development.",
            ],
            "chords": [
                "Deep minimal house chords with sophisticated underground progression and contemporary aesthetics.",
                "Refined minimal house harmony with underground depth and sophisticated character.",
            ],
        },
    },
    "🔊 Gaskin": {
        "description": "Bass-heavy minimal house with robust low-end and underground grit",
        "prompts": {
            "bassline": [
                "Gaskin inspired bass-heavy minimal house with robust low-end frequencies, underground grit, and powerful sub-bass foundation that defines his sound.",
                "Deep minimal bassline with heavy low-end emphasis, raw underground character, and the robust bass foundation characteristic of Gaskin's style.",
                "Bass-heavy minimal house with powerful sub frequencies, underground rawness, and robust rhythmic foundation.",
            ],
            "melody": [
                "Bass-heavy minimal house melody with robust character and underground grit, complementing heavy low-end.",
                "Minimal house lead with powerful presence and underground rawness.",
            ],
            "chords": [
                "Robust minimal house chords with bass-heavy character and underground grit.",
                "Bass-heavy minimal harmony with powerful foundation and raw underground aesthetic.",
            ],
        },
    },
    "🖤 Obskür": {
        "description": "Dark minimal techno with atmospheric depth and underground edge",
        "prompts": {
            "bassline": [
                "Obskür inspired dark minimal techno bassline with atmospheric depth, underground edge, and the shadowy aesthetic that defines the Obskür sound.",
                "Dark minimal bass with atmospheric character, underground intensity, and mysterious depth reflecting Obskür's aesthetic approach.",
                "Minimal techno bassline with dark atmospheric qualities, underground edge, and the mysterious character of Obskür productions.",
            ],
            "melody": [
                "Dark minimal techno melody with atmospheric depth and mysterious underground character.",
                "Shadowy minimal lead with atmospheric intensity and underground edge.",
            ],
            "chords": [
                "Dark atmospheric minimal chords with mysterious depth and underground intensity.",
                "Minimal techno harmony with shadowy character and atmospheric underground aesthetic.",
            ],
        },
    },
    "🎯 Artmann": {
        "description": "Precise minimal techno with calculated grooves and refined production",
        "prompts": {
            "bassline": [
                "Artmann style precise minimal techno bassline with calculated groove patterns, refined production quality, and methodical rhythmic construction.",
                "Minimal techno bass with precise engineering, calculated rhythm, and the refined production aesthetic that characterizes Artmann's work.",
                "Calculated minimal bassline with precise groove architecture, refined production, and methodical approach to rhythm construction.",
            ],
            "melody": [
                "Precise minimal techno melody with calculated development and refined production aesthetic.",
                "Methodical minimal lead with precise harmonic construction and refined character.",
            ],
            "chords": [
                "Precise minimal techno chords with calculated progression and refined production quality.",
                "Methodical minimal harmony with precise construction and refined aesthetic.",
            ],
        },
    },
    "🇳🇱 Luuk Van Dijk": {
        "description": "Dutch minimal house with organic groove and sophisticated production",
        "prompts": {
            "bassline": [
                "Luuk Van Dijk inspired Dutch minimal house bassline with organic groove development, sophisticated production, and the natural flow of Dutch house tradition.",
                "Dutch minimal bass with organic rhythm patterns, sophisticated underground character, and the refined groove aesthetic of Luuk Van Dijk.",
                "Minimal house bassline with Dutch organic groove, sophisticated production values, and natural rhythmic flow.",
            ],
            "melody": [
                "Dutch minimal house melody with organic development and sophisticated underground character.",
                "Organic minimal lead with Dutch house influence and sophisticated groove aesthetic.",
            ],
            "chords": [
                "Dutch minimal house chords with organic progression and sophisticated production.",
                "Organic minimal harmony with Dutch house tradition and refined aesthetic.",
            ],
        },
    },
    "🏠 Sidney Charles": {
        "description": "Classic tech house with modern minimal influences and dancefloor energy",
        "prompts": {
            "bassline": [
                "Sidney Charles inspired tech house bassline with modern minimal influences, dancefloor energy, and the groove-focused approach of classic tech house.",
                "Tech house bass with minimal modern touches, dancefloor functionality, and the refined groove aesthetic that Sidney Charles brings to house music.",
                "Modern tech house bassline with minimal influences, dancefloor energy, and sophisticated groove construction.",
            ],
            "melody": [
                "Tech house melody with modern minimal influences and strong dancefloor energy.",
                "Groove-focused tech house lead with minimal aesthetic and dancefloor functionality.",
            ],
            "chords": [
                "Tech house chords with modern minimal touches and dancefloor energy.",
                "Groove-focused tech house harmony with minimal influences and refined aesthetic.",
            ],
        },
    },
    "🎵 Marsolo": {
        "description": "Contemporary minimal house with melodic sensibilities and underground depth",
        "prompts": {
            "bassline": [
                "Marsolo inspired contemporary minimal house bassline with melodic sensibilities, underground depth, and sophisticated harmonic foundation.",
                "Minimal house bass with melodic character, contemporary production, and the underground sophistication that defines Marsolo's approach.",
                "Contemporary minimal bassline with melodic foundation, underground depth, and sophisticated rhythmic development.",
            ],
            "melody": [
                "Contemporary minimal house melody with sophisticated harmonic sensibilities and underground depth.",
                "Melodic minimal lead with contemporary production and underground sophistication.",
            ],
            "chords": [
                "Contemporary minimal house chords with melodic sophistication and underground depth.",
                "Melodic minimal harmony with contemporary aesthetic and sophisticated development.",
            ],
        },
    },
}

LAYER_TYPES = {
    "🎸 Bassline": {
        "description": "Foundation low-end groove",
        "icon": "🎸",
        "color": "#FF6B6B",
    },
    "🎹 Melody": {
        "description": "Main melodic content",
        "icon": "🎹",
        "color": "#4ECDC4",
    },
    "🎶 Chords": {
        "description": "Harmonic progression",
        "icon": "🎶",
        "color": "#45B7D1",
    },
    "🎺 Lead": {"description": "Lead synth element", "icon": "🎺", "color": "#96CEB4"},
    "🥁 Drums": {"description": "Rhythmic percussion", "icon": "🥁", "color": "#FECA57"},
    "🎛️ FX": {
        "description": "Sound effects and textures",
        "icon": "🎛️",
        "color": "#FF9FF3",
    },
}

CREATIVE_CONTROLS = {
    "🎯 Focus": {
        "description": "Layer focus and prominence",
        "options": ["Subtle", "Balanced", "Prominent", "Dominant"],
        "default": "Balanced",
    },
    "🌊 Energy": {
        "description": "Overall energy level",
        "options": ["Minimal", "Moderate", "Energetic", "Peak"],
        "default": "Moderate",
    },
    "🎨 Style": {
        "description": "Musical approach",
        "options": ["Classic", "Modern", "Experimental", "Fusion"],
        "default": "Modern",
    },
    "⚡ Intensity": {
        "description": "Dynamic intensity",
        "options": ["Gentle", "Medium", "Strong", "Aggressive"],
        "default": "Medium",
    },
}
