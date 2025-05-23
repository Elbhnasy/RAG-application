import os
import importlib
import logging
from typing import Dict, Optional, Any
from functools import lru_cache

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
        # Fix logic: use language if path exists, otherwise use default
        if os.path.exists(language_path):
            self.language = language
            logger.info(f"Language set to: {language}")
        else:
            self.language = self.default_language
            logger.warning(f"Language '{language}' not found, using default: {self.default_language}")
        
        # Clear cache when language changes
        self._module_cache.clear()

    @lru_cache(maxsize=128)
    def _get_available_languages(self) -> list:
        """Get list of available languages"""
        locales_path = os.path.join(self.current_path, "locales")
        if not os.path.exists(locales_path):
            return [self.default_language]
        
        return [d for d in os.listdir(locales_path) 
                if os.path.isdir(os.path.join(locales_path, d))]

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
        
        # Try current language first
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        target_language = self.language

        if not os.path.exists(group_path):
            # Fallback to default language
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            target_language = self.default_language
            logger.warning(f"Template group '{group}' not found for language '{self.language}', using default")
        
        if not os.path.exists(group_path):
            logger.error(f"Template group '{group}' not found in any language")
            return None
        
        # Load the module
        module = self._load_module(group, target_language)
        if not module:
            return None
        
        # Get the template attribute
        try:
            template_attr = getattr(module, key, None)
            if template_attr is None:
                logger.error(f"Template key '{key}' not found in group '{group}' for language '{target_language}'")
                return None
            
            # Substitute variables
            return template_attr.substitute(vars)
            
        except AttributeError:
            logger.error(f"Template key '{key}' not found in group '{group}' for language '{target_language}'")
            return None
        except KeyError as e:
            logger.error(f"Missing variable {e} for template '{group}.{key}'")
            return None
        except Exception as e:
            logger.error(f"Error substituting template '{group}.{key}': {e}")
            return None

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return self._get_available_languages()

    def template_exists(self, group: str, key: str, language: str = None) -> bool:
        """Check if a template exists"""
        if language is None:
            language = self.language
            
        group_path = os.path.join(self.current_path, "locales", language, f"{group}.py")
        if not os.path.exists(group_path):
            return False
            
        module = self._load_module(group, language)
        return module is not None and hasattr(module, key)