import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_agents import AIAgents

@pytest.fixture
def ai_agents():
    return AIAgents()

@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = '{"pages": [{"name": "Home", "path": "/"}]}'
    return mock_response

@pytest.mark.asyncio
async def test_generate_site_maps(ai_agents, mock_anthropic_response):
    """Test site map generation"""
    with patch.object(ai_agents.client.messages, 'create') as mock_create:
        mock_create.return_value = mock_anthropic_response
        
        result = await ai_agents.generate_site_maps("Test project", count=2)
        
        assert len(result) == 2
        assert all(isinstance(r, dict) for r in result)
        assert mock_create.call_count == 2

@pytest.mark.asyncio
async def test_generate_mermaid_diagrams(ai_agents):
    """Test Mermaid diagram generation"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = 'graph TD\nA[Home] --> B[About]'
    
    with patch.object(ai_agents.client.messages, 'create') as mock_create:
        mock_create.return_value = mock_response
        
        site_map = {"pages": [{"name": "Home", "path": "/"}]}
        result = await ai_agents.generate_mermaid_diagrams("Test project", site_map, count=2)
        
        assert len(result) == 2
        assert all("graph TD" in r for r in result)
        assert mock_create.call_count == 2

@pytest.mark.asyncio
async def test_generate_backend_diagrams(ai_agents):
    """Test backend diagram generation"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = 'flowchart TD\nAPI --> Database'
    
    with patch.object(ai_agents.client.messages, 'create') as mock_create:
        mock_create.return_value = mock_response
        
        result = await ai_agents.generate_backend_diagrams("Test project", count=3)
        
        assert len(result) == 3
        assert all("flowchart TD" in r for r in result)
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_rate_artifacts(ai_agents):
    """Test artifact rating"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = '''[
        {"index": 0, "overall_score": 8.5, "completeness": 9, "clarity": 8, "feasibility": 8, "innovation": 9}
    ]'''
    
    with patch.object(ai_agents.client.messages, 'create') as mock_create:
        mock_create.return_value = mock_response
        
        artifacts = [{"pages": [{"name": "Home"}]}]
        result = await ai_agents.rate_artifacts(artifacts, "site maps", "Test project")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["overall_score"] == 8.5
        assert result[0]["completeness"] == 9

def test_parse_json_response(ai_agents):
    """Test JSON parsing from model responses"""
    # Test clean JSON
    result = ai_agents._parse_json_response('{"test": "value"}')
    assert result == {"test": "value"}
    
    # Test JSON with markdown code blocks
    result = ai_agents._parse_json_response('```json\n{"test": "value"}\n```')
    assert result == {"test": "value"}
    
    # Test invalid JSON
    result = ai_agents._parse_json_response('invalid json')
    assert result == {}

def test_clean_mermaid_diagram(ai_agents):
    """Test Mermaid diagram cleaning"""
    # Test clean diagram
    result = ai_agents._clean_mermaid_diagram('graph TD\nA-->B')
    assert result == 'graph TD\nA-->B'
    
    # Test diagram with markdown code blocks
    result = ai_agents._clean_mermaid_diagram('```mermaid\ngraph TD\nA-->B\n```')
    assert result == 'graph TD\nA-->B'
    
    # Test diagram with generic code blocks
    result = ai_agents._clean_mermaid_diagram('```\ngraph TD\nA-->B\n```')
    assert result == 'graph TD\nA-->B'

@pytest.mark.asyncio
async def test_error_handling(ai_agents):
    """Test error handling in AI agent methods"""
    with patch.object(ai_agents.client.messages, 'create') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        result = await ai_agents._generate_with_model("Test prompt")
        assert result == ""