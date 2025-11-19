import { GoogleGenAI } from "@google/genai";
import { Property } from "../types";

// Safe initialization check
const apiKey = process.env.API_KEY;
let ai: GoogleGenAI | null = null;

if (apiKey) {
  ai = new GoogleGenAI({ apiKey: apiKey });
} else {
  console.warn("Gemini API Key not found. AI features will return mock data.");
}

export const generatePropertyTitle = async (property: Property): Promise<string> => {
  if (!ai) {
    // Fallback if no API key
    return `Oportunidade Exclusiva em ${property.location.neighborhood}`;
  }

  try {
    const model = 'gemini-2.5-flash';
    const prompt = `
      Atue como um copywriter imobiliário de luxo.
      Crie um título curto (máximo 45 caracteres), atraente e sofisticado para um imóvel com as seguintes características:
      Tipo: ${property.type}
      Bairro: ${property.location.neighborhood}, ${property.location.city}
      Preço: R$ ${property.price}
      Quartos: ${property.bedrooms}
      Destaques: ${property.tags.join(', ')}

      Retorne APENAS o texto do título, sem aspas.
    `;

    const response = await ai.models.generateContent({
      model: model,
      contents: prompt,
    });

    return response.text.trim();
  } catch (error) {
    console.error("Error generating title with Gemini:", error);
    return property.title;
  }
};

export const analyzeMarketValue = async (neighborhood: string): Promise<string> => {
    if (!ai) return "Dados de mercado indisponíveis no momento.";

    try {
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: `Forneça uma breve análise de mercado (uma frase de impacto) sobre a valorização imobiliária no bairro ${neighborhood} na Bahia para investidores.`,
      });
      return response.text.trim();
    } catch (e) {
        return "Região com alto potencial de valorização.";
    }
}