from google.adk.tools import FunctionTool, ToolContext
from typing import List, Dict, Any
import os

def search_long_term_memory(
    query: str,
    tool_context: ToolContext # ToolContext provides access to MemoryService
) -> Dict[str, Any]:
    """
    Searches the user's long-term memory for information relevant to the query.
    Use this tool to recall details about past conversations, goals, or progress.

    Args:
        query: The query or concept to search for in the user's long-term memory.

    Returns:
        A list of relevant documents or snippets found in memory, including their content.
        Returns an empty list if nothing is found.
    """
    print(f"Tool Call: Searching long-term memory for: '{query}'")
    # Use the search_memory method from ToolContext
    # This method interacts with the configured MemoryService
    try:
        relevant_memories = tool_context.search_memory(query=query)
        print(f"Tool Result: Found {len(relevant_memories)} relevant memories.")
        # The result is a list of objects (often documents or snippets)
        # You might want to format this for the LLM
        formatted_results = []
        for i, memory in enumerate(relevant_memories):
             # Assuming memory objects have a 'content' attribute or similar
             # Structure the output clearly for the LLM
             # Add a check for the 'content' attribute to be safe
             content = getattr(memory, 'content', str(memory)) # Use str(memory) as fallback
             formatted_results.append(f"Memory Snippet {i+1}:\n{content}\n---") # Adjust based on actual memory object structure

        # Join formatted results for the LLM
        results_text = "\n".join(formatted_results) if formatted_results else "No relevant information found in long-term memory."

        return {"status": "success", "results": results_text} # Return structured output with joined text
    except Exception as e:
        print(f"Tool Error: Failed to search long-term memory: {e}")
        # Return an error status in a structured way
        return {"status": "error", "message": f"Failed to search memory: {e}"}


# Define the FunctionTool
search_long_term_memory_tool = FunctionTool(
    func=search_long_term_memory,
) 