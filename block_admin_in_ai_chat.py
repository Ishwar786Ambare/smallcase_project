#!/usr/bin/env python3
"""
Add is_ai_only field to ChatGroup model and update views to prevent admin interference
"""

import re

# 1. Update models.py
print("Step 1: Adding is_ai_only field to ChatGroup model...")
with open('stocks/models.py', 'r', encoding='utf-8') as f:
    models_content = f.read()

# Find the ChatGroup model and add the field
models_content = models_content.replace(
    "    avatar = models.CharField(max_length=10, default='👥')  # Emoji avatar\r\n    \r\n    def __str__(self):",
    "    avatar = models.CharField(max_length=10, default='👥')  # Emoji avatar\r\n    is_ai_only = models.BooleanField(default=False)  # True for AI-only support chats (no admin access)\r\n    \r\n    def __str__(self):"
)

with open('stocks/models.py', 'w', encoding='utf-8') as f:
    f.write(models_content)

print("✅ Added is_ai_only field to ChatGroup model")

# 2. Update views.py - modify the chat sending logic
print("\nStep 2: Updating views to check is_ai_only...")
with open('stocks/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# Find chat_send_message and add check for AI-only chats
# Insert check before admin auto-joins
old_admin_join = """            # Allow admin/staff to join support chats automatically
            if (request.user.is_staff or request.user.is_superuser) and group.group_type == 'support':
                # Auto-add admin as support member
                ChatGroupMember.objects.create(
                    group=group,
                    user=request.user,
                    role='admin'
                )
                # Add system message about support joining
                ChatMessage.objects.create(
                    group=group,
                    content=f"Support team member joined the chat",
                    message_type='system'
                )"""

new_admin_join = """            # Allow admin/staff to join support chats automatically (but NOT AI-only chats)
            if (request.user.is_staff or request.user.is_superuser) and group.group_type == 'support':
                # Check if this is an AI-only chat
                if group.is_ai_only:
                    return JsonResponse({'success': False, 'error': 'This is an AI-only support chat. Admins cannot join.'})
                
                # Auto-add admin as support member
                ChatGroupMember.objects.create(
                    group=group,
                    user=request.user,
                    role='admin'
                )
                # Add system message about support joining
                ChatMessage.objects.create(
                    group=group,
                    content=f"Support team member joined the chat",
                    message_type='system'
                )"""

views_content = views_content.replace(old_admin_join, new_admin_join)

# Also add check in chat_send_message to prevent admins from sending to AI-only chats
old_send = """        # Get or create support chat if no group specified
        if group_id:
            group = get_object_or_404(ChatGroup, id=group_id, is_active=True)
            # Verify user is member of this group
            if not ChatGroupMember.objects.filter(group=group, user=request.user, is_active=True).exists():
                return JsonResponse({'success': False, 'error': 'Not a member of this group'})
        else:
            group = get_or_create_support_chat(request.user)"""

new_send = """        # Get or create support chat if no group specified
        if group_id:
            group = get_object_or_404(ChatGroup, id=group_id, is_active=True)
            
            # Prevent admins from sending to AI-only chats
            if group.is_ai_only and (request.user.is_staff or request.user.is_superuser):
                return JsonResponse({'success': False, 'error': 'Cannot send messages to AI-only support chats'})
            
            # Verify user is member of this group
            if not ChatGroupMember.objects.filter(group=group, user=request.user, is_active=True).exists():
                return JsonResponse({'success': False, 'error': 'Not a member of this group'})
        else:
            group = get_or_create_support_chat(request.user)"""

views_content = views_content.replace(old_send, new_send)

# Filter AI-only chats from admin's support queue
old_admin_filter = """        # For admin/staff users: also show ALL support chats they can respond to
        if request.user.is_staff or request.user.is_superuser:
            support_chats = ChatGroup.objects.filter(
                group_type='support',
                is_active=True
            ).exclude(id__in=already_added_ids).order_by('-updated_at')"""

new_admin_filter = """        # For admin/staff users: also show ALL support chats they can respond to (excluding AI-only)
        if request.user.is_staff or request.user.is_superuser:
            support_chats = ChatGroup.objects.filter(
                group_type='support',
                is_active=True,
                is_ai_only=False  # Exclude AI-only chats from admin view
            ).exclude(id__in=already_added_ids).order_by('-updated_at')"""

views_content = views_content.replace(old_admin_filter, new_admin_filter)

with open('stocks/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print("✅ Updated views.py to prevent admin interference in AI chats")

# 3. Update the chat widget JavaScript to pass support type
print("\nStep 3: Updating chat widget to pass support type...")
with open('stocks/templates/stocks/_chat_widget.j2', 'r', encoding='utf-8') as f:
    widget_content = f.read()

# Add support_type parameter when sending messages
old_send_msg = """                body: JSON.stringify({
                    content: content,
                    group_id: currentGroupId
                })"""

new_send_msg = """                body: JSON.stringify({
                    content: content,
                    group_id: currentGroupId,
                    support_type: supportType  // Pass support type so backend knows if AI-only
                })"""

widget_content = widget_content.replace(old_send_msg, new_send_msg)

with open('stocks/templates/stocks/_chat_widget.j2', 'w', encoding='utf-8') as f:
    f.write(widget_content)

print("✅ Updated chat widget to pass support type")

# 4. Update get_or_create_support_chat to mark AI chats
print("\nStep 4: Updating support chat creation...")
with open('stocks/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# Find the get_or_create_support_chat function
old_create = """def get_or_create_support_chat(user):
    \"\"\"Get or create a support chat for the user\"\"\"
    # Check if user already has a support chat
    membership = ChatGroupMember.objects.filter(
        user=user,
        group__group_type='support',
        is_active=True
    ).select_related('group').first()
    
    if membership:
        return membership.group
    
    # Create a new support chat for this user
    group = ChatGroup.objects.create(
        name=f"Support Chat - {user.email}",
        group_type='support',
        created_by=user,
        avatar='👨‍💻'
    )"""

new_create = """def get_or_create_support_chat(user, is_ai_only=False):
    \"\"\"Get or create a support chat for the user\"\"\"
    # Check if user already has a support chat of this type
    membership = ChatGroupMember.objects.filter(
        user=user,
        group__group_type='support',
        group__is_ai_only=is_ai_only,  # Match same support type
        is_active=True
    ).select_related('group').first()
    
    if membership:
        return membership.group
    
    # Create a new support chat for this user
    avatar_emoji = '🤖' if is_ai_only else '👨‍💼'
    chat_type = 'AI Support' if is_ai_only else 'Human Support'
    
    group = ChatGroup.objects.create(
        name=f"{chat_type} - {user.email}",
        group_type='support',
        created_by=user,
        avatar=avatar_emoji,
        is_ai_only=is_ai_only  # Mark as AI-only if requested
    )"""

views_content = views_content.replace(old_create, new_create)

# Update calls to get_or_create_support_chat to pass support_type
old_call1 = """        else:
            group = get_or_create_support_chat(request.user)
        
        # Create message"""

new_call1 = """        else:
            # Get support_type from request (from frontend)
            support_type = data.get('support_type', 'ai')
            is_ai_only = (support_type == 'ai')
            group = get_or_create_support_chat(request.user, is_ai_only=is_ai_only)
        
        # Create message"""

views_content = views_content.replace(old_call1, new_call1)

# Update second call in chat_get_messages
old_call2 = """        else:
            group = get_or_create_support_chat(request.user)
        
        # Get messages"""

new_call2 = """        else:
            # For initial load, check localStorage preference (defaults to AI)
            # Since we can't access it server-side, default to admin support
            # The frontend will handle switching if needed
            group = get_or_create_support_chat(request.user, is_ai_only=False)
        
        # Get messages"""

views_content = views_content.replace(old_call2, new_call2)

with open('stocks/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print("✅ Updated support chat creation to use is_ai_only flag")

print("\n" + "="*60)
print("✅ ALL CHANGES COMPLETE!")
print("="*60)
print("\nWhat was done:")
print("1. Added 'is_ai_only' field to ChatGroup model")
print("2. Prevented admins from joining AI-only support chats")
print("3. Prevented admins from sending messages to AI-only chats")
print("4. Filtered AI-only chats from admin's support queue")
print("5. Updated chat creation to mark AI vs Admin support")
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate")
print("3. Restart your Django server")
print("4. Test: AI support should block admins, Admin support should allow them")
