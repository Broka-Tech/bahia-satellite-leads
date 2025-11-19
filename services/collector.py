import sys
import asyncio
import json
import random
import logging
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from datetime import datetime

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MassCollector")

class MassCollector:
    """
    Módulo 'Mass Collector' - Scraper Resiliente para Lopes.com.br
    Atualizado para extrair dados completos de lançamentos imobiliários.
    """
    # URL correta com filtros de lançamentos na Bahia
    BASE_URL = "https://www.lopes.com.br/busca/venda/br/ba"
    FILTERS = "?estagio=real_estate&estagio=real_estate_parent&placeId=ChIJs6U8onwDFgcRBe2RtF9vkn4&origem=home"
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    def __init__(self):
        self.price_history_db = {} # Simulação de persistência simples (em memória por enquanto)

    def _get_random_user_agent(self):
        return random.choice(self.USER_AGENTS)

    async def scrape_inventory(self, max_pages: int = 1) -> List[Dict]:
        """
        Coleta o inventário de imóveis da Lopes.
        """
        logger.info(f"Iniciando coleta massiva. Max Pages: {max_pages}")
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self._get_random_user_agent())
            page = await context.new_page()

            for current_page in range(1, max_pages + 1):
                # Construir URL com paginação
                if current_page == 1:
                    url = f"{self.BASE_URL}{self.FILTERS}"
                else:
                    url = f"{self.BASE_URL}{self.FILTERS}&pagina={current_page}"
                
                logger.info(f"Acessando: {url}")
                
                try:
                    await page.goto(url, timeout=60000)
                    # Aguardar os cards de imóveis carregarem
                    await page.wait_for_selector("a.lead-button", timeout=15000)
                    
                    # Aguardar um pouco mais para garantir que todo o conteúdo carregou
                    await asyncio.sleep(2)

                    # Extração completa usando seletores corretos identificados no DOM
                    listings = await page.eval_on_selector_all("a.lead-button", """
                        elements => elements.map(el => {
                            // Título (h2 ou h3)
                            const titleEl = el.querySelector('h2') || el.querySelector('h3');
                            const title = titleEl?.innerText?.trim() || 'Sem Título';
                            
                            // Preço (elemento p com valor)
                            const priceElements = el.querySelectorAll('p');
                            let priceText = '0';
                            for (const p of priceElements) {
                                if (p.innerText.includes('R$')) {
                                    priceText = p.innerText.trim();
                                    break;
                                }
                            }
                            
                            // Link do imóvel
                            const link = el.href || '';
                            
                            // Fotos (pode haver múltiplas)
                            const photoElements = el.querySelectorAll('img');
                            const photos = Array.from(photoElements).map(img => img.src).filter(src => src && !src.includes('data:image'));
                            
                            // Detalhes (área, quartos, etc.) - em elementos li > p
                            const detailsList = el.querySelectorAll('ul > li > p');
                            const details = Array.from(detailsList).map(p => p.innerText.trim());
                            
                            // Localização - extrair texto que contenha endereço
                            const allText = el.innerText;
                            const lines = allText.split('\\n').map(l => l.trim()).filter(l => l);
                            
                            // Tentar identificar localização (geralmente tem vírgula e menciona bairro/cidade)
                            let location = '';
                            for (const line of lines) {
                                if (line.includes(',') && !line.includes('R$') && line.length > 10) {
                                    location = line;
                                    break;
                                }
                            }
                            
                            // Descrição - pegar texto mais longo que não seja título, preço ou localização
                            let description = '';
                            for (const line of lines) {
                                if (line.length > 50 && 
                                    line !== title && 
                                    line !== priceText && 
                                    line !== location &&
                                    !line.includes('R$')) {
                                    description = line;
                                    break;
                                }
                            }
                            
                            return { 
                                title, 
                                priceText, 
                                location, 
                                link,
                                photos,
                                details,
                                description
                            };
                        })
                    """)

                    logger.info(f"Encontrados {len(listings)} imóveis na página {current_page}")

                    for item in listings:
                        processed_item = self._process_item(item)
                        results.append(processed_item)
                    
                    # Random delay para stealth
                    await asyncio.sleep(random.uniform(3, 6))

                except Exception as e:
                    logger.error(f"Erro na página {current_page}: {e}")
                    continue

            await browser.close()
        
        logger.info(f"Coleta finalizada. {len(results)} imóveis encontrados.")
        return results

    def _process_item(self, item: Dict) -> Dict:
        """
        Processa dados brutos, extrai informações estruturadas e gerencia histórico de preços.
        """
        # Limpeza de preço (Ex: "R$ 1.500.000" -> 1500000.0)
        try:
            price_text = item.get('priceText', '0')
            # Remover "R$", ".", e substituir "," por "."
            price_clean_str = price_text.replace('R$', '').replace('.', '').replace(',', '.').strip()
            # Remover qualquer texto adicional (ex: "a partir de")
            price_clean_str = ''.join(c for c in price_clean_str if c.isdigit() or c == '.')
            price_clean = float(price_clean_str) if price_clean_str else 0.0
        except:
            price_clean = 0.0

        # Extrair características dos detalhes
        details = item.get('details', [])
        area = None
        bedrooms = None
        bathrooms = None
        parking = None
        
        for detail in details:
            detail_lower = detail.lower()
            # Área (m²)
            if 'm²' in detail_lower or 'área' in detail_lower:
                try:
                    # Extrair números
                    numbers = ''.join(c for c in detail if c.isdigit() or c == '.')
                    if numbers:
                        area = float(numbers)
                except:
                    pass
            # Quartos
            elif 'quarto' in detail_lower or 'dorm' in detail_lower:
                try:
                    bedrooms = int(''.join(c for c in detail if c.isdigit()))
                except:
                    pass
            # Banheiros
            elif 'banh' in detail_lower:
                try:
                    bathrooms = int(''.join(c for c in detail if c.isdigit()))
                except:
                    pass
            # Vagas
            elif 'vaga' in detail_lower:
                try:
                    parking = int(''.join(c for c in detail if c.isdigit()))
                except:
                    pass

        # Estruturar localização
        location_text = item.get('location', '')
        neighborhood = ''
        city = 'Salvador'  # Default
        
        if location_text:
            parts = location_text.split(',')
            if len(parts) >= 2:
                neighborhood = parts[-2].strip()  # Penúltima parte geralmente é o bairro
                city = parts[-1].strip()  # Última parte é a cidade
            elif len(parts) == 1:
                neighborhood = parts[0].strip()

        # Montar objeto estruturado
        processed = {
            'title': item.get('title', 'Sem Título'),
            'price': price_clean,
            'priceText': item.get('priceText', 'R$ 0'),
            'location': {
                'address': location_text,
                'neighborhood': neighborhood,
                'city': city,
                'state': 'BA'
            },
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'parking': parking,
            'type': 'Apartamento',  # Pode ser extraído do título se necessário
            'photos': item.get('photos', []),
            'description': item.get('description', ''),
            'link': item.get('link', ''),
            'collected_at': datetime.now().isoformat(),
            'source': 'Lopes'
        }
        
        # Price Watchdog Logic
        item_id = processed['link']
        if item_id in self.price_history_db:
            last_price = self.price_history_db[item_id][-1]['price']
            if price_clean != last_price:
                processed['status'] = 'PRICE_CHANGED'
                self.price_history_db[item_id].append({'price': price_clean, 'date': processed['collected_at']})
            else:
                processed['status'] = 'UNCHANGED'
        else:
            processed['status'] = 'NEW'
            self.price_history_db[item_id] = [{'price': price_clean, 'date': processed['collected_at']}]
        
        processed['price_history'] = self.price_history_db[item_id]
        return processed

if __name__ == "__main__":
    # Teste rápido
    collector = MassCollector()
    asyncio.run(collector.scrape_inventory(max_pages=1))
