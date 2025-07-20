import asyncio
from typing import List, Dict, Any
import anthropic
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIAgents:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def generate_site_maps(self, project_description: str, count: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple site map options using sub-agents"""
        tasks = []
        for i in range(count):
            prompt = f"""As a web architecture specialist, create a comprehensive site map for the following project:
            
{project_description}

Create an extremely detailed site map with comprehensive information for each page:
- At least 8-12 main pages/sections
- Multiple nested pages where appropriate
- For EACH page include:
  * 5-8 specific features
  * A detailed description (2-3 sentences)
  * Technical requirements
  * User interactions
  * Data requirements
  * SEO considerations

Return ONLY valid JSON with this exact structure:
{{
  "pages": [
    {{
      "name": "Home",
      "path": "/",
      "description": "The main landing page that introduces the product and captures visitor interest. Features dynamic content personalization based on user behavior and A/B tested conversion elements.",
      "features": [
        "Hero section with animated background and CTA buttons",
        "Feature comparison grid with interactive tooltips",
        "Customer testimonials carousel with video testimonials",
        "Live chat integration with AI-powered responses",
        "Newsletter signup with double opt-in process",
        "Social proof indicators (user count, reviews)",
        "Performance metrics dashboard preview",
        "Multi-language support selector"
      ],
      "technical_requirements": [
        "Server-side rendering for SEO",
        "Lazy loading for images and videos",
        "WebSocket connection for live data",
        "CDN integration for static assets"
      ],
      "user_interactions": [
        "Scroll-triggered animations",
        "Hover effects on interactive elements",
        "Form validation with real-time feedback",
        "Cookie consent management"
      ],
      "data_requirements": [
        "User analytics tracking",
        "A/B test variant selection",
        "Personalization engine integration",
        "Real-time metrics from backend"
      ],
      "seo_considerations": [
        "Meta tags optimization",
        "Schema.org structured data",
        "OpenGraph tags for social sharing",
        "Sitemap.xml generation"
      ],
      "children": []
    }}
  ]
}}"""
            tasks.append(self._generate_with_model(prompt))
        
        results = await asyncio.gather(*tasks)
        parsed_results = []
        for r in results:
            parsed = self._parse_json_response(r)
            # If parsing failed or result is empty, create a default sitemap
            if not parsed or not isinstance(parsed, dict) or 'pages' not in parsed:
                print("Warning: Failed to parse sitemap or empty result, using fallback")
                parsed = {
                    "pages": [
                        {
                            "name": "Home",
                            "path": "/",
                            "description": "Main landing page",
                            "features": ["Welcome message", "Navigation menu", "Call to action"],
                            "children": []
                        }
                    ]
                }
            parsed_results.append(parsed)
        return parsed_results
    
    async def generate_mermaid_diagrams(self, project_description: str, site_map: Dict, count: int = 1) -> List[str]:
        """Generate multiple Mermaid diagram options for frontend architecture"""
        tasks = []
        for i in range(count):
            prompt = f"""As a frontend architecture expert (Agent {i+1}), create a Mermaid diagram for:
            
Project: {project_description}
Site Map: {json.dumps(site_map, indent=2)}

Focus on: {"component hierarchy" if i == 0 else "data flow" if i == 1 else "user interactions"}

Create a VERTICAL (top-to-bottom) diagram with proper spacing.

Return your response in this EXACT format:
<MERMAID_START>
flowchart TB
    [your mermaid diagram here]
<MERMAID_END>

IMPORTANT: 
- Use TB (Top-Bottom) for vertical layout
- Space nodes appropriately for readability
- Include ONLY the diagram between the markers
- No explanations
- Use ONLY black boxes with white text and white outlines
- Do NOT use any colors - everything should be black and white only
- Style example: A[Component]:::blackBox
- classDef blackBox fill:#000,stroke:#fff,stroke-width:2px,color:#fff"""
            tasks.append(self._generate_with_model(prompt))
        
        results = await asyncio.gather(*tasks)
        return [self._clean_mermaid_diagram(r) for r in results]
    
    async def generate_backend_diagrams(self, project_description: str, count: int = 1) -> List[str]:
        """Generate multiple backend architecture diagrams"""
        tasks = []
        for i in range(count):
            prompt = f"""As a backend architecture specialist (Agent {i+1}), create a Mermaid diagram for the backend of:
            
{project_description}

Focus on: {"API design" if i == 0 else "database schema" if i == 1 else "microservices"}

Create a VERTICAL (top-to-bottom) diagram with proper spacing.

Return your response in this EXACT format:
<MERMAID_START>
flowchart TB
    [your mermaid diagram here]
<MERMAID_END>

IMPORTANT: 
- Use TB (Top-Bottom) for vertical layout
- Space nodes appropriately for readability
- Include ONLY the diagram between the markers
- No explanations
- Use ONLY black boxes with white text and white outlines
- Do NOT use any colors - everything should be black and white only
- Style example: A[Component]:::blackBox
- classDef blackBox fill:#000,stroke:#fff,stroke-width:2px,color:#fff"""
            tasks.append(self._generate_with_model(prompt))
        
        results = await asyncio.gather(*tasks)
        return [self._clean_mermaid_diagram(r) for r in results]
    
    async def rate_artifacts(self, artifacts: List[Any], artifact_type: str, project_description: str) -> List[Dict[str, Any]]:
        """Rate generated artifacts using a critic agent"""
        prompt = f"""As an expert reviewer, rate these {artifact_type} for the project:
        
Project: {project_description}

Artifacts to rate:
{json.dumps(artifacts, indent=2)}

Rate each on a scale of 1-10 for:
- Completeness
- Clarity
- Feasibility
- Innovation

Return JSON array with ratings for each artifact:
[{{"index": 0, "overall_score": 8.5, "completeness": 9, "clarity": 8, "feasibility": 8, "innovation": 9, "feedback": "..."}}]"""
        
        response = await self._generate_with_model(prompt)
        return self._parse_json_response(response)
    
    async def _generate_with_model(self, prompt: str) -> str:
        """Generate response using Anthropic Claude API"""
        try:
            # Run in thread pool since anthropic client is sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            result = response.content[0].text if response.content else ""
            if not result:
                print("Warning: Empty response from Claude API")
            return result
        except Exception as e:
            print(f"Error generating with model: {e}")
            return ""
    
    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from model response"""
        try:
            # Clean response if needed
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            result = json.loads(response.strip())
            print(f"Successfully parsed JSON with keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            return result
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response[:500]}...")
            return {}
    
    def _clean_mermaid_diagram(self, diagram: str) -> str:
        """Clean Mermaid diagram response"""
        diagram = diagram.strip()
        
        # Extract content between markers
        if "<MERMAID_START>" in diagram and "<MERMAID_END>" in diagram:
            start = diagram.find("<MERMAID_START>") + len("<MERMAID_START>")
            end = diagram.find("<MERMAID_END>")
            diagram = diagram[start:end].strip()
        
        # Fallback: clean markdown code blocks
        if diagram.startswith("```mermaid"):
            diagram = diagram[10:]
        if diagram.startswith("```"):
            diagram = diagram[3:]
        if diagram.endswith("```"):
            diagram = diagram[:-3]
        
        # If still has issues, try to extract just the diagram part
        lines = diagram.strip().split('\n')
        clean_lines = []
        in_diagram = False
        
        for line in lines:
            if line.strip().startswith(('graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'gitGraph')):
                in_diagram = True
            if in_diagram:
                clean_lines.append(line)
        
        if clean_lines:
            return '\n'.join(clean_lines).strip()
        
        # Last resort: return a default diagram
        return "flowchart TD\n    A[Component] --> B[Loading...]"