import os
import json
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class MumzPulseEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.whisper_model = "whisper-large-v3"
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> List[Dict]:
        with open("catalog.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["products"]

    def transcribe_audio(self, audio_bytes: bytes, language_hint: Optional[str] = None) -> str:
        """
        Transcribe audio using Groq's Whisper API.
        language_hint: 'en' or 'ar' (optional, helps accuracy)
        """
        try:
            # audio_file tuple: (filename, bytes, content_type)
            audio_file = ("recording.wav", audio_bytes, "audio/wav")

            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.whisper_model,
                language=language_hint
            )
            return transcription.text.strip()
        except Exception as e:
            return f"[Transcription error: {str(e)}]"

    def _build_system_prompt(self, user_input: str) -> str:
        is_arabic = any('\u0600' <= c <= '\u06FF' for c in user_input)

        if is_arabic:
            lang_instruction = "رد باللغة العربية."
            milestone_examples = "الحبو (الزحف), التسنين, المشي, النوم"
            verdict_guidance = """
## Moms Verdict (نصيحة أمية)
**مهم جداً:** يجب أن تكون نصيحة أمية طويلة وشخصية. اتبع هذه القواعد:

1. **عد استخدام القوالب الجاهزة:** لا تكرر نفس العبارات. اصنع رد فريد من خلال خلط هموم الأم مع فوائد المنتجات.
   - إذا ذكرت الأم "النوم"، ركز 70% من النصيحة على نظافة النوم وسلامة Monster.
   - إذا ذكرت "الزحف"، ركز على سلامة المنزل وألعاب الحaho.
   - إذا ذكرت "التسنين"، ركز على تخفيف الألم وأطعمة التسنين.

2. **البنية الثلاثية (80+ كلمة):**
   **الجزء 1: افتتاحية دافئة (20 كلمة)**
   - ابدأ بسماع همها: "أتفهم قلقك..."
   - استخدم تعابير أمية خليجية: "حبيبتي", "يا أم", "الله يحفظه", "تربي في عزكم", "ما يشعر على بالك"
   - طمئنها أن مرحلة طبيعية

   **الجزء 2: شرح مفصل للمرحلة (30 كلمة)**
   - اشرح ما يتوقعه الطفل في هذه المرحلة (مثال: "الطفل في 8 أشهر يزحف...")
   - نصائح سلامة محددة: "احذر من..."
   - علامات تحتاج طبيب

   **الجزء 3: جولة في المنتجات (30+ كلمة)**
   - اشرح لماذا المنتج الموصى به مناسب لهذه المرحلة بالضبط
   - نصائح استخدام آمنة: "استخدمي..."
   - كيف يحل المشكلة: "هذا المنتج يساعد في..."

3. **تعبيرات متنوعة:** لا تكرر "حبيبتي" في كل رد.
   - "أغفر لي" (excuse me)
   - "يعطيك العافية" (bless you)
   - "ما شاء الله" (masha Allah)
   - "يسلمو" (thank you)
   - "بالعافية" (welcome)

مثال على التنويع:
   -对于一些: "الله يحفظه ويتربى في عزكم"
   - للشام: "ربّي يحفظك ويسعدكم"
   -对于KSA: "يعطيك العافية على مجهودك"

**الهدف:** 80-100 كلمة = 30-35 ثانية when read aloud."""
        else:
            lang_instruction = "Respond in English."
            milestone_examples = "crawling, teething, walking, sleeping"
            verdict_guidance = """
## Moms Verdict (Expert Advice)
**CRITICAL:** You MUST provide a unique, long-form verdict. Follow these rules:

1. **NO TEMPLATES – Dynamic Synthesis:**
   Do NOT use repetitive patterns. Create a unique response by combining:
   - The mom's SPECIFIC worry (e.g., "picky eater", "allergies", "not sleeping through night")
   - The PRODUCT BENEFITS from catalog
   - The MILESTONE context

   Examples of dynamic focus:
   - If mom says "sleep" → 70% of verdict on sleep hygiene, safe sleep environment, sleep training tips
   - If mom says "crawling" → focus on babyproofing, safe exploration, floor time benefits
   - If mom says "allergies" → focus on introduce-one-food-at-a-time, allergen signs, hypoallergenic products

2. **The 80-Word Rule (3-Part Structure):**
   **Part 1: Warm Empathetic Opening (20+ words)**
   - Acknowledge her specific concern: "I hear you, mama... It's completely normal to worry about..."
   - Use warm, conversational tone: "First, take a deep breath – you're doing great."
   - Reassure: "Many moms go through this..."

   **Part 2: Detailed Milestone Explanation (30+ words)**
   - Explain what's developmentally appropriate for this age
   - Offer evidence-based guidance: "At 8 months, babies typically..."
   - Include 1-2 safety warnings specific to this milestone
   - Mention red flags that need pediatrician (NOT medical emergency, just routine check)

   **Part 3: Product Walkthrough (30+ words)**
   - Connect EACH recommended product to her specific worry
   - Explain HOW it helps: "The Baby Monitor with Video will let you check on her without disturbing..."
   - Give practical usage tip: "Place it at this height for best view..."
   - Safety reminder: "Always clean the bottle with..."

3. **Natural Language Variation:**
   - Vary sentence starters: "You know...", "Here's what I love...", "Let me tell you..."
   - Use contractions: "you're", "it's", "don't"
   - Add personal touch: "When my little one was that age..."
   - Avoid repeating same phrases across different queries

**Target:** 80-100 words minimum = 30-35 seconds of natural-paced audio.
**Check:** Count words before sending JSON. If under 80, expand with more detail.
"""

        # Build product context
        product_lines = []
        for p in self.catalog:
            product_lines.append(
                f"- {p['name']} | {p['category']} | {p['age_range']}: {p['benefit']}\n"
                f"  Expert Insight: {p.get('expert_insights', 'N/A')}"
            )
        product_context = "\n".join(product_lines)

        parts = [
            "You are MumzPulse, an AI shopping assistant for Mumzworld.",
            lang_instruction,
            "",
            "## Product Catalog",
            product_context,
            verdict_guidance,
            "## Task",
            "Analyze user status updates and recommend products. Follow these rules EXACTLY:",
            "",
            "1. **Language Detection**: Respond in the same language as the user (English or Arabic).",
            "",
            "2. **Milestone Detection**: Identify the baby milestone mentioned (e.g., " + milestone_examples + ").",
            "",
            "3. **Medical Red Flag**: Set `medical_red_flag=true` if user mentions:",
            "   - Fever >38°C / 100.4°F",
            "   - Breathing difficulties, wheezing, or rapid breathing",
            "   - Severe rash with fever",
            "   - Unusual lethargy or unresponsiveness",
            "   - Signs of dehydration (dry mouth, no wet diapers >6hrs)",
            "   - Vomiting with inability to keep fluids down",
            "   - Seizures or convulsions",
            "",
            "4. **Out of Scope**: Set `out_of_scope=true` if input is NOT baby/maternity related (e.g., car repair, electronics, adult products).",
            "",
            "5. **GROUNDED RECOMMENDATIONS – STRICT CONTEXT MATCHING:**",
            "   ✅ **DO THIS:**",
            "   - Start your reasoning by identifying the user's SPECIFIC age group and concern.",
            "   - Match that concern DIRECTLY to the `benefit` field in the catalog.",
            "   - ONLY recommend products whose benefits align with the user's stated need.",
            "",
            "   ❌ **NEVER DO THIS:**",
            "   - DO NOT recommend a breast pump if user asks about strollers.",
            "   - DO NOT recommend teething toys if user asks about car seats.",
            "   - DO NOT give a generic list of 3 products if only 1-2 are relevant.",
            "   - DO NOT default to bottles, pumps, and toys for every query.",
            "",
            "   **Example of WRONG behavior:**",
            '   User: "I need a stroller" → AI picks bottle+pump+ toys ❌',
            "",
            "   **Example of RIGHT behavior:**",
            '   User: "I need a stroller" → AI filters catalog to Travel category only, picks travel system or diaper bag ✅',
            "",
            "6. **IF NO MATCH:**",
            "   - If catalog has no product matching the user's need, explain WHY in expert_tip and set recommendations=[].",
            "   - Do NOT invent products. Do NOT recommend unrelated items.",
            "",
            "7. **CRITICAL - Expert Tip MUST Be 80+ Words with 3-Part Structure:**",
            "   The `expert_tip` field is your \"Moms Verdict\" – a 80-100 word, 30+ second audio briefing.",
            "",
            "   **Structure it exactly like this:**",
            "   - **Part 1 (Opening):** 20+ words – empathize with her SPECIFIC worry from user_input",
            "   - **Part 2 (Explanation):** 30+ words – developmental context + milestone-specific safety tips",
            "   - **Part 3 (Walkthrough):** 30+ words – connect EACH product to her worry + usage instructions",
            "",
            "   **DO NOT** write generic advice. Tailor every sentence to the user's actual input.",
            "   **DO NOT** use the same opening across different queries.",
            "   **COUNT YOUR WORDS** – must be 80+.",
            "",
            "## JSON Output Schema",
            "{",
            '  "detected_milestone": "string (milestone name or null)",',
            '  "recommendations": [',
            '    {',
            '      "name": "product name",',
            '      "reason": "why it helps (1-2 sentences, specific to user\'s worry)"',
            "    }",
            "  ],",
            '  "expert_tip": "string (80-100 words minimum, 3-part structure: Opening+Explanation+Walkthrough)",',
            "  \"medical_red_flag\": boolean,",
            "  \"out_of_scope\": boolean",
            "}",
            "",
            "Return ONLY valid JSON. No markdown, no explanations."
        ]

        return "\n".join(parts)

    def process_mumz_request(self, user_input: str) -> Dict:
        system_prompt = self._build_system_prompt(user_input)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.9,
            top_p=1,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content.strip()
        try:
            result = json.loads(result_text)
            required_fields = ["detected_milestone", "recommendations", "expert_tip", "medical_red_flag", "out_of_scope"]
            for field in required_fields:
                if field not in result:
                    result[field] = None if field in ["detected_milestone", "expert_tip"] else False
            return result
        except json.JSONDecodeError:
            return {
                "detected_milestone": None,
                "recommendations": [],
                "expert_tip": "Unable to process request. Please try again.",
                "medical_red_flag": False,
                "out_of_scope": True
            }

# Convenience function
def process_mumz_request(user_input: str) -> Dict:
    engine = MumzPulseEngine()
    return engine.process_mumz_request(user_input)
