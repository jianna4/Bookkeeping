from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import json
from .utils import analyze_sales, suggest_price, plot_sales, plot_predicted_week

LAST_ANALYSIS = {}  # cache results

CSV_PATH = r"F:\projects\Bookkeeping\Backend\project\app\sales_data.csv"

@csrf_exempt
def analyze_view(request):
    if request.method == "POST":
        try:
            # ✅ Pass the CSV path directly to analyze_sales
            results = analyze_sales(CSV_PATH)  # <-- This is correct
            global LAST_ANALYSIS
            LAST_ANALYSIS = results

            return JsonResponse({
                "slope": float(results["slope"]),
                "intercept": float(results["intercept"]),
                "r2": float(results["r2"]),
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def price_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            base_price = float(body.get("base_price", 100))

            if not LAST_ANALYSIS:
                return JsonResponse({"error": "Run /analyze/ first"}, status=400)

            slope = LAST_ANALYSIS["slope"]
            suggested = suggest_price(base_price, slope)

            return JsonResponse({
                "slope": slope,
                "base_price": base_price,
                "suggested_price": suggested,
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Only POST allowed"}, status=405)


def plot_trend_view(request):
    if not LAST_ANALYSIS:
        return JsonResponse({"error": "Run /analyze/ first"}, status=400)

    img = plot_sales(
        LAST_ANALYSIS["df"],
        LAST_ANALYSIS["fitted_line"],
        LAST_ANALYSIS["future_dates"],
        LAST_ANALYSIS["predicted_future"],
    )
    return JsonResponse({"plot": img})


def plot_forecast_view(request):
    if not LAST_ANALYSIS:
        return JsonResponse({"error": "Run /analyze/ first"}, status=400)

    img = plot_predicted_week(
        LAST_ANALYSIS["future_dates"],
        LAST_ANALYSIS["predicted_future"],
    )
    return JsonResponse({"plot": img})


@csrf_exempt
def revenue_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            base_price = float(body.get("base_price", 0))

            if not LAST_ANALYSIS:
                return JsonResponse({"error": "Run /analyze/ first"}, status=400)

            slope = LAST_ANALYSIS["slope"]
            suggested = suggest_price(base_price, slope)
            predicted_future = LAST_ANALYSIS["predicted_future"]

            revenue_base = float(np.sum(predicted_future) * base_price)
            revenue_suggested = float(np.sum(predicted_future) * suggested)

            return JsonResponse({
                "base_price": base_price,
                "suggested_price": suggested,
                "revenue_base_price": round(revenue_base, 2),
                "revenue_suggested_price": round(revenue_suggested, 2),
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Only POST allowed"}, status=405)


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
