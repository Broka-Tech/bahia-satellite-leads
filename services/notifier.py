import logging
import urllib.parse

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ShadowNotifier")

class ShadowNotifier:
    """
    Módulo 'Shadow Notifier' - Notificações Stealth.
    """
    BROKER_NUMBER = "5571992392300"

    def __init__(self):
        pass

    def notify_broker(self, lead_data: dict):
        """
        Gera o link de notificação ou simula o envio.
        Em um cenário real com API paga, aqui seria o request.
        No modo Stealth/Free, geramos um link 'wa.me' pré-preenchido para o corretor clicar.
        """
        try:
            message = f"🚨 *NOVO LEAD DETECTADO* 🚨\n\n" \
                      f"👤 Nome/User: {lead_data.get('username', 'N/A')}\n" \
                      f"📱 Contato: {lead_data.get('phone', 'N/A')}\n" \
                      f"🔗 Origem: {lead_data.get('source', 'N/A')}\n" \
                      f"💡 Interesse: {lead_data.get('interest', 'Imóvel')}\n" \
                      f"⏰ Horário: {lead_data.get('found_at', 'Agora')}"

            encoded_message = urllib.parse.quote(message)
            notify_url = f"https://wa.me/{self.BROKER_NUMBER}?text={encoded_message}"
            
            logger.info(f"Notificação gerada para o corretor: {notify_url}")
            
            # Em um sistema automatizado real, poderíamos usar o Playwright para enviar isso via Web WhatsApp,
            # mas isso exigiria manter uma sessão ativa (QR Code). 
            # Retornamos a URL para log ou ação manual/frontend.
            return {
                "status": "notification_prepared",
                "notify_url": notify_url,
                "message_preview": message
            }

        except Exception as e:
            logger.error(f"Erro ao gerar notificação: {e}")
            return {"status": "error", "details": str(e)}
