import os
from tavily import TavilyClient
import dotenv

dotenv.load_dotenv()

class ContextAgent:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            print("Warning: TAVILY_API_KEY not found. Context features will be disabled.")
            self.client = None
        else:
            self.client = TavilyClient(api_key=self.api_key)

    def get_context(self, query: str) -> str:
        """
        Searches for the manga chapter summary/context.
        Returns a string summarizing the search results.
        """
        if not self.client:
            return ""

        print(f"Fetching context for: '{query}'...")
        try:
            # We use "advanced" depth for better RAG context if needed, 
            # but usually "basic" is enough for a summary.
            # Including answer=True often gives a direct summary.
            response = self.client.search(
                query=query,
                search_depth="basic",
                include_answer=True,
                max_results=3,
                topic="general"
            )
            
            context_parts = []
            
            # 1. Direct Answer (if available)
            if response.get("answer"):
                context_parts.append(f"AI SUMMARY:\n{response['answer']}")
            
            # 2. Top Results Snippets
            context_parts.append("\nWEB RESULTS:")
            for result in response.get("results", []):
                title = result.get("title", "No Title")
                content = result.get("content", "")
                context_parts.append(f"- {title}: {content}")
                
            full_context = "\n\n".join(context_parts)
            return full_context

        except Exception as e:
            print(f"Error fetching context: {e}")
            return ""

if __name__ == "__main__":
    # Test
    agent = ContextAgent()
    if agent.client:
        print(agent.get_context("Boruto Chapter 28 summary"))
