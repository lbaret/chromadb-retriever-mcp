import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    url = "http://localhost:8000/sse"
    print(f"Connecting to {url}...")
    
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("Connected successfully!")
                
                # List available tools
                tools = await session.list_tools()
                print("\nAvailable Tools:")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
                
                # Test the retrieve_by_query tool
                print("\nTesting 'retrieve_by_query' tool...")
                result = await session.call_tool(
                    "retrieve_by_query", 
                    arguments={"query": "example query", "top_k": 2}
                )
                print(f"Result:\n{result}")

                # Test the retrieve_by_query tool with metadata filter
                print("\nTesting 'retrieve_by_query' tool with 'where' filter...")
                result_filtered = await session.call_tool(
                    "retrieve_by_query", 
                    arguments={"query": "example query", "top_k": 2, "where": {"source": "fake_source"}}
                )
                print(f"Result (Filtered):\n{result_filtered}")

                # Test the retrieve_batch tool
                print("\nTesting 'retrieve_batch' tool...")
                batch_result = await session.call_tool(
                    "retrieve_batch", 
                    arguments={"rows": ["first row query", "second row query"], "top_k": 1}
                )
                print(f"Batch Result:\n{batch_result}")
                
    except Exception as e:
        print(f"Error connecting to the MCP server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
