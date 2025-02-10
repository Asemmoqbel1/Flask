from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# تهيئة عميل OpenAI مع OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# تخزين تاريخ المحادثة
conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "الرسالة مطلوبة"}), 400

    # إضافة رسالة المستخدم إلى تاريخ المحادثة
    conversation_history.append({"role": "user", "content": user_message})

    try:
        # تحليل السؤال باستخدام نموذج لغة
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي متخصص في موضوع الدم وبنك الدم والتبرعات بالدم. يجب أن تجيب فقط على الأسئلة المتعلقة بالدم (مثل تعريفه، مكوناته، وظائفه، الأمراض المتعلقة به) أو بنك الدم (مثل كيفية عمله، أهمية التبرع بالدم) أو التبرعات بالدم (مثل شروط التبرع، فوائد التبرع، أنواع التبرع) أو التوعية الصحية المتعلقة بالدم. إذا كان السؤال خارج هذا السياق، قل 'عذرًا، لا يمكنني الإجابة على هذا السؤال.'"},
                {"role": "user", "content": f"السؤال: {user_message}\n\nالرجاء الإجابة فقط إذا كان السؤال متعلقًا بالدم أو بنك الدم أو التبرعات بالدم أو التوعية الصحية المتعلقة بالدم."},
                *conversation_history,  # إضافة تاريخ المحادثة
            ],
            max_tokens=300,  # زيادة عدد الكلمات للإجابات الأكثر تفصيلاً
            temperature=0  # لجعل الإجابات أكثر دقة
        )

        if completion and completion.choices:
            response = completion.choices[0].message.content

            # تحقق إضافي: إذا كانت الإجابة تحتوي على "لا أعرف" أو "لا يمكنني الإجابة"، نعيد رسالة محددة
            if "لا أعرف" in response or "لا يمكنني الإجابة" in response:
                response = "عذرًا، لا يمكنني الإجابة على هذا السؤال."

            # إضافة رد المساعد إلى تاريخ المحادثة
            conversation_history.append({"role": "assistant", "content": response})
            return jsonify({"response": response})
        else:
            return jsonify({"error": "لم يتم استلام أي رد من المساعد"}), 500

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)