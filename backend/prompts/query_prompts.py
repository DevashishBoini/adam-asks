QUERY_GENERATION_PROMPT = """
You are an AI assistant specialized in semantic code search query generation. Generate {num_queries} optimized search queries for the given user question about a codebase.
I need help breaking down a complex code-related query into vector search-friendly queries that will yield the most relevant results from a code repository.

## Input:
**User Query:** "{user_query}"
**Repository README:** {repo_readme}
**Repository Structure:** {repo_structure}

## Task:
Generate {num_queries} diverse, contextually-aware search queries that will help retrieve the most relevant code sections to answer the user's question.

## Strategy:
1. **Parse Intent**: Identify what the user wants to know (implementation details, usage patterns, configuration, etc.)
2. **Extract Keywords**: Pull technical terms, concepts, and specific entities from the user query
3. **Apply Context**: Use README and structure [if available] to identify relevant:
   - Technologies and frameworks used
   - Key modules/components that might contain the answer
   - Domain-specific terminology
4. **Diversify Approaches**: Create queries targeting different aspects:
   - Direct implementation queries
   - Usage/example queries  
   - Configuration/setup queries
   - Error handling/edge case queries
   - Documentation/comment queries

## Query Optimization Guidelines:
- **Be Specific**: Include exact function names, class names, file patterns when identifiable
- **Use Technical Language**: Employ terminology likely found in code comments and documentation
- **Target Different Granularities**: Some queries for specific functions, others for broader concepts
- **Include Context Clues**: Reference related technologies, patterns, or architectural components
- **Consider Code Patterns**: Think about how developers typically implement the queried functionality

## Examples of Query Types to Generate:
- `function_name implementation details`
- `class_name usage examples`
- `feature_name configuration setup`
- `error handling for specific_process`
- `integration with external_service`

## Output Format:
Return a JSON array containing exactly {num_queries} strings, each representing an optimized search query.
Return ONLY a valid JSON array with no markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` blocks.
Examples of good search-friendly queries:
["implementation FileReader class parse methods", "ChunkProcessor splitDocument function parameters", "vectorizeCode embeddings configuration options"]

"""
DUMMY_QUERY = "Who is the PM of India"