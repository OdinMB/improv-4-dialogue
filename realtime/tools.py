import chainlit as cl
import plotly

search_documents_def = {
    "name": "search_documents",
    "description": "Semantic search over our internal knowledge base. Should be used for answering most questions by the user. Returns a list of relevant documents.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query to use for the semantic search."
        }
      },
      "required": ["query"]
    }
}

async def search_documents_handler(query):
    """
    Semantic search over documents. Returns a list of relevant documents.
    """
    print("Tool call: search_documents.", query)
    try:
        # Hard-coded list of documents
        result = [
            {
                "title": "Introduction to Machine Learning",
                "file": "file1.pdf",
                "content": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models...",
                "relevance_score": 0.95
            },
            {
                "title": "Python Programming Basics",
                "file": "file2.pdf",
                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability...",
                "relevance_score": 0.87
            },
            {
                "title": "Data Structures and Algorithms",
                "file": "file3.pdf",
                "content": "Data structures are ways of organizing and storing data, while algorithms are step-by-step procedures for solving problems...",
                "relevance_score": 0.82
            }
        ]
        
        # Display the relevant documents in the chat
        message = "Hier sind die relevantesten Dokumente:"
        elements = [
            cl.Text(name=f"{doc['title']}", content=f"Datei: {doc['file']}\nRelevanz: {doc['relevance_score']:.2f}\n\n{doc['content']}")
            for i, doc in enumerate(result)
        ]
        await cl.Message(content=message, elements=elements).send()
        
        print("Result: ", result)
        return result
 
    except Exception as e:
        return {"error": str(e)}

search_documents = (search_documents_def, search_documents_handler)


draw_plotly_chart_def = {
    "name": "draw_plotly_chart",
    "description": "Draws a Plotly chart based on the provided JSON figure and displays it with an accompanying message.",
    "parameters": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string",
          "description": "The message to display alongside the chart"
        },
        "plotly_json_fig": {
          "type": "string",
          "description": "A JSON string representing the Plotly figure to be drawn"
        }
      },
      "required": ["message", "plotly_json_fig"]
    }
}

async def draw_plotly_chart_handler(message: str, plotly_json_fig):
    fig = plotly.io.from_json(plotly_json_fig)
    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

    await cl.Message(content=message, elements=elements).send()
    
draw_plotly_chart = (draw_plotly_chart_def, draw_plotly_chart_handler)


tools = [search_documents, draw_plotly_chart]