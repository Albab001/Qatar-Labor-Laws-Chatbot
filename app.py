"""
Qatar Labor Laws RAG Chatbot - Hugging Face Spaces Deployment
Main entry point for the application
"""

import asyncio
import json
import os
import gradio as gr
from mcp import ClientSession
from mcp.client.sse import sse_client

# Your n8n MCP endpoint - Can be overridden by environment variable
MCP_URL = os.getenv(
    "MCP_URL",
    "https://albabnawaz.app.n8n.cloud/mcp/47c10661-3a07-4968-9edc-da6941a28792"
)

# Cache for tool information
tool_cache = None


def is_valid_labor_query(query: str) -> bool:
    """
    Check if the query is related to labor laws or a casual greeting
    
    Args:
        query: User's input
        
    Returns:
        bool: True if it's a valid labor law query
    """
    query_lower = query.lower().strip()
    
    # List of casual/greeting phrases that aren't labor law queries
    casual_phrases = [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 
        'good evening', 'how are you', 'what\'s up', 'whatsup',
        'thanks', 'thank you', 'bye', 'goodbye', 'ok', 'okay'
    ]
    
    # If query is very short and matches casual phrases
    if len(query_lower.split()) <= 3:
        for phrase in casual_phrases:
            if phrase in query_lower or query_lower in phrase:
                return False
    
    return True


def get_helpful_response(query: str) -> str:
    """
    Generate a helpful response for casual queries or errors
    
    Args:
        query: User's input
        
    Returns:
        str: Helpful response
    """
    query_lower = query.lower().strip()
    
    # Handle greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in query_lower for greeting in greetings):
        return """👋 Hello! I'm your Qatar Labor Laws assistant.

I can help you with questions about Qatar labor regulations, such as:
• Working hours and schedules
• Leave entitlements (annual, sick, maternity)
• Employment contracts and termination
• Probation periods
• Overtime and compensation
• Employee rights and employer obligations

Please ask me a specific question about Qatar labor law!"""
    
    # Handle thank you
    if 'thank' in query_lower:
        return "You're welcome! Feel free to ask if you have more questions about Qatar labor laws."
    
    # Handle goodbye
    if any(word in query_lower for word in ['bye', 'goodbye', 'see you']):
        return "Goodbye! Come back anytime you need information about Qatar labor laws."
    
    # Default for unclear queries
    return """I'm here to answer questions about Qatar Labor Law. 

Please try asking a specific question like:
• "What are the working hours in Qatar?"
• "How many days of annual leave am I entitled to?"
• "What is the notice period for termination?"
• "Tell me about overtime pay regulations"

Please ask a question related to Qatar labor laws!"""


async def query_mcp(user_query: str) -> str:
    """
    Query the n8n MCP server with a user question
    
    Args:
        user_query: The question to ask about Qatar labor laws
        
    Returns:
        str: The response from the RAG system
    """
    global tool_cache
    
    # First, check if this is a valid labor law query
    if not is_valid_labor_query(user_query):
        return get_helpful_response(user_query)
    
    try:
        # Connect to MCP server using SSE transport
        async with sse_client(MCP_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                await session.initialize()
                
                # Discover available tools and cache schema (only once)
                if tool_cache is None:
                    tools_response = await session.list_tools()
                    
                    if not tools_response.tools:
                        return "❌ Error: No tools found on MCP server. Please try again later."
                    
                    # Use the first tool found
                    tool = tools_response.tools[0]
                    tool_cache = {
                        'name': tool.name,
                        'description': tool.description if hasattr(tool, 'description') else None,
                        'input_schema': tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                    }
                    
                    print(f"✅ Connected to MCP tool: '{tool_cache['name']}'")
                
                # Determine the correct parameter name from schema
                schema = tool_cache['input_schema']
                param_name = 'query'  # default
                
                # Check if schema has properties defined
                if isinstance(schema, dict):
                    if 'properties' in schema and schema['properties']:
                        param_name = list(schema['properties'].keys())[0]
                
                # Prepare arguments
                arguments = {param_name: user_query}
                
                # Call the tool with the user's query
                result = await session.call_tool(
                    tool_cache['name'],
                    arguments=arguments
                )
                
                # Extract the text response
                response_text = []
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        response_text.append(content_item.text)
                    elif isinstance(content_item, dict) and 'text' in content_item:
                        response_text.append(content_item['text'])
                
                if not response_text:
                    return get_helpful_response(user_query)
                
                # Parse the response
                raw_response = "\n".join(response_text).strip()
                
                # Check if it's an error response
                if "There was an error" in raw_response or "doesn't fit required format" in raw_response:
                    return get_helpful_response(user_query)
                
                # Try to parse if it's JSON
                try:
                    if raw_response.startswith('[') or raw_response.startswith('{'):
                        parsed = json.loads(raw_response)
                        
                        # Handle array response
                        if isinstance(parsed, list) and len(parsed) > 0:
                            first_item = parsed[0]
                            
                            if isinstance(first_item, dict):
                                # Check for nested 'output' with 'answer' inside
                                if 'output' in first_item:
                                    if isinstance(first_item['output'], dict) and 'answer' in first_item['output']:
                                        raw_response = first_item['output']['answer']
                                    elif isinstance(first_item['output'], str):
                                        raw_response = first_item['output']
                                # Direct 'answer' field
                                elif 'answer' in first_item:
                                    raw_response = first_item['answer']
                                elif 'text' in first_item:
                                    raw_response = first_item['text']
                                elif 'response' in first_item:
                                    raw_response = first_item['response']
                        
                        # Handle dict response
                        elif isinstance(parsed, dict):
                            # Priority order for extraction
                            for key in ['answer', 'response', 'output', 'text', 'result', 'data']:
                                if key in parsed:
                                    extracted = parsed[key]
                                    if isinstance(extracted, dict) and 'answer' in extracted:
                                        raw_response = extracted['answer']
                                    else:
                                        raw_response = extracted
                                    break
                                
                except json.JSONDecodeError:
                    pass
                
                # Ensure we always return a string
                if not isinstance(raw_response, str):
                    raw_response = str(raw_response)
                
                # Final validation - if response still contains error messages
                if "error" in raw_response.lower() and len(raw_response) < 100:
                    return get_helpful_response(user_query)
                
                return raw_response
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Don't show technical errors to users
        return """⚠️ I'm having trouble connecting to the Qatar labor law database right now. 

Please try:
1. Asking your question again in a moment
2. Rephrasing your question to be more specific
3. Asking about a specific topic like "working hours" or "leave entitlement"

If the problem persists, please contact the administrator."""


def chat_interface(message: str, history: list) -> str:
    """
    Synchronous wrapper for Gradio chat interface
    
    Args:
        message: User's message
        history: Chat history
        
    Returns:
        str: Bot's response
    """
    # Run the async function in the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(query_mcp(message))
        return response
    finally:
        loop.close()


# Example questions
EXAMPLES = [
    "What are the standard working hours in Qatar?",
    "Explain annual leave entitlement under Qatar Labour Law.",
    "What is the notice period for termination in Qatar?",
    "Are overtime payments mandatory in Qatar?",
    "What are the rights of employees in Qatar?",
    "Tell me about probation period in Qatar labor law.",
    "How many hours can I work during Ramadan?",
    "What is the minimum wage in Qatar?",
]


# Create Gradio interface
with gr.Blocks(
    title="Qatar Labor Laws RAG Chatbot",
    theme=gr.themes.Soft(),
    css="""
        .gradio-container {
            max-width: 900px !important;
        }
    """
) as demo:
    
    gr.Markdown(
        """
        # 🇶🇦 Qatar Labor Laws Assistant
        
        Get accurate answers about Qatar Labor Law from official regulations through our 
        AI-powered RAG (Retrieval Augmented Generation) system.
        
        **Ask specific questions** about working hours, leave entitlements, contracts, termination, 
        overtime, employee rights, and more.
        """
    )
    
    chatbot = gr.Chatbot(
        height=500,
        placeholder="👋 Hello! Ask me anything about Qatar Labor Laws...",
        show_label=False,
        avatar_images=("👤", "🇶🇦"),
        type="messages",  # Use new messages format for Gradio
    )
    
    msg = gr.Textbox(
        placeholder="Type your question here... (e.g., 'What are the working hours in Qatar?')",
        show_label=False,
        container=False,
    )
    
    with gr.Row():
        submit = gr.Button("📤 Send", variant="primary", size="lg")
        clear = gr.Button("🗑️ Clear Chat", size="lg")
    
    gr.Examples(
        examples=EXAMPLES,
        inputs=msg,
        label="💡 Example Questions - Click to try:",
    )
    
    def respond(message, chat_history):
        """Handle user message and update chat"""
        if not message.strip():
            return "", chat_history
        
        # Get bot response
        bot_message = chat_interface(message, chat_history)
        
        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return "", chat_history
    
    # Event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)
    
    gr.Markdown(
        """
        ---
        ### 📋 About This Assistant
        
        This chatbot uses:
        - **Model Context Protocol (MCP)** for tool integration
        - **n8n workflow** for processing
        - **RAG (Retrieval Augmented Generation)** to retrieve relevant information from official Qatar labor law documents
        
        **Note:** This assistant is specialized in Qatar labor law questions. For best results, ask specific 
        questions about employment regulations, working conditions, or employee rights in Qatar.
        
        **Data Source:** Official Qatar Labor Law regulations
        
        ---
        
        Built with ❤️ using Gradio and MCP | [GitHub](https://github.com) | [Report Issue](https://github.com)
        """
    )


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Qatar Labor Laws RAG Chatbot - Starting...")
    print("="*70)
    print(f"📡 MCP Server: {MCP_URL}")
    print("="*70 + "\n")
    
    # Launch with settings optimized for Hugging Face Spaces
    demo.launch(
        server_name="0.0.0.0",  # Required for Hugging Face Spaces
        server_port=7860,        # Default Gradio port
        share=False,
    )