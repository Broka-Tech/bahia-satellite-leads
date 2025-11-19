import React, { useState, useEffect } from 'react';
import { Lock, Unlock, MessageCircle, ShieldCheck, AlertCircle } from 'lucide-react';
import { Property } from '../../types';
import { BROKER_PHONE } from '../../constants';

interface UnlockModalProps {
  isOpen: boolean;
  onClose: () => void;
  property: Property;
}

export const UnlockModal: React.FC<UnlockModalProps> = ({ isOpen, onClose, property }) => {
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Adaptive Logic
  const isLuxury = property.price >= 1500000;
  const isEconomy = property.price <= 500000;

  const getModalConfig = () => {
    if (isLuxury) {
      return {
        title: "Acesso Private",
        subtitle: "Este imóvel faz parte da nossa coleção exclusiva. Desbloqueie detalhes confidencias e planta baixa.",
        buttonText: "Solicitar Acesso VIP",
        icon: <ShieldCheck className="w-12 h-12 text-yellow-500 mb-4" />,
        colorClass: "border-yellow-500/50 bg-yellow-500/10",
        btnColor: "bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 text-black font-bold"
      };
    } else if (isEconomy) {
      return {
        title: "Oportunidade Única",
        subtitle: "Verifique as condições especiais de financiamento e valor final negociável para esta unidade.",
        buttonText: "Ver Parcelas e Descontos",
        icon: <Unlock className="w-12 h-12 text-green-500 mb-4" />,
        colorClass: "border-green-500/50 bg-green-500/10",
        btnColor: "bg-green-600 hover:bg-green-500 text-white font-semibold"
      };
    } else {
      return {
        title: "Desbloquear Detalhes",
        subtitle: "Fale diretamente com o corretor responsável para agendar uma visita ou receber o vídeo tour.",
        buttonText: "Falar com Corretor",
        icon: <MessageCircle className="w-12 h-12 text-blue-500 mb-4" />,
        colorClass: "border-blue-500/50 bg-blue-500/10",
        btnColor: "bg-blue-600 hover:bg-blue-500 text-white font-semibold"
      };
    }
  };

  const config = getModalConfig();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Immediate action (Backend removed)
    
    // Construct WhatsApp Message
    const message = `Olá, meu nome é ${name}. Gostaria de desbloquear as informações do imóvel: ${property.title} (Ref: ${property.id}) no bairro ${property.location.neighborhood}. Valor: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(property.price)}`;
    
    const whatsappUrl = `https://wa.me/${BROKER_PHONE}?text=${encodeURIComponent(message)}`;
    
    window.open(whatsappUrl, '_blank');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-[#121212] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-500 hover:text-white transition-colors"
        >
          ✕
        </button>

        <div className="p-8 flex flex-col items-center text-center">
          {config.icon}
          
          <h2 className="text-2xl font-bold text-white mb-2">{config.title}</h2>
          <p className="text-zinc-400 text-sm mb-6 leading-relaxed">
            {config.subtitle}
          </p>

          {/* Price Highlight */}
          <div className={`w-full py-3 mb-6 rounded-lg border ${config.colorClass} flex items-center justify-center gap-2`}>
            <span className="text-xs uppercase tracking-widest opacity-70">Valor de Referência</span>
            <span className="font-mono font-bold text-lg">
              {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(property.price)}
            </span>
          </div>

          <form onSubmit={handleSubmit} className="w-full space-y-4">
            <input
              type="text"
              required
              placeholder="Seu Nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary transition-colors placeholder:text-zinc-600"
            />
            <input
              type="tel"
              required
              placeholder="WhatsApp (DD) 99999-9999"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary transition-colors placeholder:text-zinc-600"
            />
            
            <button 
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 rounded-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 shadow-lg ${config.btnColor}`}
            >
              {isLoading ? (
                <span className="animate-pulse">Processando...</span>
              ) : (
                <>
                  <span>{config.buttonText}</span>
                  {isLuxury ? <Lock size={16} /> : <MessageCircle size={16} />}
                </>
              )}
            </button>
          </form>

          <p className="mt-4 text-[10px] text-zinc-600 flex items-center gap-1">
            <AlertCircle size={10} />
            Seus dados são enviados com criptografia para a equipe Lopes Imóveis.
          </p>
        </div>
      </div>
    </div>
  );
};