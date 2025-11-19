import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional
import json

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from services.collector import MassCollector

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PropertyScheduler")


class PropertyScheduler:
    """
    Scheduler para executar scraping automático de imóveis periodicamente.
    """
    
    def __init__(self, interval_hours: int = 6):
        """
        Args:
            interval_hours: Intervalo em horas para executar o scraping
        """
        self.interval_hours = interval_hours
        self.collector = MassCollector()
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.properties_db = []  # Simulação de banco (em produção, usar SQLAlchemy)
        
    async def start(self):
        """
        Inicia o scheduler em loop contínuo.
        """
        logger.info(f"Scheduler iniciado. Intervalo: {self.interval_hours} horas")
        self.is_running = True
        
        while self.is_running:
            try:
                await self._run_scraping()
                self.last_run = datetime.now()
                logger.info(f"Próxima execução em {self.interval_hours} horas")
                
                # Aguardar intervalo
                await asyncio.sleep(self.interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Erro no scheduler: {e}")
                # Retry após 5 minutos em caso de erro
                logger.info("Tentando novamente em 5 minutos...")
                await asyncio.sleep(300)
    
    async def _run_scraping(self):
        """
        Executa o scraping e salva os dados.
        """
        logger.info("=== Iniciando execução do scraper ===")
        
        try:
            # Coletar imóveis (2 páginas para ter um bom volume)
            properties = await self.collector.scrape_inventory(max_pages=2)
            
            logger.info(f"Scraping concluído: {len(properties)} imóveis coletados")
            
            # Salvar em "banco de dados" (simulado)
            self._save_to_database(properties)
            
            # Detectar mudanças importantes
            self._detect_changes(properties)
            
            logger.info("=== Execução concluída com sucesso ===")
            
        except Exception as e:
            logger.error(f"Erro durante scraping: {e}")
            raise
    
    def _save_to_database(self, properties: list):
        """
        Salva propriedades no banco de dados (simulado).
        Em produção, usar SQLAlchemy para persistência real.
        """
        timestamp = datetime.now().isoformat()
        
        for prop in properties:
            # Verificar se já existe
            existing = next((p for p in self.properties_db if p['link'] == prop['link']), None)
            
            if existing:
                # Atualizar propriedade existente
                existing.update(prop)
                existing['updated_at'] = timestamp
                logger.debug(f"Atualizado: {prop['title']}")
            else:
                # Adicionar nova propriedade
                prop['created_at'] = timestamp
                prop['updated_at'] = timestamp
                self.properties_db.append(prop)
                logger.info(f"Novo imóvel adicionado: {prop['title']}")
        
        logger.info(f"Banco de dados atualizado. Total: {len(self.properties_db)} imóveis")
    
    def _detect_changes(self, properties: list):
        """
        Detecta mudanças importantes (novos imóveis, mudanças de preço).
        """
        new_count = 0
        price_changed_count = 0
        
        for prop in properties:
            if prop.get('status') == 'NEW':
                new_count += 1
                logger.info(f"🆕 Novo imóvel: {prop['title']} - {prop['priceText']}")
            elif prop.get('status') == 'PRICE_CHANGED':
                price_changed_count += 1
                logger.warning(f"💰 Mudança de preço: {prop['title']}")
                # Aqui poderia disparar notificação
        
        if new_count > 0 or price_changed_count > 0:
            logger.info(f"Resumo: {new_count} novos, {price_changed_count} com mudança de preço")
    
    def stop(self):
        """
        Para o scheduler.
        """
        logger.info("Parando scheduler...")
        self.is_running = False
    
    def get_properties(self) -> list:
        """
        Retorna todas as propriedades do banco.
        """
        return self.properties_db
    
    def get_status(self) -> dict:
        """
        Retorna status do scheduler.
        """
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "interval_hours": self.interval_hours,
            "total_properties": len(self.properties_db),
            "next_run": (self.last_run + timedelta(hours=self.interval_hours)).isoformat() if self.last_run else "Aguardando primeira execução"
        }


# Instância global do scheduler (será usada pelo main.py)
scheduler = PropertyScheduler(interval_hours=6)


async def run_scheduler_forever():
    """
    Função auxiliar para rodar o scheduler.
    """
    await scheduler.start()


if __name__ == "__main__":
    # Teste - rodar uma única vez
    logger.info("Modo teste - executando scraping único")
    asyncio.run(scheduler._run_scraping())
    print(json.dumps(scheduler.get_properties(), indent=2, ensure_ascii=False))
