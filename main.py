from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
import sys
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Fix for Playwright on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Importação dos Serviços
from services.lopes_scraper import LopesScraper  # Scraper otimizado para Windows
from services.refiner import ChameleonRefiner
from services.stealth_radar import StealthRadar
from services.validator import GhostValidator
from services.notifier import ShadowNotifier
from services.value_generator import ValueGenerator
from services.seo.aggregator import EntityAggregator
from services.seo.metadata import MetadataGenerator
from services.seo.schema import SchemaFactory
from fastapi.responses import Response

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BahiaSatelliteAPI")

app = FastAPI(
    title="Bahia Satellite - Stealth Predator Engine",
    description="Backend Headless para Inteligência Imobiliária",
    version="1.0.0"
)

# Configuração de CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, restringir para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciação dos Serviços
# NOTA: Em produção, usar injeção de dependência e gestão de segredos adequada (.env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") # Definir via variável de ambiente
collector = LopesScraper()  # Scraper otimizado para Windows (requests + BeautifulSoup)
refiner = ChameleonRefiner(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
radar = StealthRadar()
validator = GhostValidator()
notifier = ShadowNotifier()
value_gen = ValueGenerator(api_key=GEMINI_API_KEY)
seo_aggregator = EntityAggregator(api_key=GEMINI_API_KEY)
seo_metadata = MetadataGenerator(api_key=GEMINI_API_KEY)
seo_schema = SchemaFactory()

# Modelos Pydantic
class LeadUnlockRequest(BaseModel):
    phone: str
    username: Optional[str] = None
    source: str = "Web"

class RadarRequest(BaseModel):
    max_results: int = 10

class DossierRequest(BaseModel):
    property_id: str
    user_phone: str
    property_data: Optional[dict] = None # Opcional: passar dados se não tiver ID no banco

# Rotas

@app.get("/")
async def root():
    return {"status": "online", "system": "Bahia Satellite Stealth Engine"}

@app.get("/properties")
async def get_properties(pages: int = 1):
    """
    Vitrine: Coleta imóveis em tempo real da Lopes.com.br
    """
    try:
        logger.info(f"Coletando imóveis da Lopes (páginas: {pages})")
        
        # Usar o scraper síncrono (requests + BeautifulSoup)
        properties = collector.scrape_inventory(max_pages=pages)
        
        logger.info(f"✅ {len(properties)} imóveis coletados com sucesso")
        
        # Refinamento Opcional (se API Key estiver configurada)
        if refiner and len(properties) > 0:
            logger.info("Aplicando refinamento com IA...")
            for prop in properties[:5]:  # Refinar apenas os primeiros 5 para economizar tokens
                try:
                    refiner.refine_property(prop)
                except Exception as e:
                    logger.warning(f"Erro no refinamento: {e}")
        
        # Enriquecimento SEO
        for prop in properties:
            try:
                # 1. Gerar Metadados e Slug
                seo_data = seo_metadata.generate_seo_data(prop)
                prop.update(seo_data)
                
                # 2. Gerar Schema JSON-LD
                prop['schema_json'] = seo_schema.build_json_ld(prop)
            except Exception as e:
                logger.warning(f"Erro no SEO: {e}")

        return {"count": len(properties), "data": properties}
    
    except Exception as e:
        logger.error(f"Erro ao coletar imóveis: {e}")
        # Retornar erro em vez de mock data
        raise HTTPException(status_code=500, detail=f"Erro ao coletar imóveis: {str(e)}")

@app.post("/leads/unlock")
async def unlock_lead(request: LeadUnlockRequest, background_tasks: BackgroundTasks):
    """
    Entrada de Lead -> Validação Ghost -> Notificação Shadow
    """
    logger.info(f"Recebido lead para desbloqueio: {request.phone}")
    
    # 1. Validação Ghost (Assíncrona para não bloquear, mas aqui faremos await para resposta imediata se for rápido)
    is_valid = await validator.validate_phone(request.phone)
    
    if not is_valid:
        return {"status": "invalid_phone", "message": "Número não possui WhatsApp válido ou está formatado incorretamente."}
    
    # 2. Notificação Shadow (Background)
    lead_data = request.dict()
    lead_data['found_at'] = "Agora"
    
    # Disparar notificação
    notification_result = notifier.notify_broker(lead_data)
    
    return {
        "status": "success",
        "validation": "valid",
        "notification": notification_result
    }

@app.post("/admin/run-radar")
async def run_radar(request: RadarRequest):
    """
    Gatilho manual para o Stealth Radar (OSINT).
    """
    try:
        results = radar.run_radar(max_results_per_dork=request.max_results)
        return {"status": "completed", "leads_found": len(results), "data": results}
    except Exception as e:
        logger.error(f"Erro no Radar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-dossier")
async def generate_dossier(request: DossierRequest):
    """
    Gera um Dossiê de Investimento (PDF) para o lead.
    """
    logger.info(f"Gerando dossiê para {request.user_phone} - Imóvel {request.property_id}")

    # 1. Validar Telefone (Ghost Validator)
    is_valid = await validator.validate_phone(request.user_phone)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Número de WhatsApp inválido.")

    # 2. Obter dados do imóvel (Mockado se não passado)
    prop_data = request.property_data or {
        "title": "Imóvel Exemplo",
        "price": 1200000,
        "location": {"neighborhood": "Horto Florestal"},
        "area": 120
    }

    # 3. Gerar Tese de Investimento (Gemini)
    thesis = value_gen.generate_renovation_vision(prop_data)
    if "error" in thesis:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {thesis['error']}")

    # 4. Gerar PDF
    filename = f"dossier_{request.property_id}_{datetime.now().timestamp()}.pdf"
    pdf_path = value_gen.create_dossier_pdf(prop_data, thesis, filename)

    if not pdf_path:
        raise HTTPException(status_code=500, detail="Erro ao gerar PDF.")

    # 5. Retornar link (simulado) ou enviar via WhatsApp
    # Aqui retornamos o caminho local para teste
    return {
        "status": "success",
        "message": "Dossiê gerado com sucesso.",
        "download_url": f"/downloads/{filename}", # Rota fictícia de download
        "thesis_preview": thesis
    }

@app.get("/buildings/{slug}")
async def get_building_page(slug: str):
    """
    Módulo 1: Página de Condomínio (Landing Page SEO).
    """
    # Em produção, buscaria do banco de dados pelo slug
    # Aqui simulamos a extração e geração on-the-fly
    
    # Mock de dados do edifício
    building_name = slug.replace("-", " ").title()
    neighborhood = "Horto Florestal" # Mock
    
    description = seo_aggregator.generate_building_description(building_name, neighborhood)
    
    return {
        "name": building_name,
        "slug": slug,
        "description": description,
        "properties_available": [] # Listaria imóveis do banco
    }

@app.get("/sitemap.xml")
async def get_sitemap():
    """
    Módulo 4: Sitemap Dinâmico.
    """
    # Em produção, iterar sobre todos os imóveis e edifícios do banco
    base_url = "https://bahiasatellite.com"
    
    urls = []
    
    # 1. Home
    urls.append(f"""
    <url>
        <loc>{base_url}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """)
    
    # 2. Edifícios (Exemplo)
    buildings = ["mansao-wildberger", "edf-costa-pinto"]
    for b in buildings:
        urls.append(f"""
        <url>
            <loc>{base_url}/buildings/{b}</loc>
            <changefreq>weekly</changefreq>
            <priority>1.0</priority>
        </url>
        """)
        
    # 3. Imóveis (Exemplo)
    # Aqui chamaria o collector ou banco
    properties = [
        {"slug": "apartamento-4-quartos-horto-florestal-vista-mar"},
        {"slug": "cobertura-ondina-alto-padrao"}
    ]
    for p in properties:
        urls.append(f"""
        <url>
            <loc>{base_url}/imoveis/{p['slug']}</loc>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
        </url>
        """)
        
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {"".join(urls)}
    </urlset>
    """
    
    return Response(content=sitemap_content, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
