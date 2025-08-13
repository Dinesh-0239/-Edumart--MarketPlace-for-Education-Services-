import uuid
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.backends.db import SessionStore

class UniqueSessionMiddleware(MiddlewareMixin):
    """Handles per-tab sessions and server-restart invalidation"""

    def process_request(self, request):
        # Get or generate Tab ID
        tab_id = request.COOKIES.get('edumart_tab_id') 
        is_new_tab = False
        
        if not tab_id:
            tab_id = str(uuid.uuid4())
            is_new_tab = True
        
        request.edumart_tab_id = tab_id  # Attach to request

        # Get session key for this tab
        session_key = request.get_signed_cookie(
            f'edumart_session_{tab_id}',
            default=None,
            salt=settings.SESSION_COOKIE_SECRET
        )

        # Validate session
        valid_session = False
        if session_key:
            session = SessionStore(session_key=session_key)
            if session.exists(session_key):
                # Check server secret match
                if session.get('server_secret') == settings.SESSION_COOKIE_SECRET:
                    request.session = session
                    valid_session = True
        
        # Create new session if invalid
        if not valid_session:
            request.session = SessionStore()
            request.session.create()
            request.session['server_secret'] = settings.SESSION_COOKIE_SECRET
            request.session.save()
            if session_key:
                SessionStore(session_key=session_key).delete()  # Delete old session

        request.is_new_tab = is_new_tab  # Flag for response


    def process_response(self, request, response):
        tab_id = getattr(request, 'edumart_tab_id', None)
        
        if tab_id and hasattr(request, 'session'):
            # Set/Update Tab ID cookie
            if getattr(request, 'is_new_tab', False):
                response.set_cookie(
                    'edumart_tab_id',
                    tab_id,
                    max_age=settings.SESSION_COOKIE_AGE,
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
            
            # Set session cookie for this tab
            response.set_signed_cookie(
                f'edumart_session_{tab_id}',
                request.session.session_key,
                salt=settings.SESSION_COOKIE_SECRET,
                max_age=settings.SESSION_COOKIE_AGE,
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE
            )
        
        return response