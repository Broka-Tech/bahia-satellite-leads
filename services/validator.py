import logging
from playwright.async_api import async_playwright

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GhostValidator")

class GhostValidator:
    """
    Módulo 'Ghost Validator' - Validação de WhatsApp sem API paga.
    """
    def __init__(self):
        pass

    async def validate_phone(self, phone_number: str) -> bool:
        """
        Valida se um número tem WhatsApp simulando a verificação de link wa.me.
        Nota: Esta é uma validação heurística baseada na resposta da página pública.
        """
        # Limpeza do número
        clean_number = "".join(filter(str.isdigit, phone_number))
        if not clean_number.startswith("55"):
            clean_number = "55" + clean_number # Assumindo BR se não tiver DDI

        url = f"https://api.whatsapp.com/send?phone={clean_number}"
        logger.info(f"Validando número: {clean_number}")

        is_valid = False

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=30000)
                
                # Lógica de detecção:
                # Se o botão "Iniciar conversa" ou "Continue to Chat" aparecer, o número é tecnicamente válido/formatado corretamente.
                # Se aparecer "Número de telefone inválido", então não existe.
                # O Playwright deve buscar por elementos que indiquem sucesso ou erro.
                
                # Esperar um pouco para carregamento
                await page.wait_for_load_state("networkidle")

                content = await page.content()
                
                # Verificar mensagens de erro comuns na página pública do WA
                if "Phone number shared via url is invalid" in content or "O número de telefone compartilhado através de url é inválido" in content:
                    is_valid = False
                    logger.info(f"Número {clean_number} INVÁLIDO.")
                else:
                    # Se não deu erro explícito e carregou a página de redirecionamento, assumimos válido preliminarmente
                    # Para certeza absoluta precisaria tentar abrir o web.whatsapp, mas isso exige login (QR Code), o que viola a premissa "Headless/No Login" para este escopo simples.
                    # A validação aqui é "Soft": O formato é aceito pelo gateway do WA?
                    is_valid = True
                    logger.info(f"Número {clean_number} VÁLIDO (Soft Check).")

            except Exception as e:
                logger.error(f"Erro na validação do número {clean_number}: {e}")
                is_valid = False # Fail safe

            await browser.close()

        return is_valid
