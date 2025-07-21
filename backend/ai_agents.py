import asyncio
from typing import List, Dict, Any
import anthropic
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIAgents:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"Initializing AI Agents with API key: {api_key[:10]}...{api_key[-4:] if api_key else 'NONE'}")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        
    async def _send_progress(self, project_id: str, step: str, message: str, progress: int):
        """Send progress update if callback is set"""
        if self.progress_callback:
            await self.progress_callback(project_id, step, message, progress)
        
    async def generate_site_maps(self, project_description: str, count: int = 1, project_id: str = None) -> List[Dict[str, Any]]:
        """Generate multiple site map options using sub-agents"""
        print(f"\n{'='*60}")
        print(f"GENERATING SITE MAPS")
        print(f"Project Description: {project_description[:100]}...")
        print(f"Count: {count}")
        print(f"{'='*60}\n")
        
        results = []
        for i in range(count):
            prompt = f"""As a web architecture specialist, create a comprehensive site map for the following project:
            
{project_description}

Create a site map with 5-8 main pages. For each page include:
- name (string)
- path (string) 
- description (1-2 sentences)
- features (array of 3-5 features)
- children (array, can be empty)

Return ONLY valid JSON, no additional text. Example structure:
{{
  "pages": [
    {{
      "name": "Home",
      "path": "/",
      "description": "Main landing page with product showcase.",
      "features": ["Hero section", "Featured products", "Newsletter signup"],
      "children": []
    }}
  ]
}}"""
            await self._send_progress(project_id, "sitemap", f"Preparing sitemap generation {i+1} of {count}...", 25 + (i * 10))
            await asyncio.sleep(0.3)
            await self._send_progress(project_id, "sitemap", f"Analyzing project requirements for sitemap structure...", 25 + (i * 10) + 2)
            print(f"\nGenerating sitemap {i+1} of {count}...")
            result = await self._generate_with_model(prompt, project_id, f"Sitemap {i+1}/{count}")
            await self._send_progress(project_id, "sitemap", f"Processing sitemap response {i+1}/{count}...", 25 + (i * 10) + 8)
            results.append(result)
        parsed_results = []
        
        # Save raw results to log file
        import datetime
        import os
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Created logs directory: {log_dir}")
            
        log_file = os.path.join(log_dir, f"sitemap_generation_{timestamp}.log")
        
        with open(log_file, 'w') as f:
            f.write(f"Sitemap Generation Log - {timestamp}\n")
            f.write(f"Project Description: {project_description}\n")
            f.write(f"{'='*80}\n\n")
            
            for i, r in enumerate(results):
                await self._send_progress(project_id, "sitemap", f"Validating sitemap {i+1} structure and content...", 35 + (i * 5))
                
                print(f"\n--- Result {i+1} ---")
                print(f"Raw response length: {len(r) if r else 0}")
                print(f"First 200 chars: {r[:200] if r else 'EMPTY'}")
                
                f.write(f"Result {i+1}:\n")
                f.write(f"Raw response: {r}\n")
                f.write(f"{'='*80}\n\n")
                
                await self._send_progress(project_id, "sitemap", f"Parsing JSON response for sitemap {i+1}...", 38 + (i * 5))
                parsed = self._parse_json_response(r)
                
                # If parsing failed or result is empty, create a default sitemap
                if not parsed or not isinstance(parsed, dict) or 'pages' not in parsed:
                    await self._send_progress(project_id, "sitemap", f"Sitemap {i+1} parsing failed, using fallback structure...", 40 + (i * 5))
                    print(f"WARNING: Failed to parse sitemap {i+1} or empty result, using fallback")
                    print(f"Parsed result: {parsed}")
                    f.write(f"PARSING FAILED - Using fallback\n")
                    f.write(f"Parsed result: {parsed}\n\n")
                    
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
                else:
                    await self._send_progress(project_id, "sitemap", f"Sitemap {i+1} validated: {len(parsed.get('pages', []))} pages created", 42 + (i * 5))
                    print(f"SUCCESS: Parsed sitemap {i+1} with {len(parsed.get('pages', []))} pages")
                    f.write(f"PARSING SUCCESS\n")
                    f.write(f"Number of pages: {len(parsed.get('pages', []))}\n\n")
                
                parsed_results.append(parsed)
        
        print(f"\n{'='*60}")
        print(f"SITEMAP GENERATION COMPLETE")
        print(f"Log saved to: {log_file}")
        print(f"{'='*60}\n")
        
        return parsed_results
    
    async def generate_mermaid_diagrams(self, project_description: str, site_map: Dict, count: int = 1, project_id: str = None) -> List[str]:
        """Generate multiple Mermaid diagram options for frontend architecture"""
        await self._send_progress(project_id, "architecture", "Initializing frontend architecture design...", 55)
        await asyncio.sleep(0.2)
        await self._send_progress(project_id, "architecture", "Analyzing sitemap structure for component hierarchy...", 57)
        
        tasks = []
        for i in range(count):
            await self._send_progress(project_id, "architecture", f"Preparing architecture diagram {i+1}/{count}...", 58 + (i * 5))
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
            tasks.append(self._generate_with_model(prompt, project_id, f"Frontend Diagram {i+1}/{count}"))
        
        await self._send_progress(project_id, "architecture", f"Generating {count} frontend architecture diagram(s)...", 60)
        results = await asyncio.gather(*tasks)
        
        await self._send_progress(project_id, "architecture", "Processing and cleaning Mermaid diagrams...", 68)
        cleaned_results = []
        for i, r in enumerate(results):
            await self._send_progress(project_id, "architecture", f"Cleaning diagram {i+1}/{count}...", 69 + i)
            cleaned_results.append(self._clean_mermaid_diagram(r))
        
        await self._send_progress(project_id, "architecture", "Frontend architecture diagrams complete!", 72)
        return cleaned_results
    
    async def generate_backend_diagrams(self, project_description: str, count: int = 1, project_id: str = None) -> List[str]:
        """Generate multiple backend architecture diagrams"""
        await self._send_progress(project_id, "backend", "Initializing backend architecture design...", 75)
        await asyncio.sleep(0.2)
        await self._send_progress(project_id, "backend", "Analyzing data flow and API requirements...", 77)
        
        tasks = []
        for i in range(count):
            await self._send_progress(project_id, "backend", f"Setting up backend diagram {i+1}/{count}...", 78 + (i * 3))
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
            tasks.append(self._generate_with_model(prompt, project_id, f"Backend Diagram {i+1}/{count}"))
        
        await self._send_progress(project_id, "backend", f"Generating {count} backend architecture diagram(s)...", 80)
        results = await asyncio.gather(*tasks)
        
        await self._send_progress(project_id, "backend", "Processing backend diagrams and cleaning code...", 87)
        cleaned_results = []
        for i, r in enumerate(results):
            await self._send_progress(project_id, "backend", f"Finalizing backend diagram {i+1}/{count}...", 88 + i)
            cleaned_results.append(self._clean_mermaid_diagram(r))
        
        await self._send_progress(project_id, "backend", "Backend architecture diagrams complete!", 90)
        return cleaned_results
    
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
    
    async def _generate_with_model(self, prompt: str, project_id: str = None, step_description: str = "Processing") -> str:
        """Generate response using Anthropic Claude API"""
        await self._send_progress(project_id, "ai_call", f"{step_description}: Sending request to Claude AI...", 0)
        
        print(f"\n--- AI API CALL ---")
        print(f"Prompt length: {len(prompt)} chars")
        print(f"Model: claude-sonnet-4-20250514")
        
        try:
            await self._send_progress(project_id, "ai_call", f"{step_description}: Claude AI thinking and analyzing...", 0)
            
            # Make synchronous call directly
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10000,  # Increased to handle even larger JSON responses
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and len(response.content) > 0:
                result = response.content[0].text
                await self._send_progress(project_id, "ai_call", f"{step_description}: Response received ({len(result)} chars)", 0)
                
                print(f"Response received: {len(result)} chars")
                print(f"Response type: {type(response.content[0])}")
                print(f"Stop reason: {response.stop_reason}")
                
                if response.stop_reason == "max_tokens":
                    print("WARNING: Response was truncated due to max_tokens limit!")
                    await self._send_progress(project_id, "ai_call", f"{step_description}: Response truncated - may need adjustment", 0)
                    
                return result
            else:
                print("WARNING: Empty response.content from Claude API")
                print(f"Response object: {response}")
                await self._send_progress(project_id, "ai_call", f"{step_description}: Empty response from Claude", 0)
                return ""
                
        except Exception as e:
            print(f"ERROR generating with model: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            await self._send_progress(project_id, "ai_call", f"{step_description}: API error - {str(e)[:50]}...", 0)
            return ""
    
    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from model response"""
        print(f"\n--- PARSING JSON ---")
        print(f"Response length: {len(response) if response else 0}")
        
        if not response:
            print("ERROR: Empty response to parse")
            return {}
            
        try:
            # Clean response if needed
            original_response = response
            response = response.strip()
            
            if response.startswith("```json"):
                print("Cleaning: Removing ```json prefix")
                response = response[7:]
            if response.endswith("```"):
                print("Cleaning: Removing ``` suffix")
                response = response[:-3]
                
            response = response.strip()
            print(f"Cleaned response length: {len(response)}")
            print(f"First 100 chars: {response[:100]}...")
            print(f"Last 100 chars: ...{response[-100:]}")
            
            result = json.loads(response)
            print(f"SUCCESS: Parsed JSON")
            print(f"Type: {type(result)}")
            print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict) and 'pages' in result:
                print(f"Pages found: {len(result['pages'])}")
                
            return result
        except json.JSONDecodeError as e:
            print(f"ERROR parsing JSON: {e}")
            print(f"Error position: {e.pos if hasattr(e, 'pos') else 'Unknown'}")
            print(f"Raw response first 500 chars: {response[:500]}...")
            return {}
        except Exception as e:
            print(f"ERROR parsing JSON (other): {type(e).__name__}: {str(e)}")
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