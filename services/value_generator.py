import google.generativeai as genai
import logging
import json
import os
from typing import Dict, Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ValueGenerator")

class ValueGenerator:
    """
    Módulo 'Value Generator Engine' - Isca de Alto Valor.
    Gera teses de investimento e guias de bairro.
    """
    def __init__(self, api_key: str):
        if not api_key:
            logger.warning("API Key do Gemini não fornecida. ValueGenerator funcionará em modo limitado.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def generate_renovation_vision(self, property_data: Dict) -> Dict:
        """
        Gera uma tese de investimento para imóveis com potencial.
        """
        if not hasattr(self, 'model'):
            return {"error": "Gemini API not configured"}

        prompt = f"""
        Atue como um Consultor de Investimentos Imobiliários em Salvador.
        Analise este imóvel:
        Título: {property_data.get('title')}
        Bairro: {property_data.get('location', {}).get('neighborhood', 'Salvador')}
        Preço: R$ {property_data.get('price', 0):,.2f}
        Área: {property_data.get('area', 0)} m²
        
        Crie um resumo executivo de 3 pontos:
        1. 'O Potencial Oculto': O que pode ser melhorado (ex: integrar varanda, modernizar layout).
        2. 'Estimativa de Valorização': Se reformado, quanto valeria (use +30% como base conservadora, mas ajuste conforme o perfil).
        3. 'Perfil de Comprador': Para quem é ideal (Investidor, Família, Single).

        Retorne APENAS um JSON no seguinte formato:
        {{
            "hidden_potential": "Texto sobre potencial...",
            "valuation_estimate": "Texto sobre valorização...",
            "buyer_profile": "Texto sobre perfil..."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            thesis = json.loads(text_response)
            return thesis
        except Exception as e:
            logger.error(f"Erro ao gerar tese de investimento: {e}")
            return {"error": str(e)}

    def generate_neighborhood_guide(self, neighborhood: str) -> Dict:
        """
        Gera um 'Inside Scoop' sobre o bairro.
        """
        if not hasattr(self, 'model'):
            return {"error": "Gemini API not configured"}

        prompt = f"""
        Escreva um 'Inside Scoop' de luxo sobre morar no bairro {neighborhood} em Salvador.
        Cite os 2 melhores restaurantes e 1 segredo local que apenas moradores sabem.
        
        Retorne APENAS um JSON no seguinte formato:
        {{
            "vibe": "Descrição da vibe do bairro...",
            "top_spots": ["Restaurante 1", "Restaurante 2"],
            "local_secret": "O segredo local..."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            guide = json.loads(text_response)
            return guide
        except Exception as e:
            logger.error(f"Erro ao gerar guia de bairro: {e}")
            return {"error": str(e)}

    def create_dossier_pdf(self, property_data: Dict, thesis: Dict, filename: str = "dossier.pdf") -> str:
        """
        Gera um PDF simples com a tese de investimento.
        """
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, "Bahia Satellite | Investment Dossier")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Imóvel: {property_data.get('title', 'N/A')}")
            c.drawString(50, height - 100, f"Valor Atual: R$ {property_data.get('price', 0):,.2f}")

            # Thesis Content
            y_position = height - 150
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "1. O Potencial Oculto")
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position - 20, thesis.get('hidden_potential', 'N/A')[:90] + "...") # Truncate for simple PDF
            
            y_position -= 60
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "2. Estimativa de Valorização")
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position - 20, thesis.get('valuation_estimate', 'N/A'))

            y_position -= 60
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "3. Perfil de Comprador")
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position - 20, thesis.get('buyer_profile', 'N/A'))

            # Footer
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, 50, "Gerado automaticamente por Bahia Satellite AI Engine.")
            c.drawString(50, 35, f"Data: {datetime.now().strftime('%d/%m/%Y')}")

            c.save()
            logger.info(f"PDF gerado com sucesso: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            return ""
