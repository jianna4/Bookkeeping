from django.shortcuts import render

# Create your views here.
#chatbot
# views.py

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse

# === Your RAG / chatbot logic ===
def quey_vectorstore(query):
    # Replace this with your real RAG logic
    return f"🤖 AI Response for: {query}"

# === Webhook for Twilio WhatsApp ===
@csrf_exempt  # Disable CSRF for webhook (later secure with Twilio signature check)
def whatsapp_chatbot(request):
    if request.method == "POST":
        try:
            # Twilio sends data via POST form-data
            user_message = request.POST.get("Body", "").strip()    # User text
            from_number = request.POST.get("From", "")             # Example: 'whatsapp:+254712345678'
            to_number = request.POST.get("To", "")                 # Your Twilio WhatsApp number

            print("📩 Incoming WhatsApp Message:", user_message)
            print("👤 From:", from_number)
            print("📨 To (Your Bot):", to_number)

            if not user_message:
                response = MessagingResponse()
                response.message("⚠️ I didn't receive any message. Please type something.")
                return HttpResponse(str(response), content_type="application/xml")

            # Call your AI / RAG logic
            answer = quey_vectorstore(user_message)

            # Respond to WhatsApp
            response = MessagingResponse()
            response.message(answer)

            return HttpResponse(str(response), content_type="application/xml")

        except Exception as e:
            response = MessagingResponse()
            response.message(f"⚠️ Internal Error: {str(e)}")
            return HttpResponse(str(response), content_type="application/xml")

    return HttpResponse("Only POST requests allowed", status=405)
