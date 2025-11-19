import re
import google.generativeai as genai
import logging
import json
from typing import List, Dict, Optional

logger = logging.getLogger("SEOAggregator")

class EntityAggregator:
    """
    Módulo 1: Entity Aggregator
    Responsável por identificar e agrupar imóveis do mesmo condomínio/edifício.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def extract_building_name(self, title: str) -> Optional[str]:
        """
        Tenta extrair o nome do edifício do título usando Regex.
        Padrões comuns: "Edf. X", "Mansão Y", "Condomínio Z".
        """
        patterns = [
            r"(?i)(?:edf\.?|edifício|edificio)\s+([A-Za-z0-9\s]+?)(?:\s-|\s,|$)",
            r"(?i)(?:mansão)\s+([A-Za-z0-9\s]+?)(?:\s-|\s,|$)",
            r"(?i)(?:condomínio|condominio)\s+([A-Za-z0-9\s]+?)(?:\s-|\s,|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1).strip()
        
        return None

    def group_properties(self, properties: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa imóveis por nome de edifício normalizado.
        """
        groups = {}
        for prop in properties:
            title = prop.get('title', '')
            building_name = self.extract_building_name(title)
            
            if building_name:
                # Normalização simples
                key = building_name.lower().strip()
                if key not in groups:
                    groups[key] = {
                        'name': building_name,
                        'properties': []
                    }
                groups[key]['properties'].append(prop)
        
        # Filtrar apenas grupos com mais de 2 imóveis (conforme regra)
        valid_groups = {k: v for k, v in groups.items() if len(v['properties']) > 2}
        return valid_groups

    def generate_building_description(self, building_name: str, neighborhood: str) -> str:
        """
        Gera um review técnico e histórico sobre o condomínio usando Gemini.
        """
        if not self.model:
            return "Descrição indisponível (AI não configurada)."

        prompt = f"""
        Escreva um review técnico e histórico sobre o condomínio '{building_name}' localizado em {neighborhood}, Salvador, Bahia.
        Foco:
        1. Infraestrutura (lazer, segurança).
        2. Exclusividade e perfil dos moradores.
        3. Valorização histórica.
        
        O texto deve ser persuasivo para SEO, com cerca de 200 palavras.
        Não invente dados específicos se não souber, foque no prestígio e localização.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Erro ao gerar descrição para {building_name}: {e}")
            return "Descrição temporariamente indisponível."
