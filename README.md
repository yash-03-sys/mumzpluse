
Loom Video link : https://www.loom.com/share/bcd4fb408cd24e4eac7222f1ade7f64a

# MumzPulse 

Milestone-Driven Shopping Assistant for Mumzworld – an AI-powered prototype that analyzes baby status updates and recommends relevant products from the Mumzworld catalog.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Tooling & Dependencies](#tooling--dependencies)
5. [Evaluation Rubric](#evaluation-rubric)
6. [Project Structure](#project-structure)

---

## Overview

MumzPulse helps parents discover the right products at the right developmental stage. Users submit status updates via **text or voice recording** (e.g., "My baby started teething" or "ابني بدأ يزحف"), and the AI assistant:

- Detects the baby milestone
- Recommends 2-3 matching products from the catalog
- Provides an expert parenting tip (read aloud via TTS)
- Flags medical emergencies and out-of-scope queries

The system supports **English and Arabic** multilingual input with automatic speech-to-text and text-to-speech conversion.

---

## Architecture

```mermaid
graph TB
    User[👤 User Input<br/>Voice/Text Status] --> UI[Streamlit UI<br/>main.py]
    UI --> |Voice Recording| Whisper[Groq Whisper API<br/>Speech-to-Text]
    Whisper --> UI
    UI --> Engine[AI Engine<br/>engine.py]
    Engine --> Groq[Groq API<br/>LLaMA 3.3 70B]
    Engine --> Catalog[Product Catalog<br/>catalog.json]
    Engine --> Output[JSON Response<br/>Structured Schema]
    Output --> UI
    UI --> |Expert Tip| TTS[gTTS<br/>Text-to-Speech]
    TTS --> Audio[ Audio Playback<br/>Auto-detect Language]
    UI --> Display[ UI States:<br/>- Success (Green)<br/>- Medical Alert (Red)<br/>- Warning (Yellow)]

    style User fill:#e1f5e1
    style Groq fill:#fff4e6,stroke:#ff9500
    style Whisper fill:#fff4e6,stroke:#ff9500
    style Output fill:#e3f2fd
    style Display fill:#fce4ec
    style TTS fill:#e8f5e9
```

### Data Flow

1. **Input Capture** – Streamlit text area or voice recorder collects user status update
2. **Speech-to-Text** – Audio sent to Groq Whisper API (if voice input); result auto-fills text field
3. **Language Detection** – Engine auto-detects English vs. Arabic from transcribed text
4. **Product Retrieval** – `catalog.json` loaded into memory
5. **LLM Inference** – Prompt sent to Groq's LLaMA 3.3 70B with JSON schema constraint
6. **Structured Output** – Response parsed into `detected_milestone`, `recommendations`, `expert_tip`, `medical_red_flag`, `out_of_scope`
7. **Text-to-Speech** – `expert_tip` (or medical warning) converted to audio via gTTS with auto language detection
8. **State-Based Rendering** – UI displays appropriate message type (Success/Alert/Warning) and provides "Listen to Advice" audio player

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Access to [Groq Cloud](https://console.groq.com) for API key
- Git (optional)

### 1. Clone & Navigate

```bash
cd mumzpulse
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit streamlit-mic-recorder groq python-dotenv tabulate gtts
```

### 3. Configure Environment

Edit `.env` and replace the placeholder with your actual Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

**Note:** Obtain your key from [Groq Console](https://console.groq.com/keys).

### 4. Run the Application

```bash
streamlit run main.py
```

The app opens at `http://localhost:8501`.

---

## Tooling & Dependencies

| Tool | Purpose |
|------|---------|
| **Groq API** | LLM + Whisper inference provider – delivers LLaMA 3.3 70B and Whisper transcription at high speed via LPUs |
| **Streamlit** | Web UI framework – rapid prototyping, state management |
| **streamlit-mic-recorder** | Voice input capture – hands-free audio recording for busy parents |
| **gTTS (Google Text-to-Speech)** | Multilingual audio output – converts expert tips to speech in English/Arabic |
| **LLaMA 3.3 70B Versatile** | Base model – handles multilingual prompts and constrained JSON output |
| **Python 3.10+** | Runtime – type hints, structured error handling |
| **Tabulate** | Evaluation table formatting |

### AI Agent Configuration

The engine uses a system prompt with:
- **Zero-shot classification** for milestone detection
- **Guardrails** for medical emergency and out-of-scope detection
- **Structured JSON schema** enforcement via `response_format={"type": "json_object"}`
- **Multilingual prompt injection** based on input script detection
- **Long-form "Moms Verdict" requirement** – `expert_tip` explicitly mandated 80-100 words with 3-part structure (Opening, Explanation, Product Walkthrough)
- **Dynamic Synthesis Directive** – AI instructed to avoid templates; combine user's specific worry with product benefits (e.g., sleep queries focus on sleep hygiene, crawling queries focus on safety)
- **Arabic Variation Protocol** – GCC-specific idioms (الله يحفظه, تربي في عزكم, يعطيك العافية) vary across responses to sound human
- **Temperature 0.9 + top_p=1** – High creativity sampling prevents repetitive outputs; ensures each query generates unique, context-aware recommendations
- **Strict Grounding Rules** – System prompt mandates: "ONLY recommend products whose benefits align with user's stated need. DO NOT recommend breast pump if user asks about strollers."
- **No Conversation History** – Messages array contains only current system + user message; no memory of previous interactions to avoid context contamination
- **Max tokens 2048** – Accommodates long-form 80+ word responses
- **Expert insights injection** – Catalog includes `expert_insights` field providing safety context for richer verdicts

### Busy Mom Use Case: Hands-Free Multimodal Interaction

MumzPulse solves the real-world constraint of parents juggling babies and devices with **fully hands-free operation**:

#### 🎤 Voice Input → AI Processing
1. Parent taps **"Start Recording"** and speaks naturally (English/Arabic)
2. Audio sent to **Groq Whisper API** → instant transcription
3. Transcribed text auto-fills the input field (editable if needed)
4. Parent taps **"Analyze"** → AI processes the spoken status update

#### Voice Output
- Expert tips converted to audio via **gTTS** with automatic language detection (Arabic RTL check)
- Medical emergencies prioritized: audio warning overrides recommendations
- **"Listen to Advice"** button plays audio directly in browser – no file downloads

#### Seamless Multilingual
- **Input:** Whisper auto-detects English vs Arabic during transcription
- **Output:** gTTS selects `lang='ar'` or `lang='en'` based on Unicode RTL character detection
- No language selector needed – works naturally for bilingual parents

####  Technical Implementation
- Audio passed to Whisper as bytes via `client.audio.transcriptions.create()` (no temp files)
- TTS output stored in `io.BytesIO` and Streamlit session state for instant playback
- RTL detection: `any('\u0600' <= c <= '\u06FF' for c in text)` reliably distinguishes Arabic
- 30-second audio briefing: AI's `expert_tip` mandated to be 4-6 sentences, gTTS processing with loading spinner for smooth UX

####  30-Second Audio Briefing Design
MumzPulse delivers **30+ second comprehensive audio briefings** – not one-word tips:

**Structure (80-100 words, 3 parts):**
1. **Warm Opening (20+ words)** – Acknowledges mom's specific worry; uses empathetic, conversational tone
2. **Milestone Explanation (30+ words)** – Developmental context + milestone-specific safety tips + red flag warnings
3. **Product Walkthrough (30+ words)** – Connects each recommended product to her worry + usage instructions + safety reminders

**AI Quality Controls:**
- **Dynamic Synthesis:** No templates – AI combines user's specific concern with product benefits (e.g., sleep queries focus on sleep hygiene, crawling queries focus on babyproofing)
- **Temperature 0.9 + top_p=1:** Maximum creativity sampling ensures unique, non-repetitive responses; eliminates "same 3 products every time" problem
- **Strict Grounding Rule:** System prompt enforces: "ONLY recommend products whose benefits align with user's need. DO NOT recommend breast pump if user asks about strollers."
- **No History Memory:** Messages array contains only current query; prevents cross-query contamination
- **Arabic Variation:** GCC idioms (الله يحفظه, تربي في عزكم, يعطيك العافية) vary naturally; never repeats same phrase
- **Word Count Enforcement:** System prompt mandates 80+ words; AI self-checks before JSON output

**Busy Mom UX:**
- Loading spinner shows " Generating 30-second audio briefing..." while gTTS processes
- Audio plays directly in browser – no downloads, no temp files
- Medical emergencies override with priority warning in same language

This multimodal pipeline enables **eyes-free, hands-free** assistance – a parent can record a voice note while nursing, then listen to product recommendations without touching the screen.

---

## Grounded Recommendations (v1.4 Fix)

**Problem Solved:** Early versions returned the same 3 products (bottle, pump, toys) for every query regardless of user intent.

**Solution Implemented:**
- **Strict Context Matching:** System prompt explicitly forbids recommending unrelated categories. Example: "DO NOT recommend breast pump if user asks about strollers."
- **Dynamic Reasoning:** AI identifies user's specific age group and concern, then matches ONLY to the `benefit` field in the catalog.
- **No Memory Contamination:** Messages array contains only current system + user message. Previous conversations are never included.
- **High Creativity Sampling:** `temperature=0.9`, `top_p=1` forces diverse, context-aware outputs.
- **Fallback Behavior:** If no catalog product matches, AI explains why instead of giving generic list.

**Verification Tests:**
```bash
python test_grounding.py
```

Expected:
- Stroller query → Travel products (Travel System, Diaper Bag, Car Seat Stroller) – NO breast pump
- Teething query → Feeding/Toys (Bottle Set, Sensory Toys) – NO stroller

---

## Evaluation Rubric

The `evals.py` script runs 5 predefined test cases:

| Test Case | Category | Expected Behavior |
|---|---|---|
| English – Crawling | Standard milestone | Detect "crawling", recommend travel/safety toys |
| Arabic – Teething | Multilingual | Detect "تسنين", respond in Arabic, recommend teething products |
| Medical Emergency – Fever | Safety critical | `medical_red_flag=True`, no product recommendations |
| Out of Scope – Car repair | Relevance filter | `out_of_scope=True`, yellow warning displayed |
| Ambiguous Input | Robustness | Request clarification or make safe default recommendation |

### Running Evaluations

```bash
python evals.py
```

Output shows a formatted table with Expectation vs. Reality comparison:

```
Test Case               Detected Milestone  ... Status  Expert Tip (preview)
───────────────────────────────────────────────────────────────────────────────
English - Crawling      crawling             ...  PASS  For crawling stage...
...
```

**Pass Criteria:** All 5 tests must meet expected flag values.

---

## Project Structure

```
mumzpulse/
├── .env                  # Environment variables (user-edited)
├── catalog.json          # Mock product database (10 items)
├── engine.py             # AI inference engine + Groq integration
├── main.py               # Streamlit application entry point
├── evals.py              # Automated test script
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore            # Excludes .env, __pycache__, etc.
```

---

## User Interface

MumzPulse uses a clean, minimal Streamlit interface:

- **Header:** Title "MumzPulse AI Assistant" with subtitle
- **Input:** Single text area + voice recorder button below
- **Action:** Standard "Analyze" button
- **Results:** Sequential display: milestone → expert advice → product list → audio player
- **States:** Standard Streamlit alerts (`st.success`, `st.error`, `st.warning`, `st.info`)
- **Products:** Vertical numbered list with italic reasoning
- **Audio:** Native `st.audio()` player for 30-second TTS briefing

No custom CSS. All standard Streamlit components for maximum stability.

---

## Future Enhancements

- Dynamic catalog loading from Mumzworld API
- User session history & preference learning
- Arabic-to-English translation fallback for catalog search
- Accessibility filters (e.g., products for special needs)
- A/B testing interface for recommendation quality

---

> **Prototype v2.1** – Clean functional UI, grounded recommendations, 30-second multilingual audio briefings, strict context matching (temperature=0.9, top_p=1).
