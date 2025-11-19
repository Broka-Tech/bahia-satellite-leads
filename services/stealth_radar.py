import logging
import random
import time
from typing import List, Dict
import json
from googlesearch import search

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StealthRadar")

class StealthRadar:
    """
    Módulo 'Stealth Radar' - OSINT via Google Dorking.
    """
    KEYWORDS_ELITE = ["Médico", "Advogado", "CEO", "Sócio", "Diretor", "Empresário", "Cirurgião"]
    TARGET_SITE = "site:instagram.com"
    LOCATION = "Salvador"

    def __init__(self):
        pass

    def generate_dorks(self) -> List[str]:
        """
        Gera combinações de Dorks para busca.
        """
        dorks = []
        for keyword in self.KEYWORDS_ELITE:
            # Ex: site:instagram.com "Salvador" "Médico"
            dork = f'{self.TARGET_SITE} "{self.LOCATION}" "{keyword}"'
            dorks.append(dork)
        return dorks

    def run_radar(self, max_results_per_dork: int = 10) -> List[Dict]:
        """
        Executa a varredura OSINT.
        """
        logger.info("Iniciando Stealth Radar...")
        all_leads = []
        dorks = self.generate_dorks()

        for dork in dorks:
            logger.info(f"Executando Dork: {dork}")
            try:
                # Pausa aleatória para evitar bloqueio do Google
                time.sleep(random.uniform(5, 15))
                
                results = search(dork, num_results=max_results_per_dork, advanced=True)
                
                for result in results:
                    lead = self._parse_result(result)
                    if lead:
                        all_leads.append(lead)
            
            except Exception as e:
                logger.error(f"Erro ao executar dork '{dork}': {e}")
                continue

        logger.info(f"Radar finalizado. {len(all_leads)} prospects encontrados.")
        return all_leads

    def _parse_result(self, result) -> Dict:
        """
        Extrai informações úteis do resultado da busca.
        """
        try:
            url = result.url
            title = result.title
            description = result.description

            # Extrair username da URL do Instagram
            if "instagram.com/" in url:
                parts = url.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0]
                else:
                    username = "unknown"
            else:
                return None # Ignorar se não for Instagram (segurança)

            return {
                "source": "Instagram OSINT",
                "username": username,
                "profile_url": url,
                "snippet_title": title,
                "snippet_description": description,
                "detected_keyword": next((k for k in self.KEYWORDS_ELITE if k.lower() in (title + description).lower()), "Unknown"),
                "found_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            logger.warning(f"Erro ao fazer parse do resultado: {e}")
            return None

if __name__ == "__main__":
    radar = StealthRadar()
    results = radar.run_radar(max_results_per_dork=2)
    print(json.dumps(results, indent=2, ensure_ascii=False))
