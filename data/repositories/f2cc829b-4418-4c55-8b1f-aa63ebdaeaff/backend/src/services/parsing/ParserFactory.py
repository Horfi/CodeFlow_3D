# backend/src/services/parsing/ParserFactory.py
from typing import Optional, List  # Add List import here
from .base_parser import BaseParser

class ParserFactory:
    """Factory for creating language-specific parsers"""
    
    @classmethod
    def create_parser(cls, language: str) -> Optional[BaseParser]:
        """Create a parser for the specified language"""
        if language.lower() == 'python':
            from .PythonParser import PythonParser
            return PythonParser()
        elif language.lower() == 'javascript':
            from .JavaScriptParser import JavaScriptParser
            return JavaScriptParser()
        elif language.lower() == 'typescript':
            from .TypeScriptParser import TypeScriptParser
            return TypeScriptParser()
        else:
            return None
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of supported languages"""
        return ['python', 'javascript', 'typescript']
    