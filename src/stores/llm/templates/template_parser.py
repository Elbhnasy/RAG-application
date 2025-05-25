import os
import importlib
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class TemplateParser:
    def __init__(self, language: str = None, default_language: str = "en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self._module_cache: Dict[str, Any] = {}

        self.set_language(language)

    def set_language(self, language: str):
        """Set the current language, fallback to default if not available"""
        if not language:
            language = self.default_language

        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
            logger.info(f"Language set to: {language}")
        else:
            self.language = self.default_language
            logger.warning(f"Language '{language}' not found, using default: {self.default_language}")
        
        self._module_cache.clear()

    def _load_module(self, group: str, target_language: str) -> Optional[Any]:
        """Load and cache template module"""
        cache_key = f"{target_language}.{group}"
        
        if cache_key in self._module_cache:
            return self._module_cache[cache_key]
        
        try:
            module_name = f"stores.llm.templates.locales.{target_language}.{group}"
            module = importlib.import_module(module_name)
            self._module_cache[cache_key] = module
            return module
        except (ImportError, ModuleNotFoundError) as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            return None

    def get(self, group: str, key: str, vars: Dict[str, Any] = None) -> Optional[str]:
        """Get template with substitution"""
        if not group or not key:
            logger.error("Group and key must be provided")
            return None
        
        if vars is None:
            vars = {}
        
        # Try current language first, then fallback to default
        for target_language in [self.language, self.default_language]:
            module = self._load_module(group, target_language)
            if module and hasattr(module, key):
                try:
                    template_attr = getattr(module, key)
                    return template_attr.substitute(vars)
                except KeyError as e:
                    logger.error(f"Missing variable {e} for template '{group}.{key}'")
                    return None
                except Exception as e:
                    logger.error(f"Error substituting template '{group}.{key}': {e}")
                    return None
        
        logger.error(f"Template '{group}.{key}' not found in any language")
        return None