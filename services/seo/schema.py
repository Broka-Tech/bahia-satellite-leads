from typing import Dict, Any, List

class SchemaFactory:
    """
    Módulo 3: Schema Markup Factory
    Gera JSON-LD para Rich Snippets do Google.
    """
    
    def build_json_ld(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói o objeto RealEstateListing conforme schema.org.
        """
        price = property_data.get('price', 0)
        currency = "BRL"
        
        schema = {
            "@context": "https://schema.org",
            "@type": "RealEstateListing",
            "name": property_data.get('seo_title', property_data.get('title')),
            "description": property_data.get('meta_description', property_data.get('description')),
            "url": f"https://bahiasatellite.com/imoveis/{property_data.get('seo_slug', '')}",
            "image": property_data.get('images', []),
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Salvador",
                "addressRegion": "BA",
                "addressCountry": "BR"
            },
            "offers": {
                "@type": "Offer",
                "price": str(price),
                "priceCurrency": currency,
                "availability": "https://schema.org/InStock"
            }
        }
        
        # Adicionar dados opcionais se existirem
        if 'bedrooms' in property_data:
            schema['numberOfRooms'] = property_data['bedrooms']
            
        if 'area' in property_data:
            schema['floorSize'] = {
                "@type": "QuantitativeValue",
                "value": property_data['area'],
                "unitCode": "MTK" # Metros quadrados
            }

        return schema
