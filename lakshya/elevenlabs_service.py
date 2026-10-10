"""
AarogyaSahay - ElevenLabs Voice Intelligence Service
Enables lifelike, empathetic conversational voice responses for rural healthcare access,
multilingual guidance (Hindi, English, regional dialects), and enhanced accessibility
for users with low literacy or visual impairments.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

# Default ElevenLabs Settings
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL = "eleven_multilingual_v2"  # Flagship model with Hindi, English, and 27+ languages

# Curated healthcare-friendly voices
DEFAULT_VOICES = [
    {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel (Aarogya Clinical Voice)",
        "description": "Calm, clear, and reassuring medical narrator",
        "gender": "Female"
    },
    {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Sarah (ASHA Care Provider)",
        "description": "Warm, gentle, and empathetic maternal caregiver",
        "gender": "Female"
    },
    {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "name": "Antoni (Primary Care Physician)",
        "description": "Reassuring, clear, and supportive doctor voice",
        "gender": "Male"
    },
    {
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "name": "Daniel (Public Health Guide)",
        "description": "Authoritative, clear public health communicator",
        "gender": "Male"
    }
]

_runtime_api_key = None


def get_api_key() -> Optional[str]:
    """Retrieve ElevenLabs API key from runtime memory, env vars, or .env file."""
    global _runtime_api_key
    if _runtime_api_key:
        return _runtime_api_key

    key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("XI_API_KEY")
    if key and key.strip():
        return key.strip()

    # Check local .env files
    for env_path in [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("ELEVENLABS_API_KEY=") or line.startswith("XI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    return None


def set_runtime_api_key(api_key: str) -> bool:
    """Store API key into runtime and write to local .env for persistence."""
    global _runtime_api_key
    clean_key = api_key.strip()
    _runtime_api_key = clean_key
    os.environ["ELEVENLABS_API_KEY"] = clean_key

    # Persist to local .env file
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    try:
        lines = []
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("ELEVENLABS_API_KEY=") and not line.startswith("XI_API_KEY="):
                        lines.append(line)
        lines.append(f"ELEVENLABS_API_KEY={clean_key}\n")
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        logger.warning(f"Failed to persist ElevenLabs key to .env: {e}")
        return True


def is_configured() -> bool:
    """Check if an ElevenLabs API key is configured."""
    key = get_api_key()
    return bool(key and len(key) > 8)


def test_elevenlabs_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Verify ElevenLabs API key against the official API."""
    key = api_key or get_api_key()
    if not key:
        return {"success": False, "error": "No ElevenLabs API key configured."}

    try:
        response = requests.get(
            f"{ELEVENLABS_API_URL}/user",
            headers={"xi-api-key": key},
            timeout=8
        )
        if response.status_code == 200:
            user_data = response.json()
            sub = user_data.get("subscription", {})
            return {
                "success": True,
                "tier": sub.get("tier", "free"),
                "character_count": sub.get("character_count", 0),
                "character_limit": sub.get("character_limit", 10000),
                "message": "ElevenLabs Voice API connected successfully!"
            }
        else:
            return {
                "success": False,
                "error": f"ElevenLabs API returned HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}


def get_available_voices() -> List[Dict[str, Any]]:
    """Return list of recommended healthcare voices."""
    return DEFAULT_VOICES


def text_to_speech(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = DEFAULT_MODEL
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Generate realistic spoken audio from text using ElevenLabs.
    Returns (audio_bytes, error_message).
    """
    key = get_api_key()
    if not key:
        return None, "ElevenLabs API key not configured"

    # Truncate to reasonable speech length if needed (e.g. 1500 chars)
    clean_text = text.replace("*", "").replace("#", "").strip()[:1500]
    if not clean_text:
        return None, "Text is empty"

    url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": clean_text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.15,
            "use_speaker_boost": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.content, None
        else:
            logger.error(f"ElevenLabs TTS failed [{response.status_code}]: {response.text}")
            return None, f"ElevenLabs error ({response.status_code}): {response.text[:150]}"
    except Exception as e:
        logger.error(f"ElevenLabs request exception: {e}")
        return None, str(e)
