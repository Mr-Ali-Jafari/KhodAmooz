import json
import streamlit as st
from modules.sentence_analysis import analyze_sentence
import language_tool_python
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
import matplotlib.pyplot as plt

st.markdown("""
<style>
/* Persian/Arabic font from CDN */
@font-face {2
    font-family: 'Vazir';
    src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.woff') format('woff');
    font-display: swap;
    font-weight: normal;
    font-style: normal;
}

.ltr-text {
    font-family: 'Roboto', Consolas, monospace, Arial, sans-serif !important;
}

.main-container {
  direction: rtl !important;
  unicode-bidi: embed !important;
  font-family: 'Vazir', Tahoma, Arial, sans-serif !important;
  background-color: #f8f9fa;
  color: #333;
  line-height: 1.6;
  padding: 10px;
}

.title-container {
  text-align: center;
  margin-bottom: 30px;
}

.header-container {
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  margin-top: 25px;
  margin-bottom: 20px;
  color: #007bff;
}

.rule-container {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.example-container {
  margin-right: 20px;
  margin-top: 10px;
}

.exercise-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  color: black;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.input-container {
  margin-top: 20px;
  margin-bottom: 20px;
}

.button-container {
  text-align: left;
  margin-bottom: 20px;
}

.result-container {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #ddd;
  color:black;
}

.analysis-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0;
  margin: 15px 0;
  background: white;
  direction: rtl;
  font-size: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  border-radius: 12px 12px 0 0;
  overflow: hidden;
}

.analysis-table th, 
.analysis-table td {
  border-bottom: 1px solid #e0e0e0 !important;
  padding: 14px 10px !important;
  text-align: center;
}

.analysis-table th {
  background-color: #0097a7 !important;
  color: white !important;
  font-weight: bold;
  border-bottom: 2px solid #007bff !important;
}

.analysis-table tr:last-child td {
  border-bottom: none !important;
}

.analysis-table tr:hover td {
  background-color: #f1f8ff !important;
}

.analysis-table th:nth-child(1),
.analysis-table td:nth-child(1),
.analysis-table th:nth-child(2),
.analysis-table td:nth-child(2),
.analysis-table th:nth-child(3),
.analysis-table td:nth-child(3) {
  width: 33.33%;
}

.analysis-table .ltr-text {
  direction: ltr;
  text-align: center;
  font-family: 'Roboto', Consolas, monospace, Arial, sans-serif;
}

.analysis-table .rtl-text {
  direction: rtl;
  text-align: right;
  font-family: 'Vazir', Tahoma, Arial, sans-serif;
}

.grammar-suggestion {
  direction: ltr;
  text-align: left;
  font-family: 'Roboto', monospace;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  margin: 10px 0;
  border-right: 4px solid #007bff;
}

.grammar-suggestion .error {
  color: #dc3545;
  font-weight: bold;
}

.grammar-suggestion .message {
  color: #6c757d;
}

.grammar-suggestion .original {
  color: #343a40;
}

.grammar-suggestion .correction {
  color: #28a745;
  font-weight: bold;
}

.grammar-suggestion .divider {
  border-top: 1px dashed #ccc;
  margin: 8px 0;
}

.rtl-text {
  direction: rtl !important;
  text-align: right !important;
  unicode-bidi: embed !important;
  
}

.ltr-text {
  direction: ltr !important;
  text-align: left !important;
  unicode-bidi: embed !important;
  font-family: 'Roboto', Consolas, monospace, Arial, sans-serif !important;
  display: inline-block;
}

.warning-container {
  color: #856404;
  background-color: #fff3cd;
  border-color: #ffeeba;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.divider-container {
  border-top: 1px solid #ddd;
  margin: 30px 0;
}
</style>
""", unsafe_allow_html=True)

def load_grammar_rules():
    with open("rules/grammar_rules.json", encoding="utf-8") as f:
        return json.load(f)

def load_exercises():
    with open("rules/exercises.json", encoding="utf-8") as f:
        return json.load(f)

def grammar_check(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    if not matches:
        return "No grammar errors found."
    results = []
    for match in matches:
        error_info = {
            'message': match.message,
            'context': match.context,
            'offset': match.offset,
            'replacements': match.replacements
        }
        results.append(error_info)
    return results

def translate_to_farsi(text):
    return GoogleTranslator(source='en', target='fa').translate(text)

def smart_feedback(grammar_results):
    common_errors = {
        'subject-verb agreement': 'به تطابق فاعل و فعل دقت کن.',
        'article': 'استفاده از a/an/the را بررسی کن.',
        'tense': 'زمان فعل را بررسی کن.',
        'spelling': 'املای کلمات را بررسی کن.'
    }
    feedbacks = []
    for error in grammar_results:
        for key in common_errors:
            if key in error['message'].lower():
                feedbacks.append(common_errors[key])
    return list(set(feedbacks))

def save_history(user_sentence, grammar_result, analysis, score):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    st.session_state['history'].append({
        'sentence': user_sentence,
        'grammar': grammar_result,
        'analysis': analysis,
        'score': score
    })

def show_history():
    if 'history' in st.session_state and st.session_state['history']:
        st.markdown('<div class="header-container rtl-text"><h3>تاریخچه تمرینات شما</h3></div>', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state['history']):
            st.markdown(f"<div class='result-container rtl-text'><b>جمله:</b> {item['sentence']}<br><b>امتیاز:</b> {item['score']}</div>", unsafe_allow_html=True)

def calculate_score(grammar_result):
    if isinstance(grammar_result, str):
        return 100
    else:
        errors = len(grammar_result)
        score = max(0, 100 - errors * 20)
        return score

def get_level(score):
    if score >= 90:
        return 'عالی'
    elif score >= 70:
        return 'خوب'
    elif score >= 50:
        return 'متوسط'
    else:
        return 'نیاز به تمرین بیشتر'

def suggest_exercise(history, exercises):
    if not history:
        return exercises[0]
    if history[-1]['score'] < 70:
        return next((ex for ex in exercises if ex['id'] == history[-1]['sentence']), exercises[0])
    last_id = history[-1]['sentence']
    for i, ex in enumerate(exercises):
        if ex['id'] == last_id and i+1 < len(exercises):
            return exercises[i+1]
    return exercises[0]

def play_tts(text, lang, filename):
    if not text or text.strip() == "":
        return
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    audio_file = open(filename, 'rb')
    st.audio(audio_file.read(), format='audio/mp3')
    audio_file.close()
    os.remove(filename)

def show_progress_chart():
    if 'history' in st.session_state and st.session_state['history']:
        scores = [item['score'] for item in st.session_state['history']]
        plt.figure(figsize=(5,2))
        plt.plot(scores, marker='o')
        plt.title('Score Progress Chart')
        plt.xlabel('Exercise')
        plt.ylabel('Score')
        st.pyplot(plt)

def show_quiz():
    st.markdown('<div class="header-container rtl-text"><h3>آزمون کوتاه</h3></div>', unsafe_allow_html=True)
    questions = [
        {'q': 'کدام جمله صحیح است؟', 'options': ['He go to school.', 'He goes to school.'], 'a': 1},
        {'q': 'کدام گزینه فعل است؟', 'options': ['quickly', 'run'], 'a': 1},
    ]
    score = 0
    for i, q in enumerate(questions):
        st.write(f"{i+1}. {q['q']}")
        answer = st.radio("انتخاب کنید:", q['options'], key=f'quiz_{i}')
        if answer == q['options'][q['a']]:
            score += 1
    if st.button('ثبت پاسخ آزمون'):
        st.success(f'امتیاز شما در آزمون: {score} از {len(questions)}')

grammar_rules = load_grammar_rules()
exercises = load_exercises()

st.set_page_config(page_title="دستیار یادگیری خودآموز", layout="centered")
st.markdown('<div class="title-container rtl-text"><h1>دستیار هوشمند یادگیری خودآموز</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="header-container rtl-text"><h2>قوانین گرامری</h2></div>', unsafe_allow_html=True)
for rule in grammar_rules:
    with st.expander(f"{rule['id']}. {rule['title']}"):
        st.markdown(f'<div class="rule-container rtl-text">{rule["description"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="rtl-text"><strong>مثال‌ها:</strong></div>', unsafe_allow_html=True)
        for ex in rule['examples']:
            st.markdown(f'<div class="example-container rtl-text">- {ex["sentence"]}  |  توضیح: {ex["explanation"]}</div>', unsafe_allow_html=True)
st.markdown('<div class="divider-container"></div>', unsafe_allow_html=True)
st.markdown('<div class="header-container rtl-text"><h2>تمرین‌های ترجمه و گرامر</h2></div>', unsafe_allow_html=True)
exercise_ids = [ex["id"] for ex in exercises]
selected_id = st.selectbox(' یک تمرین انتخاب کنید:', exercise_ids, key='exercise_select')
selected_ex = next((ex for ex in exercises if ex["id"] == selected_id), None)
if selected_ex:
    st.markdown(f'<div class="exercise-container rtl-text"><strong>جمله فارسی:</strong> {selected_ex["fa"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="exercise-container rtl-text"><strong>ترجمه انگلیسی (نمونه):</strong> {selected_ex["en"]}</div>', unsafe_allow_html=True)
    related_rule = next((r for r in grammar_rules if r["id"] == selected_ex["grammar_id"]), None)
    if related_rule:
        st.markdown(f'<div class="rtl-text"><strong>قانون گرامری مرتبط:</strong> {related_rule["title"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-container rtl-text"><strong>جمله انگلیسی خود را وارد کنید و سپس بررسی گرامری را بزنید:</strong></div>', unsafe_allow_html=True)
    user_sentence = st.text_area("Enter your English sentence", key="user_sentence", label_visibility="collapsed")
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("بررسی گرامر و تحلیل جمله"):
        st.markdown('</div>', unsafe_allow_html=True)
        if user_sentence.strip() == "":
            st.markdown('<div class="warning-container rtl-text">لطفاً جمله‌ای وارد کنید.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="result-container rtl-text" style="color:black;"><h3>نتیجه بررسی گرامر</h3></div>', unsafe_allow_html=True)
            results = grammar_check(user_sentence)
            if isinstance(results, str):
                st.success(results)
            else:
                for error in results:
                    st.markdown(f"""
                    <div class="grammar-suggestion">
                        <div class="error">Error: نیاز به اصلاح</div>
                        <div class="message">پیغام: {error['message']}</div>
                        <div class="original">درمتن: {error['context']}</div>
                        <div class="divider"></div>
                        <div class="correction">پیشنهاد: {', '.join(error['replacements'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('<div class="result-container rtl-text" style="color:black;"><h3>تحلیل نقش دستوری کلمات</h3></div>', unsafe_allow_html=True)
            analysis = analyze_sentence(user_sentence)
            pos_explanation = {
                "VERB": "فعل (Verb)",
                "NOUN": "اسم (Noun)",
                "ADJ": "صفت (Adjective)",
                "ADV": "قید (Adverb)",
                "PRON": "ضمیر (Pronoun)",
                "DET": "حروف تعریف (Determiner)",
                "ADP": "حروف اضافه (Preposition)",
                "CONJ": "حروف ربط (Conjunction)",
                "NUM": "عدد (Numeral)",
                "PART": "حروف ربط (Particle)",
                "INTJ": "حروف ندا (Interjection)",
                "PROPN": "اسم خاص (Proper Noun)"
            }
            st.markdown("""
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th class="rtl-text">کلمه</th>
                        <th class="rtl-text">نقش دستوری</th>
                        <th class="rtl-text">توضیح نقش</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            for token in analysis:
                explanation = pos_explanation.get(token["pos"], "نامشخص")
                st.markdown(f"""
                  <table style="width: 100%; margin: auto;">
                      <tr>
                          <td style="width: 33.3%; text-align: left;">{token["word"]}</td>
                          <td style="width: 33.3%; text-align: center;">{token["pos"]}</td>
                          <td style="width: 33.3%; text-align: right;">{explanation}</td>
                      </tr>
                  </table>
                """, unsafe_allow_html=True)
            st.markdown("""
                </tbody>
            </table>
            """, unsafe_allow_html=True)
            st.markdown('<div class="result-container rtl-text"><b>ترجمه خودکار جمله شما:</b></div>', unsafe_allow_html=True)
            st.info(translate_to_farsi(user_sentence))
            st.markdown('<div class="result-container rtl-text"><b>تلفظ انگلیسی:</b></div>', unsafe_allow_html=True)
            play_tts(user_sentence, 'en', 'en.mp3')
            st.markdown('<div class="result-container rtl-text"><b>بازخورد هوشمند:</b></div>', unsafe_allow_html=True)
            feedbacks = smart_feedback(results) if not isinstance(results, str) else []
            for fb in feedbacks:
                st.warning(fb)
            score = calculate_score(results)
            level = get_level(score)
            st.markdown(f'<div class="result-container rtl-text"><b>امتیاز شما:</b> {score} / 100  |  <b>سطح:</b> {level}</div>', unsafe_allow_html=True)
            save_history(user_sentence, results, analysis, score)
            show_progress_chart()
            st.markdown('<div class="result-container rtl-text"><b>پیشنهاد تمرین بعدی:</b></div>', unsafe_allow_html=True)
            suggested = suggest_exercise(st.session_state.get('history', []), exercises)
            st.info(f"{suggested['fa']} (ترجمه نمونه: {suggested['en']})")
            show_history()
    show_quiz()