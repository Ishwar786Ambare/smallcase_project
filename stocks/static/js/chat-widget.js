/* ========================================
   CHAT-WIDGET - JavaScript
   Extracted from _chat_widget.j2
   ======================================== */


(function() {
    // State
    let isOpen = false;
    let currentGroupId = null;
    let currentGroupType = 'support';  // Can be: 'ai_support', 'admin_support', 'group'
    let supportType = 'ai';  // 'ai' or 'admin' - tracks which support type user chose
    let selectedMembers = [];
    let socket = null;
    let reconnectAttempts = 0;
    let typingTimeout = null;
    let displayedMessageIds = new Set();  // Track displayed messages to prevent duplicates
    let isAIOnly = false;  // Track if current chat is AI-only
    
    // DOM Elements
    const container = document.getElementById('chat-widget-container');
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const minimizeBtn = document.getElementById('chat-minimize-btn');
    const chatIcon = toggleBtn.querySelector('.chat-icon');
    const closeIcon = toggleBtn.querySelector('.close-icon');
    const messagesContainer = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const unreadBadge = document.getElementById('chat-unread-badge');
    const statusIndicator = document.getElementById('chat-status');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Panels
    const groupsPanel = document.getElementById('groups-panel');
    const createGroupPanel = document.getElementById('create-group-panel');
    const membersPanel = document.getElementById('members-panel');
    
    // Buttons
    const aiToggleBtn = document.getElementById('ai-toggle-btn');
    const groupsBtn = document.getElementById('chat-groups-btn');
    const newGroupBtn = document.getElementById('chat-new-group-btn');
    const closeGroupsPanel = document.getElementById('close-groups-panel');
    const closeCreatePanel = document.getElementById('close-create-panel');
    const closeMembersPanel = document.getElementById('close-members-panel');
    const viewMembersBtn = document.getElementById('view-members-btn');
    const leaveGroupBtn = document.getElementById('leave-group-btn');
    const groupActions = document.getElementById('group-actions');
    
    // CSRF Token
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
    
    // Get API URL with language prefix to avoid redirects
    function getApiUrl(path) {
        // Get the current language prefix from the URL path (e.g., /en/, /hi/, /mr/)
        const pathParts = window.location.pathname.split('/');
        const langCode = pathParts[1]; // First part after the domain
        
        // Check if it's a valid language code (2-3 characters)
        if (langCode && langCode.length <= 3 && /^[a-z]+$/i.test(langCode)) {
            // Prepend language prefix to API path
            return `/${langCode}${path}`;
        }
        // If no language prefix detected, return path as is
        return path;
    }
    
    // WebSocket Connection
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = currentGroupId 
            ? `${protocol}//${window.location.host}/ws/chat/${currentGroupId}/`
            : `${protocol}//${window.location.host}/ws/chat/`;
        
        socket = new WebSocket(wsUrl);
        
        socket.onopen = function(e) {
            console.log('WebSocket connected');
            updateStatus('Online', 'online');
            reconnectAttempts = 0;
        };
        
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            handleSocketMessage(data);
        };
        
        socket.onclose = function(e) {
            console.log('WebSocket disconnected');
            updateStatus('Offline', 'offline');
            
            // Attempt to reconnect with exponential backoff
            if (isOpen && reconnectAttempts < 5) {
                reconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                console.log(`Reconnecting in ${delay}ms...`);
                setTimeout(connectWebSocket, delay);
            }
        };
        
        socket.onerror = function(e) {
            console.error('WebSocket error:', e);
            updateStatus('Error', 'offline');
        };
    }
    
    function handleSocketMessage(data) {
        switch(data.type) {
            case 'connection_established':
                console.log('Connection established:', data.room);
                break;
                
            case 'new_message':
                // Only add if it's not our own message (we already added it optimistically)
                if (!data.message.is_own) {
                    addMessageToUI(data.message);
                } else {
                    // It's our own message - just make sure we track the real ID
                    if (data.message.id) {
                        displayedMessageIds.add(data.message.id);
                    }
                }
                break;
                
            case 'message_sent':
                // Message was successfully saved - track the real ID
                if (data.message && data.message.id) {
                    displayedMessageIds.add(data.message.id);
                    // Also track temp_id to real id mapping
                    if (data.message.temp_id) {
                        displayedMessageIds.add(data.message.temp_id);
                    }
                }
                console.log('Message sent successfully:', data.message?.id);
                break;
                
            case 'group_joined':
                console.log('Joined group:', data.group_id);
                loadMessages();
                break;
                
            case 'typing':
                showTypingIndicator(data.username, data.is_typing);
                break;
                
            case 'error':
                console.error('Socket error:', data.message);
                break;
        }
    }
    
    function updateStatus(text, state) {
        statusIndicator.textContent = text;
        statusIndicator.className = 'status ' + state;
    }
    
    function showTypingIndicator(username, isTyping) {
        if (isTyping) {
            document.getElementById('typing-user').textContent = username;
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    }
    
    // Send typing indicator
    function sendTypingIndicator(isTyping) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'typing',
                group_id: currentGroupId,
                is_typing: isTyping
            }));
        }
    }
    
    // Show AI typing indicator
    function showAITyping() {
        document.getElementById('typing-user').textContent = 'AI Assistant';
        typingIndicator.style.display = 'block';
    }
    
    // Hide AI typing indicator
    function hideAITyping() {
        typingIndicator.style.display = 'none';
    }
    
    // Toggle Chat
    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            chatWindow.style.display = 'flex';
            chatIcon.style.display = 'none';
            closeIcon.style.display = 'block';
            
            // Load support chat based on current supportType (default to AI)
            if (!localStorage.getItem('preferredSupportType')) {
                supportType = 'ai';
                localStorage.setItem('preferredSupportType', 'ai');
            } else {
                supportType = localStorage.getItem('preferredSupportType');
            }
            
            // Update toggle button state
            updateToggleButton();
            
            loadMessages();
            setTimeout(() => chatInput.focus(), 100);
        } else {
            chatWindow.style.display = 'none';
            chatIcon.style.display = 'block';
            closeIcon.style.display = 'none';
            if (socket) {
                socket.close();
                socket = null;
            }
            closeAllPanels();
        }
    }
    
    // Load Messages via API (initial load)
    async function loadMessages() {
        try {
            const url = currentGroupId 
                ? getApiUrl(`/api/chat/messages/?group_id=${currentGroupId}`)
                : getApiUrl(`/api/chat/messages/?support_type=${supportType}`);  // Pass support type to backend
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                currentGroupId = data.group_id;
                isAIOnly = data.is_ai_only || false;  // Track if this is an AI-only chat
                console.log('💬 Loaded chat - Group ID:', currentGroupId, 'AI-only:', isAIOnly, 'Support type:', supportType);
                updateHeader(data.group_name, data.group_avatar);
                console.log('data response',data.messages)
                renderMessages(data.messages);
                
                // Connect WebSocket after we know the group
                if (socket) {
                    socket.close();
                }
                connectWebSocket();
                
                // Show group actions for group chats
                if (currentGroupType === 'group') {
                    groupActions.style.display = 'flex';
                } else {
                    groupActions.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            messagesContainer.innerHTML = '<div class="loading-messages">Failed to load messages</div>';
        }
    }
    
    // Render Messages
    function renderMessages(messages) {
        // Clear the displayed messages tracker for new conversation
        displayedMessageIds.clear();
        
        if (messages.length === 0) {
            messagesContainer.innerHTML = '<div class="message system-message"><p>No messages yet. Start the conversation!</p></div>';
            return;
        }
        
        // Track all message IDs that we're rendering
        messages.forEach(msg => {
            if (msg.id) {
                displayedMessageIds.add(msg.id);
            }
        });
        
        messagesContainer.innerHTML = messages.map(msg => createMessageHTML(msg)).join('');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function createMessageHTML(msg) {
        let className = 'message ';
        let badgeHtml = '';
        
        if (msg.message_type === 'system') {
            className += 'system-message';
        } else if (msg.is_own) {
            className += 'user-message';
        } else {
            // Check if it's an AI message or admin message
            // AI messages have sender_id = null (no user sender)
            // Admin messages have a sender (staff user)
            const isAI = !msg.sender_id || (msg.sender && (msg.sender.includes('AI') || msg.sender.includes('🤖')));
            const isAdmin = msg.sender_id && msg.sender && (msg.sender.includes('Support') || msg.sender.includes('Admin'));
            
            if (isAI) {
                className += 'ai-message';
                badgeHtml = '<span class="message-sender-badge ai-badge"><span class="badge-icon">🤖</span> AI Assistant</span>';
            } else if (isAdmin) {
                className += 'admin-message';
                badgeHtml = '<span class="message-sender-badge human-badge"><span class="badge-icon">👨‍💼</span> Support Team</span>';
            } else {
                className += 'other-message';
            }
        }
        
        let senderHtml = '';
        if (msg.message_type !== 'system' && !msg.is_own && currentGroupType === 'group') {
            senderHtml = `<span class="sender-name">${escapeHtml(msg.sender)}</span>`;
        }
        
        return `
            <div class="${className}" data-id="${msg.id}">
                ${badgeHtml}
                ${senderHtml}
                <p>${escapeHtml(msg.content)}</p>
                <span class="time">${msg.created_at}</span>
            </div>
        `;
    }
    
    function addMessageToUI(msg) {
        // Prevent duplicate messages
        const msgId = msg.id || msg.temp_id;
        if (msgId && displayedMessageIds.has(msgId)) {
            console.log('Skipping duplicate message:', msgId);
            return;
        }
        
        if (msgId) {
            displayedMessageIds.add(msgId);
        }
        
        const msgDiv = document.createElement('div');
        msgDiv.innerHTML = createMessageHTML(msg);
        messagesContainer.appendChild(msgDiv.firstElementChild);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Send Message via WebSocket
    function sendMessage(content) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Generate a temporary ID for optimistic UI update
            const tempId = 'temp_' + Date.now();
            
            socket.send(JSON.stringify({
                type: 'message',
                content: content,
                group_id: currentGroupId,
                temp_id: tempId  // Send temp ID so server can include it in response
            }));
            
            // Optimistically add message to UI with temp ID
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            addMessageToUI({
                id: tempId,  // Use temp ID so we can track it
                content: content,
                sender: 'You',
                is_own: true,
                message_type: 'text',
                created_at: time
            });
            
            // ONLY get AI response if this is an AI-only support chat
            console.log('🔍 AI Check - isAIOnly:', isAIOnly, 'supportType:', supportType, 'currentGroupType:', currentGroupType);
            if (isAIOnly && currentGroupType === 'support') {
                console.log('✅ Calling AI - conditions met!');
                getAIResponse(content);
            } else {
                console.log('❌ Skipping AI - isAIOnly:', isAIOnly, 'groupType:', currentGroupType);
                if (!isAIOnly) console.log('   Reason: Chat is not AI-only');
                if (currentGroupType !== 'support') console.log('   Reason: currentGroupType is not "support"');
            }
        } else {
            // Fallback to HTTP API if WebSocket not available
            sendMessageHTTP(content);
        }
    }
    
    // Fallback: Send Message via HTTP API
    async function sendMessageHTTP(content) {
        try {
            const response = await fetch(getApiUrl('/api/chat/send/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    content: content,
                    group_id: currentGroupId,
                    support_type: supportType  // Pass support type so backend knows if AI-only
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentGroupId = data.group_id;
                addMessageToUI(data.message);
                
                // Get AI response ONLY for AI-only support chats
                if (isAIOnly && currentGroupType === 'support') {
                    getAIResponse(content);
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
    
    // Get AI Response for support chat
    async function getAIResponse(userMessage) {
        console.log('🤖 getAIResponse called with message:', userMessage);
        try {
            // Show AI typing animation
            showAITyping();
            
            console.log('📡 Calling AI chat endpoint...');
            const response = await fetch(getApiUrl('/api/ai/chat/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });
            
            console.log('📡 Response status:', response.status);
            const data = await response.json();
            console.log('📡 Response data:', data);
            
            // Hide AI typing indicator
            hideAITyping();
            
            if (data.success && data.response) {
                console.log('✅ AI response received, saving to chat...');
                // Save AI response as a message
                const saveResponse = await fetch(getApiUrl('/api/chat/send/'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        content: data.response,
                        group_id: currentGroupId,
                        is_ai_response: true
                    })
                });
                
                const saveData = await saveResponse.json();
                console.log('💾 Save response:', saveData);
                if (saveData.success) {
                    addMessageToUI({
                        id: saveData.message.id,
                        content: data.response,
                        sender: '🤖 AI Assistant',
                        is_own: false,
                        message_type: 'text',
                        created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    });
                } else {
                    console.error('❌ Failed to save AI message:', saveData);
                }
            } else {
                console.error('❌ AI response failed or empty:', data);
            }
        } catch (error) {
            console.error('❌ Error getting AI response:', error);
            console.error('❌ Error stack:', error.stack);
            hideAITyping();
        }
    }
    
    // Update Header
    function updateHeader(name, avatar) {
        document.getElementById('chat-group-name').textContent = name || 'Support Team';
        document.getElementById('chat-avatar').textContent = avatar || '👨‍💻';
    }
    
    // Load Groups
    async function loadGroups() {
        try {
            const response = await fetch(getApiUrl('/api/chat/groups/'));
            const data = await response.json();
            
            if (data.success) {
                const groupsList = document.getElementById('groups-list');
                
                if (data.groups.length === 0) {
                    groupsList.innerHTML = '<div class="loading-messages">No groups yet. Create one!</div>';
                    return;
                }
                
                groupsList.innerHTML = data.groups.map(group => `
                    <div class="group-item" data-id="${group.id}" data-type="${group.group_type}">
                        <div class="group-avatar">${group.avatar}</div>
                        <div class="group-info">
                            <p class="group-name">${escapeHtml(group.name)}</p>
                            <p class="group-preview">${group.last_message ? escapeHtml(group.last_message) : 'No messages yet'}</p>
                        </div>
                        <div class="group-meta">
                            ${group.last_message_time ? `<span class="group-time">${group.last_message_time}</span>` : ''}
                            ${group.unread_count > 0 ? `<span class="group-unread">${group.unread_count}</span>` : ''}
                        </div>
                    </div>
                `).join('');
                
                // Add click handlers
                groupsList.querySelectorAll('.group-item').forEach(item => {
                    item.addEventListener('click', () => {
                        currentGroupId = parseInt(item.dataset.id);
                        currentGroupType = item.dataset.type;
                        closeAllPanels();
                        loadMessages();
                    });
                });
            }
        } catch (error) {
            console.error('Error loading groups:', error);
        }
    }
    
    // Create Group
    async function createGroup(name, description, avatar, memberIds) {
        try {
            const response = await fetch(getApiUrl('/api/chat/groups/create/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    avatar: avatar,
                    member_ids: memberIds
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentGroupId = data.group.id;
                currentGroupType = 'group';
                closeAllPanels();
                loadMessages();
            } else {
                alert(data.error || 'Failed to create group');
            }
        } catch (error) {
            console.error('Error creating group:', error);
        }
    }
    
    // Load Members
    async function loadMembers() {
        if (!currentGroupId) return;
        
        try {
            const response = await fetch(getApiUrl(`/api/chat/groups/members/?group_id=${currentGroupId}`));
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('members-group-name').textContent = data.group_name;
                const membersList = document.getElementById('members-list');
                
                membersList.innerHTML = data.members.map(member => `
                    <div class="member-item">
                        <div class="member-avatar">${member.username.charAt(0).toUpperCase()}</div>
                        <div class="member-info">
                            <p class="member-name">${escapeHtml(member.username)}${member.is_current_user ? ' (You)' : ''}</p>
                            <p class="member-email">${escapeHtml(member.email)}</p>
                        </div>
                        <span class="member-role">${member.role}</span>
                    </div>
                `).join('');
                
                // Show add member section for admins
                const currentUserMember = data.members.find(m => m.is_current_user);
                if (currentUserMember && ['admin', 'moderator'].includes(currentUserMember.role)) {
                    document.getElementById('add-member-section').style.display = 'flex';
                } else {
                    document.getElementById('add-member-section').style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error loading members:', error);
        }
    }
    
    // Add Member
    async function addMember(email) {
        if (!currentGroupId || !email) return;
        
        try {
            const response = await fetch(getApiUrl('/api/chat/groups/add-member/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    group_id: currentGroupId,
                    email: email
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('add-member-email').value = '';
                loadMembers();
            } else {
                alert(data.error || 'Failed to add member');
            }
        } catch (error) {
            console.error('Error adding member:', error);
        }
    }
    
    // Leave Group
    async function leaveGroup() {
        if (!currentGroupId) return;
        
        if (!confirm('Are you sure you want to leave this group?')) return;
        
        try {
            const response = await fetch(getApiUrl('/api/chat/groups/leave/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    group_id: currentGroupId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentGroupId = null;
                currentGroupType = 'support';
                loadMessages();
            } else {
                alert(data.error || 'Failed to leave group');
            }
        } catch (error) {
            console.error('Error leaving group:', error);
        }
    }
    
    // Search Users
    async function searchUsers(query) {
        if (query.length < 2) {
            document.getElementById('search-results').innerHTML = '';
            return;
        }
        
        try {
            const response = await fetch(getApiUrl(`/api/chat/users/search/?q=${encodeURIComponent(query)}`));
            const data = await response.json();
            
            if (data.success) {
                const resultsDiv = document.getElementById('search-results');
                
                const filteredUsers = data.users.filter(u => !selectedMembers.some(m => m.id === u.id));
                
                resultsDiv.innerHTML = filteredUsers.map(user => `
                    <div class="search-result-item" data-id="${user.id}" data-email="${user.email}" data-username="${user.username}">
                        ${escapeHtml(user.username)} (${escapeHtml(user.email)})
                    </div>
                `).join('');
                
                resultsDiv.querySelectorAll('.search-result-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const user = {
                            id: parseInt(item.dataset.id),
                            email: item.dataset.email,
                            username: item.dataset.username
                        };
                        selectedMembers.push(user);
                        renderSelectedMembers();
                        document.getElementById('member-search').value = '';
                        resultsDiv.innerHTML = '';
                    });
                });
            }
        } catch (error) {
            console.error('Error searching users:', error);
        }
    }
    
    // Render Selected Members
    function renderSelectedMembers() {
        const container = document.getElementById('selected-members');
        container.innerHTML = selectedMembers.map(m => `
            <div class="selected-member" data-id="${m.id}">
                ${escapeHtml(m.username)}
                <span class="remove-member" data-id="${m.id}">✕</span>
            </div>
        `).join('');
        
        container.querySelectorAll('.remove-member').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                selectedMembers = selectedMembers.filter(m => m.id !== id);
                renderSelectedMembers();
            });
        });
    }
    
    // Close All Panels
    function closeAllPanels() {
        groupsPanel.style.display = 'none';
        createGroupPanel.style.display = 'none';
        membersPanel.style.display = 'none';
    }
    
    // Update Toggle Button State
    function updateToggleButton() {
        if (supportType === 'admin') {
            aiToggleBtn.classList.add('active');
        } else {
            aiToggleBtn.classList.remove('active');
        }
    }
    
    // Toggle Support Type
    function toggleSupportType() {
        console.log('🔄 Toggling support type from:', supportType);
        // Toggle between ai and admin
        supportType = supportType === 'ai' ? 'admin' : 'ai';
        console.log('✅ New support type:', supportType);
        
        localStorage.setItem('preferredSupportType', supportType);
        currentGroupId = null;
        isAIOnly = false;  // Reset AI-only flag when switching
        
        // Update UI
        if (supportType === 'ai') {
            updateHeader('AI Assistant', '🤖');
        } else {
            updateHeader('Human Support', '👨‍💼');
        }
        
        updateToggleButton();
        closeAllPanels();
        loadMessages();
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Event Listeners
    toggleBtn.addEventListener('click', toggleChat);
    minimizeBtn.addEventListener('click', toggleChat);
    
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            sendMessage(text);
            chatInput.value = '';
            sendTypingIndicator(false);
        }
    });
    
    // Typing indicator on input
    chatInput.addEventListener('input', () => {
        sendTypingIndicator(true);
        
        // Clear previous timeout
        if (typingTimeout) {
            clearTimeout(typingTimeout);
        }
        
        // Stop typing after 2 seconds of no input
        typingTimeout = setTimeout(() => {
            sendTypingIndicator(false);
        }, 2000);
    });
    
    groupsBtn.addEventListener('click', () => {
        closeAllPanels();
        groupsPanel.style.display = 'flex';
        loadGroups();
    });
    
    newGroupBtn.addEventListener('click', () => {
        closeAllPanels();
        createGroupPanel.style.display = 'flex';
        selectedMembers = [];
        renderSelectedMembers();
    });
    
    closeGroupsPanel.addEventListener('click', () => {
        groupsPanel.style.display = 'none';
    });
    
    
    // Toggle Support Type Event Listener
    aiToggleBtn.addEventListener('click', toggleSupportType);


    closeCreatePanel.addEventListener('click', () => {
        createGroupPanel.style.display = 'none';
    });
    
    closeMembersPanel.addEventListener('click', () => {
        membersPanel.style.display = 'none';
    });
    
    viewMembersBtn.addEventListener('click', () => {
        closeAllPanels();
        membersPanel.style.display = 'flex';
        loadMembers();
    });
    
    leaveGroupBtn.addEventListener('click', leaveGroup);
    
    document.getElementById('add-member-btn').addEventListener('click', () => {
        const email = document.getElementById('add-member-email').value.trim();
        if (email) {
            addMember(email);
        }
    });
    
    document.getElementById('create-group-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('new-group-name').value.trim();
        const description = document.getElementById('new-group-description').value.trim();
        const avatar = document.getElementById('new-group-avatar').value;
        const memberIds = selectedMembers.map(m => m.id);
        
        if (name) {
            createGroup(name, description, avatar, memberIds);
        }
    });
    
    document.getElementById('member-search').addEventListener('input', (e) => {
        searchUsers(e.target.value);
    });
})();
