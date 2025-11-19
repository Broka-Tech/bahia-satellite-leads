import re
import unicodedata
import google.generativeai as genai
import logging
from typing import Dict, Any

logger = logging.getLogger("SEOMetadata")

class MetadataGenerator:
    """
    Módulo 2: Semantic Slug & Meta Generator
    Gera metadados otimizados e URLs amigáveis.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def _slugify(self, text: str) -> str:
        """
        Converte texto para slug URL-friendly.
        """
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^\w\s-]', '', text).lower()
        return re.sub(r'[-\s]+', '-', text).strip('-')

    def generate_seo_data(self, property_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera Title, Meta Description e Slug.
        """
        # Dados básicos
        tipo = property_data.get('type', 'Imovel')
        bairro = property_data.get('location', {}).get('neighborhood', 'Salvador')
        quartos = property_data.get('bedrooms', 0)
        titulo_original = property_data.get('title', '')
        
        # 1. Title Tag Otimizada
        # Ex: "Apartamento em Horto Florestal - Vista Mar | Bahia Satellite"
        destaque = "Exclusivo" # Default
        if "mar" in titulo_original.lower():
            destaque = "Vista Mar"
        elif "luxo" in titulo_original.lower():
            destaque = "Alto Padrão"
            
        seo_title = f"{tipo} em {bairro} - {destaque} | Bahia Satellite"

        # 2. Slug Semântico
        # Padrão: {tipo}-{quartos}-quartos-{bairro}-{caracteristica}
        caracteristica = self._slugify(destaque)
        slug_base = f"{tipo}-{quartos}-quartos-{bairro}-{caracteristica}"
        slug = self._slugify(slug_base)

        # 3. Meta Description (Gemini)
        meta_description = self._generate_meta_description(property_data)

        return {
            "seo_title": seo_title,
            "seo_slug": slug,
            "meta_description": meta_description
        }

    def _generate_meta_description(self, property_data: Dict) -> str:
        """
        Usa Gemini para criar uma meta description persuasiva (max 160 chars).
        """
        if not self.model:
            return f"Confira este {property_data.get('type')} em {property_data.get('location', {}).get('neighborhood')}. Oportunidade única."

        prompt = f"""
        Escreva uma Meta Description para SEO (máximo 155 caracteres) para este imóvel:
        Tipo: {property_data.get('type')}
        Bairro: {property_data.get('location', {}).get('neighborhood')}
        Detalhes: {property_data.get('title')}
        
        O texto deve ser convidativo e incluir um Call to Action sutil.
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if len(text) > 160:
                text = text[:157] + "..."
            return text
        except Exception as e:
            logger.error(f"Erro ao gerar meta description: {e}")
            return f"Imóvel incrível em {property_data.get('location', {}).get('neighborhood')}. Saiba mais."
