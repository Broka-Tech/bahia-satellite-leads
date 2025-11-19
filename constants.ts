import { Property } from './types';

export const BROKER_PHONE = '5571992392300';
export const BROKER_NAME = 'Roberto Flaminio Vasconcelos';
export const BROKER_CRECI = 'CRECI BA 30716';
export const BROKER_INSTAGRAM_URL = 'https://www.instagram.com/rflaminios/';

// URL direta da imagem fornecida pelo usuário
export const BROKER_IMAGE = 'https://i.imgur.com/h15aF3f.png'; 

// Imagem de alta qualidade remetendo ao Farol da Barra/Orla de Salvador à noite/crepúsculo
export const HERO_IMAGE = 'https://images.unsplash.com/photo-1574008566286-6b9874bb8b52?q=80&w=2574&auto=format&fit=crop'; 

export const NEIGHBORHOODS = [
  { city: 'Salvador', name: 'Pituba' },
  { city: 'Salvador', name: 'Barra' },
  { city: 'Salvador', name: 'Horto Florestal' },
  { city: 'Salvador', name: 'Caminho das Árvores' },
  { city: 'Salvador', name: 'Vitória' },
  { city: 'Salvador', name: 'Graça' },
  { city: 'Salvador', name: 'Ondina' },
  { city: 'Lauro de Freitas', name: 'Buraquinho' },
  { city: 'Lauro de Freitas', name: 'Alphaville Litoral Norte' },
  { city: 'Lauro de Freitas', name: 'Vilas do Atlântico' },
  { city: 'Mata de São João', name: 'Praia do Forte' },
];

export const MOCK_PROPERTIES: Property[] = [
  {
    id: '1',
    title: 'Apartamento Alto Padrão com Vista Mar',
    location: { city: 'Salvador', neighborhood: 'Vitória' },
    price: 3500000,
    bedrooms: 4,
    area: 280,
    imageUrl: 'https://images.unsplash.com/photo-1512918760532-3ed00af80147?auto=format&fit=crop&w=800&q=80',
    type: 'apartment',
    isExclusive: true,
    tags: ['Vista Mar', 'Alto Padrão', 'Pier'],
  },
  {
    id: '2',
    title: 'Studio Compacto perto da Praia',
    location: { city: 'Salvador', neighborhood: 'Barra' },
    price: 420000,
    bedrooms: 1,
    area: 45,
    imageUrl: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80',
    type: 'apartment',
    tags: ['Investimento', 'Airbnb'],
  },
  {
    id: '3',
    title: 'Casa em Condomínio Fechado',
    location: { city: 'Lauro de Freitas', neighborhood: 'Alphaville Litoral Norte' },
    price: 1850000,
    bedrooms: 4,
    area: 350,
    imageUrl: 'https://images.unsplash.com/photo-1600596542815-2495db9dc2c3?auto=format&fit=crop&w=800&q=80',
    type: 'house',
    tags: ['Condomínio', 'Segurança'],
  },
  {
    id: '4',
    title: '3/4 com Dependência Completa',
    location: { city: 'Salvador', neighborhood: 'Pituba' },
    price: 680000,
    bedrooms: 3,
    area: 110,
    imageUrl: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80',
    type: 'apartment',
    tags: ['Nascente', 'Ventilado'],
  },
  {
    id: '5',
    title: 'Cobertura Duplex Luxuosa',
    location: { city: 'Salvador', neighborhood: 'Horto Florestal' },
    price: 4200000,
    bedrooms: 5,
    area: 500,
    imageUrl: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80',
    type: 'penthouse',
    isExclusive: true,
    tags: ['Exclusivo', 'Piscina Privativa'],
  },
  {
    id: '6',
    title: 'Village Pé na Areia',
    location: { city: 'Mata de São João', neighborhood: 'Praia do Forte' },
    price: 1200000,
    bedrooms: 2,
    area: 90,
    imageUrl: 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=800&q=80',
    type: 'house',
    tags: ['Veraneio', 'Lazer'],
  },
  {
    id: '7',
    title: 'Oportunidade MCMV',
    location: { city: 'Lauro de Freitas', neighborhood: 'Buraquinho' },
    price: 280000,
    bedrooms: 2,
    area: 55,
    imageUrl: 'https://images.unsplash.com/photo-1484154218962-a1c002085d2f?auto=format&fit=crop&w=800&q=80',
    type: 'apartment',
    tags: ['Primeiro Imóvel', 'Financiável'],
  },
  {
    id: '8',
    title: 'Mansão Suspensa',
    location: { city: 'Salvador', neighborhood: 'Caminho das Árvores' },
    price: 2200000,
    bedrooms: 4,
    area: 210,
    imageUrl: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80',
    type: 'apartment',
    tags: ['Novo', 'Infraestrutura Completa'],
  }
];