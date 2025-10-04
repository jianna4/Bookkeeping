from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from .chatbot.retrieval import quey_vectorstore
import requests
import os
import re

# Track user sessions with state
user_sessions = {}

EXPRESS_ORDER_ENDPOINT = "https://6051c516b18b.ngrok-free.app/twilio-callback"

@csrf_exempt
def whatsapp_chatbot(request):
    if request.method == "POST":
        try:
            user_message = request.POST.get("Body", "").strip()
            from_number = request.POST.get("From", "")
            
            print(f"📱 Received: '{user_message}' from {from_number}")

            response = MessagingResponse()

            if not user_message:
                response.message("⚠️ I didn't receive any message. Please type something.")
                return HttpResponse(str(response), content_type="application/xml")

            # Check if user is in ordering state
            if from_number in user_sessions and user_sessions[from_number] == "ordering":
                print("🛒 Processing order...")
                
                # Clear session immediately
                user_sessions.pop(from_number, None)
                
                try:
                    # Parse the order message properly
                    clean_message = user_message.split('...')[0].split('..')[0].strip()
                    normalized_message = re.sub(r'[.,;]', ',', clean_message)
                    parts = [x.strip() for x in normalized_message.split(",") if x.strip()]
                    
                    if len(parts) >= 3:
                        name, product, quantity = parts[0], parts[1], parts[2]
                        
                        # Clean quantity (remove non-digits)
                        quantity_clean = re.sub(r'[^\d]', '', quantity)
                        if not quantity_clean:
                            response.message("❗Quantity must be a number. Please send like: John, Maize Flour, 50")
                            return HttpResponse(str(response), content_type="application/xml")
                        
                        # Prepare the CORRECT payload format for Express
                        payload = {
                            "Name": name.title(),
                            "product": product.title(), 
                            "quantity": int(quantity_clean),
                            "phone": from_number.replace('whatsapp:', ''),
                            "message": user_message
                        }
                        
                        print(f"📤 Sending to Express: {EXPRESS_ORDER_ENDPOINT}")
                        print(f"📦 Corrected Payload: {payload}")
                        
                        # Send to Express endpoint
                        try:
                            express_response = requests.post(
                                EXPRESS_ORDER_ENDPOINT,
                                json=payload,
                                headers={'Content-Type': 'application/json'},
                                timeout=10
                            )
                            print(f"✅ Express response: {express_response.status_code}")
                            
                            if express_response.status_code == 200:
                                response.message("✅ Order received successfully! We'll process it shortly.")
                            else:
                                response.message("✅ Order received! We're processing it.")
                                
                        except requests.exceptions.RequestException as e:
                            print(f"❌ Express error: {e}")
                            response.message("✅ Order received! We'll process it shortly.")
                        
                    else:
                        response.message("❗Please provide: Name, Product, Quantity\nExample: John, Maize Flour, 50")
                        return HttpResponse(str(response), content_type="application/xml")
                        
                except Exception as e:
                    print(f"❌ Order parsing error: {e}")
                    response.message("❗Invalid format. Please send: Name, Product, Quantity\nExample: John, Maize Flour, 50")
                
                return HttpResponse(str(response), content_type="application/xml")

            # Start order process
            elif user_message.lower() == "order":
                print("🛒 Starting order process")
                user_sessions[from_number] = "ordering"
                response.message("🛒 Please send your order as: Name, Product, Quantity\nExample: John, Maize Flour, 50")
                return HttpResponse(str(response), content_type="application/xml")

            # === ORIGINAL CHATBOT LOGIC ===
            else:
                answer = quey_vectorstore(user_message)
                
                # Append Order Option to the chatbot response
                final_answer = f"{answer}\n\nIf you'd like to place an order, type ORDER."
                
                response.message(final_answer)
                return HttpResponse(str(response), content_type="application/xml")

        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            response = MessagingResponse()
            response.message(f"⚠️ Internal Error: {str(e)}")
            return HttpResponse(str(response), content_type="application/xml")

    return HttpResponse("Only POST requests allowed", status=405)
