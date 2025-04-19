from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.http import JsonResponse
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class ValidateSessionTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get("token")

        if not token:
            return  # No token, let user access login/signup, etc.

        try:
            # Decode token (Assuming it's a JWT)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            email = payload.get("email")

            # Check if user exists in the database
            user = User.objects.filter(id=user_id, email=email).first()

            if not user:
                return JsonResponse({"detail": "Unauthorized"}, status=401)

            request.user = user  # Attach user to request if needed

        except jwt.ExpiredSignatureError:
            messages.error(request, "Session expired, please login again.")
            return JsonResponse({"detail": "Session expired"}, status=401)
        except jwt.InvalidTokenError:
            messages.error(request, "Invalid session token.")
            return JsonResponse({"detail": "Invalid token"}, status=401)
