import logging
import random
import time
import re
from typing import List, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LopesScraper")


class LopesScraper:
    """
    Scraper otimizado para Windows usando requests + BeautifulSoup.
    Coleta lançamentos imobiliários da Lopes.com.br
    """
    
    BASE_URL = "https://www.lopes.com.br/busca/venda/br/ba"
    FILTERS = "?estagio=real_estate&estagio=real_estate_parent&placeId=ChIJs6U8onwDFgcRBe2RtF9vkn4&origem=home"
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.price_history_db = {}

    def scrape_inventory(self, max_pages: int = 1) -> List[Dict]:
        """
        Coleta inventário de imóveis.
        """
        logger.info(f"Iniciando coleta de imóveis. Max Pages: {max_pages}")
        results = []

        for current_page in range(1, max_pages + 1):
            if current_page == 1:
                url = f"{self.BASE_URL}{self.FILTERS}"
            else:
                url = f"{self.BASE_URL}{self.FILTERS}&pagina={current_page}"
            
            logger.info(f"Acessando: {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Encontrar todos os cards de imóveis
                property_cards = soup.find_all('a', class_='lead-button')
                
                if not property_cards:
                    logger.warning(f"Nenhum card encontrado na página {current_page}")
                    # Tentar outros seletores possíveis
                    property_cards = soup.find_all('div', class_='property-card') or soup.find_all('article')
                
                logger.info(f"Encontrados {len(property_cards)} imóveis na página {current_page}")
                
                for card in property_cards:
                    try:
                        item_data = self._extract_property_data(card)
                        if item_data:
                            processed = self._process_item(item_data)
                            results.append(processed)
                    except Exception as e:
                        logger.error(f"Erro ao extrair dados do card: {e}")
                        continue
                
                # Delay aleatório para evitar bloqueio
                time.sleep(random.uniform(2, 4))
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao acessar página {current_page}: {e}")
                continue
        
        logger.info(f"Coleta finalizada. {len(results)} imóveis encontrados.")
        return results

    def _extract_property_data(self, card) -> Dict:
        """
        Extrai dados de um card de imóvel.
        """
        data = {}
        
        # Link
        data['link'] = card.get('href', '')
        if data['link'] and not data['link'].startswith('http'):
            data['link'] = f"https://www.lopes.com.br{data['link']}"
        
        # Título (h2 ou h3)
        title_elem = card.find('h2') or card.find('h3')
        data['title'] = title_elem.get_text(strip=True) if title_elem else 'Sem Título'
        
        # Preço
        price_text = '0'
        price_elems = card.find_all('p')
        for p in price_elems:
            text = p.get_text(strip=True)
            if 'R$' in text:
                price_text = text
                break
        data['priceText'] = price_text
        
        # Fotos
        photos = []
        img_tags = card.find_all('img')
        for img in img_tags:
            src = img.get('src', '') or img.get('data-src', '')
            if src and 'data:image' not in src:
                if not src.startswith('http'):
                    src = f"https://www.lopes.com.br{src}"
                photos.append(src)
        data['photos'] = photos
        
        # Detalhes (área, quartos, etc.)
        details = []
        detail_items = card.find_all('li')
        for li in detail_items:
            detail_text = li.get_text(strip=True)
            if detail_text:
                details.append(detail_text)
        data['details'] = details
        
        # Localização e Descrição
        all_text = card.get_text('\n', strip=True)
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # Localização (linha com vírgula e sem R$, comprimento médio)
        location = ''
        for line in lines:
            if ',' in line and 'R$' not in line and 10 < len(line) < 100:
                location = line
                break
        data['location'] = location
        
        # Descrição (linha mais longa, excluindo título, preço e localização)
        description = ''
        for line in lines:
            if (len(line) > 50 and 
                line != data['title'] and 
                line != price_text and 
                line != location and
                'R$' not in line):
                description = line
                break
        data['description'] = description
        
        return data

    def _process_item(self, item: Dict) -> Dict:
        """
        Processa e estrutura os dados brutos do imóvel.
        """
        # Limpar preço
        try:
            price_text = item.get('priceText', '0')
            price_clean_str = re.sub(r'[^\d,.]', '', price_text.replace('R$', ''))
            price_clean_str = price_clean_str.replace('.', '').replace(',', '.')
            price_clean = float(price_clean_str) if price_clean_str else 0.0
        except:
            price_clean = 0.0

        # Extrair características
        details = item.get('details', [])
        area = None
        bedrooms = None
        bathrooms = None
        parking = None
        
        for detail in details:
            detail_lower = detail.lower()
            
            # Área
            if 'm²' in detail_lower or 'área' in detail_lower:
                try:
                    numbers = re.findall(r'\d+', detail)
                    if numbers:
                        area = float(numbers[0])
                except:
                    pass
            
            # Quartos
            elif 'quarto' in detail_lower or 'dorm' in detail_lower:
                try:
                    numbers = re.findall(r'\d+', detail)
                    if numbers:
                        bedrooms = int(numbers[0])
                except:
                    pass
            
            # Banheiros
            elif 'banh' in detail_lower:
                try:
                    numbers = re.findall(r'\d+', detail)
                    if numbers:
                        bathrooms = int(numbers[0])
                except:
                    pass
            
            # Vagas
            elif 'vaga' in detail_lower:
                try:
                    numbers = re.findall(r'\d+', detail)
                    if numbers:
                        parking = int(numbers[0])
                except:
                    pass

        # Estruturar localização
        location_text = item.get('location', '')
        neighborhood = ''
        city = 'Salvador'
        
        if location_text:
            parts = location_text.split(',')
            if len(parts) >= 2:
                neighborhood = parts[-2].strip()
                city = parts[-1].strip()
            elif len(parts) == 1:
                neighborhood = parts[0].strip()

        # Objeto estruturado
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
            'type': 'Apartamento',
            'photos': item.get('photos', []),
            'description': item.get('description', ''),
            'link': item.get('link', ''),
            'collected_at': datetime.now().isoformat(),
            'source': 'Lopes'
        }
        
        # Price tracking
        item_id = processed['link']
        if item_id and item_id in self.price_history_db:
            last_price = self.price_history_db[item_id][-1]['price']
            if price_clean != last_price:
                processed['status'] = 'PRICE_CHANGED'
                self.price_history_db[item_id].append({
                    'price': price_clean,
                    'date': processed['collected_at']
                })
            else:
                processed['status'] = 'UNCHANGED'
        else:
            processed['status'] = 'NEW'
            if item_id:
                self.price_history_db[item_id] = [{
                    'price': price_clean,
                    'date': processed['collected_at']
                }]
        
        processed['price_history'] = self.price_history_db.get(item_id, [])
        return processed


if __name__ == "__main__":
    # Teste
    scraper = LopesScraper()
    properties = scraper.scrape_inventory(max_pages=1)
    
    import json
    print(json.dumps(properties[:3], indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(properties)} imóveis coletados")
