"""
Centralized localization module for FMD Detect.

Every user-facing string in the application lives in TRANSLATIONS, keyed by
language ("en" / "ar") and then by section. app2.py never hardcodes UI text
directly - it always reads from `T = TRANSLATIONS[st.session_state.lang]`.

This keeps translations maintainable in one place and guarantees the whole
site (nav, hero, tips, upload, questions, result, recommendation panel,
footer, errors, placeholders) switches language together, instantly, from
a single source of truth.
"""

TRANSLATIONS = {
    "en": {
        "dir": "ltr",
        "lang_name": "English",

        "nav": {
            "home": "Home",
            "about": "About FMD",
            "tips": "Tips",
            "diagnosis": "Diagnosis",
            "results": "Results",
            "contact": "Contact",
            "lang_switch": "العربية",
        },

        "hero": {
            "title": "FMD DETECTION",
            "slogan": "\u201cOur Wealth is Animals Health\u201d",
            "sub": "AI-Powered Early Detection System",
            "cta": "🚀 Start Diagnosis",
        },

        "about": {
            "title": "About FMD Detect",
            "text": (
                "FMD Detect is an AI-powered early-screening tool that combines "
                "deep-learning image analysis with a clinical symptom questionnaire "
                "to help flag possible Foot-and-Mouth Disease cases in livestock "
                "early — so farmers and veterinarians can act quickly."
            ),
        },

        "tips": {
            "title": "QUICK TIPS",
            "sub": "Before You Take the Photo",
            "tip1_title": "Clean & Clear",
            "tip1_text": "Make sure there is no straw, hay, or mud on the animal's mouth or hooves before taking the photo.",
            "tip2_title": "Wash & Dry",
            "tip2_text": "Gently wash the affected area with lukewarm water and wait until it is completely dry.",
            "tip3_title": "Good Lighting",
            "tip3_text": "Take the photo in good lighting, ensuring that there are no shadows covering the affected area.",
        },

        "upload": {
            "step_badge": "Step 1 of 2",
            "title": "📋 New Diagnosis Request",
            "subtitle": "Upload clear, high-quality photos of the suspected lesions",
            "dropzone_title": "Drag & drop images here",
            "dropzone_caption": "Supports JPG, PNG and HEIC, up to 20MB per image",
            "remove": "✕ Remove",
            "continue": "Continue to Questions ➡️",
            "continue_help": "Please upload at least one image first",
        },

        "questions": {
            "step_badge": "Step 2 of 2",
            "title": "📝 Clinical Questionnaire",
            "subtitle": "Please answer all of the following questions accurately",
            "submit": "🔍 Show Diagnosis Result",
            "back": "⬅️ Back to Upload",
            "gov_error": "Please select a governorate before continuing.",
            "gov_placeholder": "Select governorate",
            "yes": "Yes",
            "no": "No",
            "fields": {
                "animal_type": "What type of animal is it?",
                "fever": "Does the animal have a high fever?",
                "salivation": "Is there excessive drooling / salivation?",
                "mouth_lesions": "Are there ulcers or blisters in the mouth?",
                "lameness": "Is the animal limping or unable to walk normally?",
                "hoof_lesions": "Are there wounds around the hooves or limbs?",
                "chewing_problem": "Does the animal have difficulty chewing?",
                "mucous_abnormal": "Are the mucous membranes abnormal?",
                "skin_turgor_abnormal": "Is there visible skin dehydration (abnormal skin-turgor test)?",
                "body_swelling": "Is there any swelling on the body?",
                "nasal_lesion": "Are there wounds around the nose?",
                "governorate": "Which governorate is the animal located in?",
            },
            "animal_options": {
                "Cattle": "Cattle",
                "Goat": "Goat",
                "Sheep": "Sheep",
            },
        },

        "result": {
            "title": "Diagnosis Result",
            "status_label": "Diagnostic Status",
            "confidence_label": "Confidence Level",
            "model_meta": "🧬 Model: FMD-V4-Clinical",
            "last_update": "Last updated:",
            "image_tag": "📷 Uploaded Image",
            "new_diagnosis": "🔄 Start New Diagnosis",
            "bell_show": "🔔 Show Recommendation",
            "bell_hide": "🔔 Hide Recommendation",
            "verdicts": {
                "healthy": "NOT FMD",
                "suspected": "FMD",
                "infected": "Infected",
            },
        },

        "panel": {
            "title": "Veterinary Recommendation",
            "confidence_suffix": "confidence",
            "summary_title": "📋 Diagnosis Summary",
            "confidence_title": "📊 Classification Confidence",
            "breakdown_title": "🔎 Analysis Breakdown",
            "image_label": "🖼️ Image Analysis",
            "symptom_label": "🩺 Clinical Symptoms",
            "actions_title": "✅ Recommended Action",
            "contact_title": "📞 Veterinary Contact",
            "footer_update": "Last updated:",
        },

        "recommendation": {
            "reason_template": (
                "Image analysis showed a **{image_pct:.0f}%** probability of infection, "
                "and clinical symptom analysis showed a **{symptom_pct:.0f}%** probability of infection."
            ),
            "action_healthy": (
                "There are not enough indicators of Foot-and-Mouth Disease at this time. "
                "It is recommended to keep monitoring the animal periodically, continue "
                "hygiene and preventive isolation measures, and re-check if any new symptoms appear."
            ),
            "action_suspected": (
                "The image analysis and the symptom analysis did not agree on a single "
                "classification. This does not necessarily mean the animal has Foot-and-Mouth "
                "Disease, but it may indicate another condition with similar symptoms. It is "
                "recommended to isolate the animal from the rest of the herd as a precaution, "
                "and contact the nearest veterinary unit for a precise examination and diagnosis confirmation."
            ),
            "action_infected": (
                "Both the image analysis and the symptom analysis together strongly indicate a "
                "Foot-and-Mouth Disease infection. The animal should be isolated from the herd "
                "immediately, movement of animals in and out of the farm should be restricted, "
                "and the veterinary directorate for your governorate should be contacted urgently "
                "to take the necessary measures and limit the spread of the disease."
            ),
            "contact_found": "📞 You can contact the Veterinary Directorate in **{gov}**: {phone}",
            "contact_not_found": (
                "📞 No contact information was found for this governorate. "
                "Please contact your nearest veterinary office."
            ),
        },

        "footer": {
            "about_title": "FMD Detect",
            "about_text": (
                "An AI-assisted early screening tool for Foot-and-Mouth Disease in "
                "livestock. This is a graduation project and does not replace professional "
                "veterinary diagnosis."
            ),
            "contact_title": "Contact",
            "contact_text": "For technical support or questions about this project:",
            "email_label": "Email",
            "hotline_label": "Veterinary Hotline",
            "copyright": "© 2026 FMD Detect — Graduation Project.",
        },
    },

    "ar": {
        "dir": "rtl",
        "lang_name": "العربية",

        "nav": {
            "home": "الرئيسية",
            "about": "عن المرض",
            "tips": "نصائح",
            "diagnosis": "التشخيص",
            "results": "النتائج",
            "contact": "تواصل معنا",
            "lang_switch": "English",
        },

        "hero": {
            "title": "كشف الحمى القلاعية",
            "slogan": "\u201cثروتنا صحة حيواننا\u201d",
            "sub": "نظام كشف مبكر مدعوم بالذكاء الاصطناعى",
            "cta": "🚀 ابدأ التشخيص",
        },

        "about": {
            "title": "عن التطبيق",
            "text": (
                "FMD Detect هو أداة كشف مبكر مدعومة بالذكاء الاصطناعى، تجمع بين تحليل "
                "الصور بالتعلم العميق واستبيان الأعراض الإكلينيكية، لمساعدة المربين "
                "والأطباء البيطريين على اكتشاف الإصابة المحتملة بمرض الحمى القلاعية "
                "مبكرًا واتخاذ الإجراء المناسب بسرعة."
            ),
        },

        "tips": {
            "title": "نصائح سريعة",
            "sub": "قبل التقاط الصورة",
            "tip1_title": "نظافة ووضوح",
            "tip1_text": "تأكد من عدم وجود قش أو تبن أو طين على فم الحيوان أو حوافره قبل التقاط الصورة.",
            "tip2_title": "غسل وتجفيف",
            "tip2_text": "اغسل المنطقة المصابة برفق بماء فاتر وانتظر حتى تجف تمامًا.",
            "tip3_title": "إضاءة جيدة",
            "tip3_text": "التقط الصورة فى إضاءة جيدة، مع التأكد من عدم وجود ظلال تغطى المنطقة المصابة.",
        },

        "upload": {
            "step_badge": "الخطوة 1 من 2",
            "title": "📋 طلب تشخيص جديد",
            "subtitle": "قم برفع صور واضحة وعالية الجودة للإصابات المشتبه بها",
            "dropzone_title": "اسحب وأسقط الصور هنا",
            "dropzone_caption": "يدعم JPG وPNG وHEIC بحد أقصى 20 ميجابايت لكل صورة",
            "remove": "✕ إزالة",
            "continue": "متابعة إلى الأسئلة ⬅️",
            "continue_help": "يجب رفع صورة واحدة على الأقل أولاً",
        },

        "questions": {
            "step_badge": "الخطوة 2 من 2",
            "title": "📝 الأسئلة الإكلينيكية",
            "subtitle": "من فضلك جاوب على كل الأسئلة الآتية بدقة",
            "submit": "🔍 عرض نتيجة التشخيص",
            "back": "⬅️ رجوع لرفع الصور",
            "gov_error": "من فضلك اختر المحافظة قبل المتابعة.",
            "gov_placeholder": "اختر المحافظة",
            "yes": "نعم",
            "no": "لا",
            "fields": {
                "animal_type": "ما نوع الحيوان؟",
                "fever": "هل يعانى الحيوان من حرارة مرتفعة؟",
                "salivation": "هل يوجد سيلان لعابى مفرط؟",
                "mouth_lesions": "هل توجد تقرحات أو بثور فى الفم؟",
                "lameness": "هل الحيوان يعرج أو لا يستطيع المشى بشكل طبيعى؟",
                "hoof_lesions": "هل توجد جروح حول الحوافر أو الأطراف؟",
                "chewing_problem": "هل يواجه الحيوان صعوبة فى المضغ؟",
                "mucous_abnormal": "هل الأغشية المخاطية غير طبيعية؟",
                "skin_turgor_abnormal": "هل يوجد جفاف واضح فى الجلد (اختبار مرونة الجلد غير طبيعى)؟",
                "body_swelling": "هل يوجد أى تورم فى الجسم؟",
                "nasal_lesion": "هل توجد جروح حول الأنف؟",
                "governorate": "فى أى محافظة يتواجد الحيوان؟",
            },
            "animal_options": {
                "Cattle": "بقر / أبقار",
                "Goat": "ماعز",
                "Sheep": "خراف",
            },
        },

        "result": {
            "title": "نتيجة التشخيص",
            "status_label": "الحالة التشخيصية",
            "confidence_label": "نسبة الثقة",
            "model_meta": "🧬 الموديل: FMD-V4-Clinical",
            "last_update": "آخر تحديث:",
            "image_tag": "📷 الصورة المرفوعة",
            "new_diagnosis": "🔄 بدء تشخيص جديد",
            "bell_show": "🔔 عرض التوصية",
            "bell_hide": "🔔 إخفاء التوصية",
            "verdicts": {
                "healthy": "سليم",
                "suspected": "مشتبه به",
                "infected": "مصاب",
            },
        },

        "panel": {
            "title": "توصية الطبيب البيطرى",
            "confidence_suffix": "ثقة",
            "summary_title": "📋 ملخص التشخيص",
            "confidence_title": "📊 مستوى الثقة فى التصنيف",
            "breakdown_title": "🔎 تفصيل نتائج التحليل",
            "image_label": "🖼️ تحليل الصورة",
            "symptom_label": "🩺 الأعراض الإكلينيكية",
            "actions_title": "✅ الإجراء الموصى به",
            "contact_title": "📞 التواصل مع الطب البيطرى",
            "footer_update": "آخر تحديث:",
        },

        "recommendation": {
            "reason_template": (
                "بناءً على أن نتيجة تحليل الصورة أظهرت احتمال إصابة بنسبة **{image_pct:.0f}%**، "
                "ونتيجة تحليل الأعراض الإكلينيكية أظهرت احتمال إصابة بنسبة **{symptom_pct:.0f}%**."
            ),
            "action_healthy": (
                "لا توجد مؤشرات كافية على إصابة الحيوان بمرض الحمى القلاعية حاليًا. "
                "ينصح بمتابعة الحيوان بشكل دورى، والاستمرار فى تطبيق إجراءات النظافة والعزل الوقائى، "
                "وإعادة الفحص فى حال ظهور أى أعراض جديدة."
            ),
            "action_suspected": (
                "نتيجة تحليل الصورة ونتيجة تحليل الأعراض لم تتفقا على تصنيف واحد، وهذا لا يعنى بالضرورة الإصابة "
                "بالحمى القلاعية، لكنه قد يشير إلى مرض آخر له أعراض مشابهة. يُنصح بعزل الحيوان عن باقى القطيع "
                "كإجراء احتياطى، والتواصل مع أقرب وحدة بيطرية لإجراء فحص دقيق وتأكيد التشخيص."
            ),
            "action_infected": (
                "تشير نتائج تحليل الصورة والأعراض معًا إلى احتمال إصابة قوى بمرض الحمى القلاعية. "
                "يجب عزل الحيوان فورًا عن باقى القطيع، وتقييد حركة الحيوانات داخل وخارج المزرعة، "
                "والاتصال العاجل بمديرية الطب البيطرى التابعة لمحافظتك لاتخاذ الإجراءات اللازمة والحد من انتشار المرض."
            ),
            "contact_found": "📞 يمكنك التواصل مع مديرية الطب البيطرى فى **{gov}**: {phone}",
            "contact_not_found": (
                "📞 لم يتم العثور على بيانات اتصال لهذه المحافظة، يرجى التواصل مع أقرب مكتب للطب البيطرى التابع لمحافظتك."
            ),
        },

        "footer": {
            "about_title": "FMD Detect",
            "about_text": (
                "أداة كشف مبكر مدعومة بالذكاء الاصطناعى لمرض الحمى القلاعية فى الماشية. "
                "هذا مشروع تخرج ولا يغنى عن التشخيص البيطرى المتخصص."
            ),
            "contact_title": "تواصل معنا",
            "contact_text": "للدعم الفنى أو الاستفسارات حول هذا المشروع:",
            "email_label": "البريد الإلكترونى",
            "hotline_label": "الخط الساخن للطب البيطرى",
            "copyright": "© 2026 FMD Detect — مشروع تخرج.",
        },
    },
}


def get_translations(lang: str) -> dict:
    """Return the translation dict for `lang`, falling back to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
