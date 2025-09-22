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
