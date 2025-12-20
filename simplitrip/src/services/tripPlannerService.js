
// export default tripPlannerService;


  /**
   * STAGE 3: Generate complete itinerary
   * Endpoint: /api/v1/itinerary/generate-complete
   */
  generateItinerary: async (tripDetails) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/itinerary/generate-complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripDetails)
      });
      
      if (!response.ok) {
        throw new Error(`Generation failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating itinerary:', error);
      throw error;
    }
  },

  // --- Helpers ---
        body: JSON.stringify({ question, destination })
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error querying knowledge base:', error);
      throw error;
    }
  },

  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/health`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (e) {
      return { status: "offline" };
    }
  }
};

// `tripPlannerService` is exported at the end of this file (single default export)

// -------------------------
// Chat-based flow helpers
// -------------------------
// These helpers allow the frontend to run a chat-style conversation with the
// backend LLM and request itinerary generation from the chat. The simplest
// pattern is:
// 1) call `startChat()` to get a session id (or use a random id)
// 2) call `chatMessage(sessionId, message)` for each user message
// 3) when ready, call `generateItineraryFromChat(sessionId, context)` which
//    will call the same itinerary generation endpoint but can pass conversation
//    context as part of the request.

export const startChat = async () => {
  // backend currently doesn't provide a dedicated start endpoint; frontend
  // can use a UUID as session id. We'll generate a simple timestamp id.
  return `session-${Date.now()}`;
};

export const chatMessage = async (sessionId, message) => {
  // Prefer a /chat/continue endpoint if backend implements it. Fallback to
  // using the parse-query endpoint to get an LLM reply.
  try {
    // Try chat endpoint
    const chatResp = await fetch(`${API_BASE}/api/v1/chat/continue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message })
    });

    if (chatResp.ok) return await chatResp.json();
  } catch (e) {
    // ignore and fall back
  }

  // Fallback: send message to parse-query and return parsed response as 'reply'
  try {
    const resp = await fetch(`${API_BASE}/api/v1/llm/parse-query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message })
    });
    const parsed = await resp.json();
    return { reply: parsed, parsed };
  } catch (err) {
    console.error('Chat message failed:', err);
    throw err;
  }
};

export const generateItineraryFromChat = async (sessionId, options = {}) => {
  // options is a small object that can include destination/duration/preferences
  // The backend itinerary generator expects a payload like { destination, duration, budget, travelers, preferences }
  try {
    const payload = {
      // If chat state is stored server-side, sessionId may be used to extract context.
      session_id: sessionId,
      ...options
    };

    const response = await fetch(`${API_BASE}/api/v1/itinerary/generate-complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Generation failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error generating itinerary from chat:', error);
    throw error;
  }
};

export default tripPlannerService;