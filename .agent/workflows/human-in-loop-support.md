---
description: Human-in-the-Loop (HITL) Chat Support System
---

# Human-in-the-Loop Support Implementation Plan

## Overview
This document outlines the strategy for implementing a hybrid AI + Human support system that intelligently routes conversations between AI assistants and human support agents.

## 1. When to Transfer from AI to Human Support

### Automatic Triggers (System-Initiated Transfer)
The system should automatically escalate to human support when:

1. **Sentiment Analysis Detects Frustration**
   - User uses words like: "frustrated", "angry", "terrible", "awful", "useless"
   - Multiple repeated questions (AI failed to resolve)
   - High negative sentiment score

2. **AI Confidence is Low**
   - AI explicitly says "I don't know"
   - AI encounters errors (API failures, database errors)
   - Query is outside AI's domain knowledge

3. **Explicit Transfer Request**
   - User types: "talk to human", "speak to agent", "real person", "human support"
   - User clicks "Transfer to Human" button

4. **Complex Scenarios**
   - Account security issues (password reset, suspicious activity)
   - Financial transactions or withdrawals
   - Legal/compliance questions
   - Technical bugs or platform errors

5. **Time-Based Escalation**
   - Conversation exceeds 10 messages without resolution
   - User returns to support within 1 hour (indicating unresolved issue)

### User-Initiated Transfer (Manual)
Users can request human support at any time by:
- Clicking a "Talk to Human Agent" button
- Typing explicit keywords
- Selecting from a menu option

## 2. Database Schema Changes

Add the following fields to your existing models:

### ChatGroup Model Additions
```python
# Support-specific fields
assigned_agent = models.ForeignKey(
    User, 
    on_delete=models.SET_NULL,
    null=True, 
    blank=True,
    related_name='assigned_support_chats',
    limit_choices_to={'is_staff': True}
)
support_status = models.CharField(
    max_length=20,
    choices=[
        ('ai', 'AI Handling'),
        ('waiting', 'Waiting for Agent'),
        ('active', 'Agent Active'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ],
    default='ai'
)
ai_handoff_reason = models.TextField(blank=True)  # Why it was escalated
ai_handoff_at = models.DateTimeField(null=True, blank=True)
priority = models.CharField(
    max_length=10,
    choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ],
    default='medium'
)
requires_human = models.BooleanField(default=False)
sentiment_score = models.FloatField(default=0.0)  # -1 to 1
```

### ChatMessage Model Additions
```python
# Track who sent it: AI or Human
sender_type = models.CharField(
    max_length=10,
    choices=[
        ('user', 'User'),
        ('ai', 'AI Assistant'),
        ('agent', 'Human Agent'),
        ('system', 'System')
    ],
    default='user'
)
ai_confidence = models.FloatField(null=True, blank=True)  # 0 to 1
requires_followup = models.BooleanField(default=False)
```

## 3. Implementation Components

### A. Sentiment Analysis Module
Create `stocks/sentiment_analyzer.py`:
- Detect user frustration/satisfaction
- Score messages from -1 (very negative) to +1 (very positive)
- Use simple keyword matching or integrate TextBlob/VADER

### B. Escalation Manager
Create `stocks/escalation_manager.py`:
- Evaluate if conversation needs human intervention
- Apply escalation rules
- Handle transfer logic

### C. Agent Dashboard
New admin interface for support agents:
- View all pending support requests
- See AI conversation history
- Take over conversations
- Mark as resolved

### D. Modified AI Service
Update `ai_service.py`:
- Check if conversation needs escalation
- Track AI confidence scores
- Detect trigger keywords

### E. WebSocket Updates
Update `consumers.py`:
- Notify agents when new support request arrives
- Real-time agent assignment notifications
- Status updates

## 4. User Experience Flow

### Flow 1: AI Successfully Resolves Issue
```
User: "How's my portfolio doing?"
  ↓
AI: [Provides portfolio summary]
  ↓
User: "Thanks!"
  ↓
Status: RESOLVED (stays with AI)
```

### Flow 2: AI Escalates to Human
```
User: "I deposited money but it's not showing!"
  ↓
AI: [Detects financial transaction + frustration]
  ↓
System: Auto-escalate to WAITING
  ↓
User sees: "Connecting you to a human agent..."
  ↓
Agent joins chat
  ↓
Agent: "Hi! I'm Sarah, I'll help you with this."
  ↓
Status: ACTIVE (human handling)
  ↓
Issue resolved
  ↓
Agent marks as RESOLVED
```

### Flow 3: User Requests Human Explicitly
```
User: "I want to talk to a real person"
  ↓
UI shows button: "Transfer to Human Agent"
  ↓
User clicks button
  ↓
Status: WAITING → Agent assigned → ACTIVE
```

## 5. Agent Notification System

When escalation occurs:
1. **Dashboard Badge**: Red notification count
2. **Email Alert**: For high-priority issues
3. **Browser Notification**: If agent is online
4. **Slack/Discord Webhook**: Optional integration

## 6. Monitoring & Analytics

Track the following metrics:
- **AI Resolution Rate**: % of chats resolved without human
- **Average Time to Escalation**: How long before AI gives up
- **Escalation Reasons**: Which triggers are most common
- **Agent Response Time**: How fast humans respond
- **Customer Satisfaction**: Post-chat survey scores

## 7. AI Training Feedback Loop

After human resolves an issue:
- Agent can mark "AI should have handled this"
- System logs the conversation for AI improvement
- Periodic review to update AI knowledge base

## 8. Graceful Handoff Message Templates

When transferring to human:
```
AI: "I understand this is important to you. Let me connect you 
     with one of our support specialists who can better assist 
     you with [ISSUE TYPE]. Please hold on for a moment..."
```

When agent joins:
```
System: "🙋 Sarah (Support Agent) has joined the chat"
Agent: "Hi [User Name]! I've reviewed your conversation with our 
       AI assistant. I'm here to help you with [ISSUE]. Let's 
       get this sorted out!"
```

## 9. Working Hours & Offline Support

### During Business Hours (e.g., 9 AM - 6 PM)
- Human agents available
- Real-time transfer possible
- Target response: < 2 minutes

### Outside Business Hours
- AI handles everything
- Option: "Leave a message for our team"
- Agents respond when online
- Auto-reply: "Our team will respond within X hours"

## 10. Priority Queue for Agents

Support requests appear in order of:
1. **Urgent** (security/financial issues)
2. **High** (frustrated users, repeated contact)
3. **Medium** (general escalations)
4. **Low** (optional human review)

## Implementation Phases

### Phase 1: Basic Infrastructure (Week 1)
- Add database fields
- Create escalation triggers
- Simple keyword detection

### Phase 2: Agent Dashboard (Week 2)
- Build support queue UI
- Agent can view and claim chats
- Real-time updates via WebSocket

### Phase 3: Smart Escalation (Week 3)
- Sentiment analysis
- AI confidence tracking
- Automated prioritization

### Phase 4: Analytics & Optimization (Week 4)
- Build reporting dashboard
- A/B test escalation thresholds
- Feedback loops

---

## Quick Start: Minimum Viable HITL

If you want to start simple:

1. **Add one field**: `requires_human` to ChatGroup
2. **Add one button**: "Request Human Support"
3. **Build simple queue**: Admin page showing all `requires_human=True` chats
4. **Manual assignment**: Admin clicks "Take Over" button

This gives you 80% of the value with 20% of the complexity!
