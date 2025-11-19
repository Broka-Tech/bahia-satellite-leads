import google.generativeai as genai
import os
import json
import logging
from typing import Dict

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChameleonRefiner")

class ChameleonRefiner:
    """
    Módulo 'Chameleon Refiner' - IA Gemini para reescrita de anúncios.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key do Gemini é obrigatória.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def refine_property(self, property_data: Dict) -> Dict:
        """
        Analisa e reescreve a descrição do imóvel com base no preço.
        """
        price = property_data.get('price', 0)
        original_title = property_data.get('title', '')
        location = property_data.get('location', '')

        # Lógica Condicional de Tom
        if price > 1500000:
            tone = "Luxo, Exclusividade, Private, Sofisticação"
            target_audience = "Alto Padrão"
        else:
            tone = "Oportunidade, Investimento, Custo-Benefício, Smart Choice"
            target_audience = "Investidores/Primeiro Imóvel"

        prompt = f"""
        Atue como um Copywriter Imobiliário de Elite.
        Reescreva o título e crie uma breve descrição persuasiva para o seguinte imóvel:
        
        Título Original: {original_title}
        Localização: {location}
        Preço: R$ {price:,.2f}
        
        Diretrizes:
        - Tom de Voz: {tone}
        - Público Alvo: {target_audience}
        - O texto deve ser curto, direto e focado em conversão.
        - NÃO invente características que não estão explícitas, mas valorize a localização e o valor.
        
        Retorne APENAS um JSON no seguinte formato:
        {{
            "ai_title": "Novo Título Atraente",
            "ai_description": "Descrição persuasiva..."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # Tentativa de extrair JSON da resposta (pode vir com markdown ```json ... ```)
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            ai_data = json.loads(text_response)
            
            property_data['ai_title'] = ai_data.get('ai_title', original_title)
            property_data['ai_description'] = ai_data.get('ai_description', '')
            property_data['refined'] = True
            
            logger.info(f"Imóvel refinado com sucesso: {property_data.get('ai_title')}")

        except Exception as e:
            logger.error(f"Erro ao refinar imóvel com Gemini: {e}")
            property_data['refined'] = False
            property_data['ai_error'] = str(e)

        return property_data
