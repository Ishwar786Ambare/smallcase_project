# Fix for ai_chat view in stocks/views.py

# REPLACE THIS (around line 1241-1245):
@login_required
def ai_chat(request):
    """API endpoint for AI-powered chat responses"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

# WITH THIS:
def ai_chat(request):
    """API endpoint for AI-powered chat responses"""
    # Check authentication - return JSON instead of redirecting
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})


# INSTRUCTIONS:
# 1. Open stocks/views.py
# 2. Go to line 1241
# 3. Remove the @login_required decorator
# 4. Add the authentication check as shown above (lines must be added after the function definition)
# 5. Save the file
# 6. The server will auto-reload
