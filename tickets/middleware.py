import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache

RATE_LIMIT = 60  # requests per minute

class IdempotencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST':
            key = request.headers.get('Idempotency-Key')
            if not key:
                return None
            uid = request.user.id if getattr(request, 'user', None) and request.user.is_authenticated else request.META.get('REMOTE_ADDR')
            cache_key = f"idem:{uid}:{key}"
            data = cache.get(cache_key)
            if data:
                # data stored as dict with 'status' and 'body'
                try:
                    import json
                    body = json.loads(data['body'])
                    return JsonResponse(body, status=data.get('status',200))
                except Exception:
                    return JsonResponse({'result': data['body']}, status=data.get('status',200))
            request._idem_cache_key = cache_key

    def process_response(self, request, response):
        key = getattr(request, '_idem_cache_key', None)
        if key and response.status_code in (200,201):
            cache.set(key, {'status': response.status_code, 'body': response.content.decode('utf-8')}, 60*60)
        return response

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        uid = user.id if user.is_authenticated else request.META.get('REMOTE_ADDR')
        key = f"rate:{uid}:{int(time.time()//60)}"
        count = cache.get(key, 0)
        if count >= RATE_LIMIT:
            return JsonResponse({'error': {'code': 'RATE_LIMIT'}}, status=429)
        cache.set(key, count+1, 61)
