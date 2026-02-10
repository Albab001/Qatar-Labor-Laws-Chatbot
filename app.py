"""
Qatar Labor Laws RAG Chatbot - Hugging Face Spaces Deployment
Compatible with Gradio 5.4.0 (recommended pin)
"""

import asyncio
import json
import os
import gradio as gr
from mcp import ClientSession
from mcp.client.sse import sse_client

MCP_URL = os.getenv(
    "MCP_URL",
    "https://albabnawaz.app.n8n.cloud/mcp/47c10661-3a07-4968-9edc-da6941a28792"
)

tool_cache = None


def is_valid_labor_query(query: str) -> bool:
    query_lower = query.lower().strip()
    casual_phrases = [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 
        'good evening', 'how are you', 'what\'s up', 'whatsup',
        'thanks', 'thank you', 'bye', 'goodbye', 'ok', 'okay'
    ]
    if len(query_lower.split()) <= 3:
        for phrase in casual_phrases:
            if phrase in query_lower or query_lower in phrase:
                return False
    return True


def get_helpful_response(query: str) -> str:
    query_lower = query.lower().strip()
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in query_lower for greeting in greetings):
        return """Hello! I'm your Qatar Labor Laws assistant.

I can help you with questions about Qatar labor regulations, such as:
• Working hours and schedules
• Leave entitlements (annual, sick, maternity)
• Employment contracts and termination
• Probation periods
• Overtime and compensation
• Employee rights and employer obligations

Please ask me a specific question about Qatar labor law!"""
    
    if 'thank' in query_lower:
        return "You're welcome! Feel free to ask if you have more questions about Qatar labor laws."
    
    if any(word in query_lower for word in ['bye', 'goodbye', 'see you']):
        return "Goodbye! Come back anytime you need information about Qatar labor laws."
    
    return """I'm here to answer questions about Qatar Labor Law. 

Please try asking a specific question like:
• "What are the working hours in Qatar?"
• "How many days of annual leave am I entitled to?"
• "What is the notice period for termination?"
• "Tell me about overtime pay regulations"

Please ask a question related to Qatar labor laws!"""


async def query_mcp(user_query: str) -> str:
    global tool_cache
    
    if not is_valid_labor_query(user_query):
        return get_helpful_response(user_query)
    
    try:
        async with sse_client(MCP_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                if tool_cache is None:
                    tools_response = await session.list_tools()
                    if not tools_response.tools:
                        return "Error: No tools found on MCP server."
                    tool = tools_response.tools[0]
                    tool_cache = {
                        'name': tool.name,
                        'description': getattr(tool, 'description', None),
                        'input_schema': getattr(tool, 'inputSchema', {})
                    }
                    print(f"Connected to MCP tool: '{tool_cache['name']}'")
                
                schema = tool_cache['input_schema']
                param_name = 'query'
                if isinstance(schema, dict) and 'properties' in schema and schema['properties']:
                    param_name = list(schema['properties'].keys())[0]
                
                arguments = {param_name: user_query}
                
                result = await session.call_tool(tool_cache['name'], arguments=arguments)
                
                response_text = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        response_text.append(item.text)
                    elif isinstance(item, dict) and 'text' in item:
                        response_text.append(item['text'])
                
                if not response_text:
                    return get_helpful_response(user_query)
                
                raw = "\n".join(response_text).strip()
                
                if "There was an error" in raw:
                    return get_helpful_response(user_query)
                
                # Attempt smart parsing of common wrapped responses
                try:
                    if raw.startswith(('[', '{')):
                        parsed = json.loads(raw)
                        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                            for k in ['output', 'answer', 'text', 'response']:
                                if k in parsed[0]:
                                    v = parsed[0][k]
                                    if isinstance(v, dict) and 'answer' in v:
                                        return v['answer']
                                    if isinstance(v, str):
                                        return v
                        if isinstance(parsed, dict):
                            for k in ['answer', 'response', 'output', 'text', 'result', 'data']:
                                if k in parsed:
                                    v = parsed[k]
                                    if isinstance(v, dict) and 'answer' in v:
                                        return v['answer']
                                    if isinstance(v, str):
                                        return v
                except json.JSONDecodeError:
                    pass
                
                if not isinstance(raw, str):
                    raw = str(raw)
                
                if "error" in raw.lower() and len(raw) < 100:
                    return get_helpful_response(user_query)
                
                return raw
                
    except Exception as e:
        print(f"MCP error: {str(e)}")
        return """I'm having trouble connecting to the Qatar labor law database right now. 

Please try again in a moment or rephrase your question.
If the issue continues, contact the administrator."""


def chat_interface(message: str, history) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(query_mcp(message))
    finally:
        loop.close()


EXAMPLES = [
    "What are the standard working hours in Qatar?",
    "Explain annual leave entitlement under Qatar Labour Law.",
    "What is the notice period for termination in Qatar?",
    "Are overtime payments mandatory in Qatar?",
    "What are the rights of employees in Qatar?",
    "Tell me about probation period in Qatar labor law.",
]


with gr.Blocks(title="Qatar Labor Laws RAG Chatbot") as demo:
    
    gr.Markdown("# Qatar Labor Laws Assistant\nAsk questions about Qatar Labor Law and get precise answers from official regulations.")
    
    chatbot = gr.Chatbot(
        label="Chat History",
        height=500,
        # type="messages"   ← REMOVED - not accepted in many 5.x and 6.x versions
    )
    
    msg = gr.Textbox(
        label="Your Question",
        placeholder="Ask about Qatar labor laws...",
        lines=2,
    )
    
    with gr.Row():
        submit = gr.Button("Send", variant="primary")
        clear  = gr.Button("Clear")
    
    gr.Examples(examples=EXAMPLES, inputs=msg, label="Example Questions")
    
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history
        
        bot_message = chat_interface(message, chat_history)
        
        # Messages format — works in 5.4+ and is future-proof
        chat_history.append({"role": "user",      "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)
    
    gr.Markdown("---\n**Powered by:** MCP + n8n + RAG  \n**Data Source:** Official Qatar Labor Law regulations")


if __name__ == "__main__":
    print("="*70)
    print("Qatar Labor Laws RAG Chatbot - Starting...")
    print("="*70)
    print(f"MCP Server: {MCP_URL}")
    print("="*70 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )