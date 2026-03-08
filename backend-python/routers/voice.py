from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import whisper
import os
import tempfile
from deep_translator import GoogleTranslator
from services.classifier import classify_complaint
from services.sentiment import analyze_sentiment

router = APIRouter()

# Load Whisper model (lazy loading)
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        try:
            whisper_model = whisper.load_model("base")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"⚠️ Whisper model loading failed: {e}")
    return whisper_model

class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: str
    translated_text: str
    classification: dict
    sentiment: dict

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file using Whisper
    Supports: mp3, wav, ogg, m4a
    """
    try:
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.webm']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Load Whisper model
            model = get_whisper_model()
            if not model:
                raise HTTPException(status_code=500, detail="Whisper model not available")
            
            # Transcribe
            result = model.transcribe(temp_path)
            transcript = result["text"]
            detected_language = result.get("language", "en")
            
            # Translate to English if needed
            translated_text = transcript
            if detected_language != "en":
                try:
                    translator = GoogleTranslator(source=detected_language, target='en')
                    translated_text = translator.translate(transcript)
                except Exception as e:
                    print(f"Translation error: {e}")
                    translated_text = transcript
            
            # Run AI classification on translated text
            classification = classify_complaint(translated_text)
            
            # Run sentiment analysis
            sentiment = analyze_sentiment(translated_text)
            
            return {
                "transcript": transcript,
                "detected_language": detected_language,
                "translated_text": translated_text,
                "classification": classification,
                "sentiment": sentiment
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
