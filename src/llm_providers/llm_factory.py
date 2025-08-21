from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

import os

from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI

from src.config.config_loader import ConfigLoader
from src.observability import logger


class LLMFactory:
    def __init__(self):
        self.config_loader = ConfigLoader()

    def create_llm(self, provider_id: str):
        """
        Creates an LLM instance based on a provider ID.

        Args:
            provider_id: The generic provider ID (e.g., "google_gemini", "openai").

        Returns:
            An instance of a LangChain LLM.
        """
        config = self.config_loader.load_llm_config(provider_id)

        provider_type = config.get("provider")
        model = config.get("model")

        if provider_type == "google_vertex_ai":
            # For Google, project_id and location are needed.
            # They are loaded from environment variables for security.
            project_id = os.getenv("GCP_PROJECT_ID")
            location = os.getenv("GCP_LOCATION")

            if not project_id or not location:
                raise ValueError("GCP_PROJECT_ID and GCP_LOCATION must be set in the .env file")

            logger.debug(f"Attempting to create ChatVertexAI with project: {project_id}, location: {location}, model: {model}")
            llm = ChatVertexAI(model_name=model, project=project_id, location=location)
            logger.debug("Successfully created ChatVertexAI instance.")
            return llm

        elif provider_type == "openai":
            # For OpenAI, the API key is needed.
            # It is loaded from environment variables for security.
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY must be set in the .env file")
            return ChatOpenAI(model_name=model, api_key=api_key, temperature=1.0)

        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")
