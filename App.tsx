import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Filters } from './components/Filters';
import { UnlockModal } from './components/ui/UnlockModal';
import { Property, FilterState } from './types';
import { MOCK_PROPERTIES, HERO_IMAGE, BROKER_NAME, BROKER_CRECI, BROKER_IMAGE, BROKER_INSTAGRAM_URL, BROKER_PHONE, NEIGHBORHOODS } from './constants';
import { MapPin, BedDouble, Maximize, Sparkles, ArrowDown, Search, User, Menu, ShieldCheck, ChevronRight, Instagram, Filter, TrendingUp, Lock, Calculator, CheckCircle2, MessageCircle } from 'lucide-react';
// @ts-ignore
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Enhanced Mock Data with History
const ENHANCED_MOCK_PROPERTIES = MOCK_PROPERTIES.map(p => ({
  ...p,
  priceHistory: [
    { date: 'Jan', price: p.price * 0.92 },
    { date: 'Mar', price: p.price * 0.95 },
    { date: 'Mai', price: p.price * 0.98 },
    { date: 'Jul', price: p.price }
  ]
}));

const App: React.FC = () => {
  // Direct data usage without backend simulation
  // const properties = ENHANCED_MOCK_PROPERTIES; // Replaced by state

  const [filters, setFilters] = useState<FilterState>({
    priceRange: [0, 5000000],
    neighborhoods: [],
    profile: 'all',
    bedrooms: null
  });
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [activeTab, setActiveTab] = useState<'marketplace' | 'valuation'>('marketplace');

  const marketplaceRef = useRef<HTMLDivElement>(null);

  // Handle Scroll for Navbar transparency
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // API Integration
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        setIsLoading(true);
        // Fallback to mock if API fails or for initial demo if backend is offline
        try {
          const response = await fetch('http://localhost:8000/properties?pages=1');
          if (!response.ok) throw new Error('API Error');
          const data = await response.json();

          // Map Backend Data to Frontend Type
          const mappedProperties: Property[] = data.data.map((item: any, index: number) => ({
            id: item.link || `prop-${index}`,
            title: item.title,
            location: {
              city: 'Salvador',
              neighborhood: item.location.split(',')[0]?.trim() || 'Localização Privilegiada'
            },
            price: item.price,
            bedrooms: Math.floor(Math.random() * 3) + 2, // Mocking missing data
            area: Math.floor(Math.random() * 150) + 60, // Mocking missing data
            imageUrl: MOCK_PROPERTIES[index % MOCK_PROPERTIES.length].imageUrl, // Cycling mock images
            type: 'apartment',
            tags: ['Premium', 'Vista Mar'],
            aiGeneratedTitle: item.ai_title,
            priceHistory: item.price_history || []
          }));

          if (mappedProperties.length > 0) {
            setProperties(mappedProperties);
          } else {
            setProperties(ENHANCED_MOCK_PROPERTIES); // Fallback if empty
          }
        } catch (err) {
          console.warn("Backend unavailable, using mock data:", err);
          setProperties(ENHANCED_MOCK_PROPERTIES);
        }
      } catch (error) {
        console.error("Error fetching properties:", error);
        setProperties(ENHANCED_MOCK_PROPERTIES);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProperties();
  }, []);

  // Client-Side Filtering
  const filteredProperties = useMemo(() => {
    return properties.filter(p => {
      const matchesPrice = p.price >= filters.priceRange[0] && p.price <= filters.priceRange[1];
      const matchesNeighborhood = filters.neighborhoods.length === 0 || filters.neighborhoods.includes(p.location.neighborhood);
      const matchesBedrooms = filters.bedrooms === null ||
        (filters.bedrooms === 5 ? p.bedrooms >= 5 : p.bedrooms === filters.bedrooms);

      return matchesPrice && matchesNeighborhood && matchesBedrooms;
    });
  }, [properties, filters]);

  const handleUnlockClick = (property: Property) => {
    setSelectedProperty(property);
    setIsModalOpen(true);
  };

  const scrollToMarketplace = () => {
    setActiveTab('marketplace');
    setTimeout(() => {
      marketplaceRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-zinc-100 font-sans selection:bg-blue-600/30 overflow-x-hidden flex flex-col items-center">

      {/* Navigation Header */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-black/90 backdrop-blur-lg border-b border-white/5 py-4 shadow-2xl' : 'bg-transparent py-6'}`}>
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between w-full">
          <div className="flex items-center gap-2 opacity-80 hover:opacity-100 transition-opacity cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
              <ShieldCheck size={12} className="text-white" />
            </div>
            <span className="text-sm font-medium tracking-wide text-zinc-300">
              Bahia Satellite <span className="text-zinc-500">| Tech</span>
            </span>
          </div>

          <div className="hidden lg:flex items-center gap-8 text-sm font-medium text-zinc-300">
            <button onClick={() => setActiveTab('marketplace')} className={`transition-colors hover:text-white pb-0.5 ${activeTab === 'marketplace' ? 'text-white border-b border-blue-500' : ''}`}>Imóveis Premium</button>
            <button onClick={() => setActiveTab('valuation')} className={`transition-colors hover:text-white pb-0.5 ${activeTab === 'valuation' ? 'text-white border-b border-blue-500' : ''}`}>Avaliar Meu Imóvel</button>
          </div>

          <div className="flex items-center gap-4">
            <button className="hidden md:flex items-center gap-2 px-5 py-2 text-xs font-bold uppercase tracking-widest text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all shadow-lg shadow-blue-900/20">
              <User size={14} />
              Área do Cliente
            </button>
            <button onClick={() => setShowMobileFilters(true)} className="lg:hidden text-white">
              <Menu size={24} />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Broker Profile Layout */}
      {activeTab === 'marketplace' && (
        <section className="relative w-full min-h-[100vh] flex flex-col items-center justify-center pt-32 pb-16 overflow-hidden bg-[#050505]">
          {/* Background Image with heavy dark overlay */}
          <div className="absolute inset-0 z-0">
            <img
              src={HERO_IMAGE}
              alt="Background"
              className="w-full h-full object-cover opacity-30 blur-sm"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-[#050505]/90 to-[#050505]"></div>
          </div>

          <div className="relative z-10 flex flex-col items-center text-center px-6 animate-in fade-in zoom-in duration-700 slide-in-from-bottom-8">

            {/* 1. Lopes Badge - Top Element */}
            <div className="flex items-center gap-4 p-2 pr-6 bg-black/60 border border-white/10 rounded-xl mb-10 backdrop-blur-xl shadow-2xl ring-1 ring-white/5 hover:scale-105 transition-transform cursor-default select-none">
              <div className="w-10 h-10 bg-[#cc0000] flex items-center justify-center text-white font-serif font-bold text-2xl rounded-lg shadow-inner">L</div>
              <div className="flex flex-col text-left">
                <span className="text-white text-sm font-bold leading-none mb-0.5">Lopes Imóveis</span>
                <span className="text-zinc-400 text-[10px] uppercase tracking-[0.2em]">Parceiro Oficial</span>
              </div>
            </div>

            {/* 2. Broker Photo Card */}
            <div className="relative mb-8 group perspective-1000">
              <div className="w-72 h-96 rounded-2xl overflow-hidden border-4 border-zinc-800 bg-zinc-900 shadow-[0_20px_60px_rgba(0,0,0,0.9)] relative transform transition-transform duration-500 group-hover:scale-[1.01]">
                <img
                  src={BROKER_IMAGE}
                  alt={BROKER_NAME}
                  className="w-full h-full object-cover opacity-95 hover:opacity-100 transition-opacity"
                />
                {/* Subtle gradient at bottom of image */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"></div>
              </div>

              {/* CRECI Floating Badge on Image */}
              <div className="absolute -bottom-4 right-6 bg-blue-600 text-white px-5 py-2 rounded-full flex items-center gap-2 shadow-xl border-4 border-[#050505] hover:bg-blue-500 transition-colors z-20">
                <ShieldCheck size={16} />
                <span className="text-xs font-bold tracking-wide">CRECI</span>
              </div>
            </div>

            {/* 3. Personal Info & Bio */}
            <div className="space-y-3 max-w-lg mt-2">
              <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">{BROKER_NAME}</h1>
              <p className="text-[#ff9999] font-bold text-sm tracking-[0.15em] uppercase">{BROKER_CRECI}</p>

              <div className="h-px w-24 bg-gradient-to-r from-transparent via-zinc-700 to-transparent mx-auto my-6"></div>

              <p className="text-zinc-300 text-base md:text-lg leading-relaxed font-light px-4">
                Especialista com <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-200 to-zinc-400 font-bold">20+ anos de experiência</span> em análise de crédito, aprovação de financiamentos e vendas de imóveis premium na Bahia.
              </p>
            </div>

            {/* 4. Modern Contact Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mt-8 w-full max-w-md justify-center px-6">
              <a
                href={BROKER_INSTAGRAM_URL}
                target="_blank"
                rel="noreferrer"
                className="flex-1 px-6 py-3.5 rounded-xl bg-zinc-900/80 border border-zinc-800 text-zinc-300 hover:text-white hover:border-pink-500/50 hover:bg-zinc-800 hover:shadow-[0_0_20px_rgba(236,72,153,0.15)] transition-all duration-300 flex items-center justify-center gap-3 backdrop-blur-sm group"
              >
                <div className="p-1.5 rounded-full bg-zinc-800 group-hover:bg-pink-500/20 transition-colors">
                  <Instagram size={18} className="group-hover:text-pink-500 transition-colors" />
                </div>
                <span className="text-sm font-semibold tracking-wide">@rflaminios</span>
              </a>

              <a
                href={`https://wa.me/${BROKER_PHONE}`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 px-6 py-3.5 rounded-xl bg-zinc-900/80 border border-zinc-800 text-zinc-300 hover:text-white hover:border-green-500/50 hover:bg-zinc-800 hover:shadow-[0_0_20px_rgba(34,197,94,0.15)] transition-all duration-300 flex items-center justify-center gap-3 backdrop-blur-sm group"
              >
                <div className="p-1.5 rounded-full bg-zinc-800 group-hover:bg-green-500/20 transition-colors">
                  <MessageCircle size={18} className="group-hover:text-green-500 transition-colors" />
                </div>
                <span className="text-sm font-semibold tracking-wide">WhatsApp</span>
              </a>
            </div>

            <button
              onClick={scrollToMarketplace}
              className="mt-12 text-zinc-600 hover:text-white transition-colors animate-bounce p-4"
              aria-label="Ver Imóveis"
            >
              <ArrowDown size={28} />
            </button>
          </div>
        </section>
      )}

      {/* Main Content Area */}
      <div ref={marketplaceRef} className="w-full bg-[#050505] border-t border-zinc-900 relative z-20 flex justify-center min-h-screen">

        {activeTab === 'valuation' ? (
          <ValuationModule />
        ) : (
          <div className="w-full max-w-7xl flex flex-col lg:flex-row min-h-screen">

            {/* Mobile Filters Drawer */}
            <div className={`fixed inset-0 z-[60] lg:hidden transition-all duration-300 ${showMobileFilters ? 'visible opacity-100' : 'invisible opacity-0'}`}>
              <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={() => setShowMobileFilters(false)}
              />
              <div className={`absolute left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-[#09090b] border-r border-zinc-800 transform transition-transform duration-300 shadow-2xl ${showMobileFilters ? 'translate-x-0' : '-translate-x-full'}`}>
                <Filters
                  filters={filters}
                  setFilters={setFilters}
                  activeCount={filteredProperties.length}
                  onClose={() => setShowMobileFilters(false)}
                  className="p-6"
                />
              </div>
            </div>

            {/* Desktop Sidebar */}
            <div className="hidden lg:block lg:h-screen lg:sticky lg:top-0 z-20 bg-[#050505]">
              <Filters
                filters={filters}
                setFilters={setFilters}
                activeCount={filteredProperties.length}
                className="p-6 w-72 border-r border-white/5 pt-28"
              />
            </div>

            {/* Grid Area */}
            <main className="flex-1 p-4 lg:p-10 pt-28 lg:pt-10">
              <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <TrendingUp className="text-blue-500" size={24} />
                  Oportunidades Monitoradas
                </h2>

                <button
                  onClick={() => setShowMobileFilters(true)}
                  className="lg:hidden flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-bold uppercase tracking-wider text-zinc-300 transition-colors w-full justify-center"
                >
                  <Filter size={14} />
                  Filtros
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                {filteredProperties.length > 0 ? filteredProperties.map((property) => (
                  <PropertyCard
                    key={property.id}
                    property={property}
                    onUnlock={() => handleUnlockClick(property)}
                  />
                )) : (
                  <div className="col-span-full py-32 flex flex-col items-center justify-center text-center text-zinc-500 border border-dashed border-zinc-800 rounded-2xl bg-zinc-900/10">
                    <Search size={48} className="mb-4 opacity-30" />
                    <p className="text-lg font-medium text-zinc-400">Nenhum imóvel compatível</p>
                  </div>
                )}
              </div>
            </main>
          </div>
        )}
      </div>

      {/* Modal Layer */}
      {selectedProperty && (
        <UnlockModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          property={selectedProperty}
        />
      )}
    </div>
  );
};

// --- Valuation Module (Algorithmic Appraiser Frontend) ---
const ValuationModule: React.FC = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ neighborhood: '', area: '', bedrooms: '' });
  const [result, setResult] = useState<number | null>(null);
  const [phone, setPhone] = useState('');

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    // Instant calculation (Backend removed)
    const basePrice = 8500; // Avg price per sqm mock
    const area = parseInt(formData.area) || 0;
    setResult(area * basePrice * (Math.random() * 0.2 + 0.9)); // Randomize slightly
    setStep(2);
  };

  const handleUnlockResult = (e: React.FormEvent) => {
    e.preventDefault();
    // Instant redirection
    const message = `Olá, solicito a avaliação detalhada do meu imóvel em ${formData.neighborhood} (${formData.area}m²). Valor estimado preliminar: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result || 0)}`;
    window.open(`https://wa.me/${BROKER_PHONE}?text=${encodeURIComponent(message)}`, '_blank');
  };

  return (
    <div className="w-full max-w-2xl mx-auto pt-32 pb-20 px-6">
      <div className="bg-[#121212] border border-zinc-800 rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-blue-600/20 rounded-lg flex items-center justify-center">
            <Calculator className="text-blue-500" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Algorithmic Appraiser</h2>
            <p className="text-zinc-400 text-xs">Inteligência artificial baseada em dados da Lopes</p>
          </div>
        </div>

        {step === 1 && (
          <form onSubmit={handleCalculate} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Bairro</label>
              <select
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-3 text-white focus:border-blue-500 outline-none"
                required
                onChange={(e) => setFormData({ ...formData, neighborhood: e.target.value })}
              >
                <option value="">Selecione...</option>
                {NEIGHBORHOODS.map(n => <option key={n.name} value={n.name}>{n.name}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">Área Privativa (m²)</label>
                <input
                  type="number"
                  required
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-3 text-white focus:border-blue-500 outline-none"
                  onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">Quartos</label>
                <select
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-3 text-white focus:border-blue-500 outline-none"
                  onChange={(e) => setFormData({ ...formData, bedrooms: e.target.value })}
                >
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4+</option>
                </select>
              </div>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-lg transition-all flex justify-center"
            >
              Calcular Valor de Mercado
            </button>
          </form>
        )}

        {step === 2 && result && (
          <div className="text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8 relative overflow-hidden rounded-xl bg-zinc-900 border border-zinc-800 p-6">
              <div className="blur-md select-none opacity-50">
                <p className="text-sm text-zinc-400 mb-2">Valor Estimado de Venda</p>
                <h3 className="text-4xl font-bold text-white">R$ {result.toLocaleString()}</h3>
              </div>
              <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-[2px]">
                <Lock className="text-blue-500 w-8 h-8 mb-2" />
              </div>
            </div>

            <h3 className="text-xl font-bold text-white mb-2">Avaliação Pronta</h3>
            <p className="text-zinc-400 text-sm mb-6">
              Para receber o relatório completo em PDF com comparativos de mercado da sua região, confirme seu WhatsApp.
            </p>

            <form onSubmit={handleUnlockResult} className="space-y-4">
              <input
                type="tel"
                placeholder="Seu WhatsApp (DDD) 99999-9999"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-3 text-white text-center text-lg tracking-wider focus:border-blue-500 outline-none"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <button className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-4 rounded-lg transition-all flex items-center justify-center gap-2">
                <CheckCircle2 size={20} />
                Receber Avaliação no WhatsApp
              </button>
            </form>
            <button onClick={() => setStep(1)} className="mt-4 text-zinc-500 text-xs hover:text-white">
              Voltar para Calculadora
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Property Card with "PropertyGate" (Blur Logic) & Charts ---
const PropertyCard: React.FC<{ property: Property; onUnlock: () => void }> = ({ property, onUnlock }) => {
  const isLuxury = property.price >= 1500000;

  return (
    <div className="group bg-[#121212] border border-white/10 rounded-2xl overflow-hidden hover:border-blue-500/30 transition-all duration-500 flex flex-col relative hover:-translate-y-2 shadow-xl shadow-black/50">

      {/* Image Section */}
      <div className="relative aspect-[4/3] overflow-hidden bg-zinc-900">
        <div className="absolute inset-0 bg-gradient-to-t from-[#121212] via-transparent to-transparent z-10 opacity-80" />
        <img
          src={property.imageUrl}
          alt={property.title}
          loading="lazy"
          className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-1000"
        />
        <div className="absolute top-4 w-full flex justify-center z-20">
          <span className="bg-black/70 backdrop-blur-md text-white border border-white/10 text-[10px] font-bold px-3 py-1.5 rounded-full uppercase tracking-widest flex items-center gap-2 shadow-lg">
            <MapPin size={10} className="text-blue-400" />
            {property.location.neighborhood}
          </span>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6 pb-8 flex flex-col flex-1">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white leading-snug mb-2 group-hover:text-blue-400 transition-colors line-clamp-2 min-h-[3.5rem]">
            {property.aiGeneratedTitle || property.title}
          </h3>
          <p className="text-2xl font-light text-blue-400 tracking-tight">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(property.price)}
          </p>
        </div>

        {/* PropertyGate: Blurred Specs Wrapper */}
        <div className="relative w-full mb-6 border border-white/5 rounded-lg p-3 bg-zinc-900/30">
          {/* Blurred Content */}
          <div className="grid grid-cols-3 gap-2 text-center filter blur-[3px] opacity-60">
            <div className="flex flex-col items-center">
              <span className="text-[10px] text-zinc-500">Condomínio</span>
              <span className="text-xs text-zinc-300">R$ 1.200</span>
            </div>
            <div className="flex flex-col items-center border-l border-white/10">
              <span className="text-[10px] text-zinc-500">IPTU</span>
              <span className="text-xs text-zinc-300">R$ 350</span>
            </div>
            <div className="flex flex-col items-center border-l border-white/10">
              <span className="text-[10px] text-zinc-500">Andar</span>
              <span className="text-xs text-zinc-300">Alto</span>
            </div>
          </div>

          {/* Overlay Lock */}
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <div className="bg-black/60 backdrop-blur-sm px-3 py-1 rounded-full border border-white/10 flex items-center gap-1.5">
              <Lock size={10} className="text-yellow-500" />
              <span className="text-[9px] font-bold uppercase tracking-wider text-white">Private Info</span>
            </div>
          </div>
        </div>

        {/* Specs Visible */}
        <div className="flex items-center justify-between text-zinc-400 text-xs mb-6 px-2">
          <div className="flex items-center gap-1.5"><BedDouble size={14} /> {property.bedrooms} Quartos</div>
          <div className="flex items-center gap-1.5"><Maximize size={14} /> {property.area} m²</div>
          <div className="flex items-center gap-1.5"><ShieldCheck size={14} /> {property.type === 'house' ? 'Casa' : 'Apto'}</div>
        </div>

        {/* Price History Mini Chart */}
        <div className="h-16 w-full mb-4 opacity-50 hover:opacity-100 transition-opacity">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={property.priceHistory}>
              <defs>
                <linearGradient id={`grad${property.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="price" stroke="#2563eb" fill={`url(#grad${property.id})`} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <button
          onClick={onUnlock}
          className={`w-full py-3 rounded-lg font-bold text-xs uppercase tracking-[0.15em] transition-all duration-300 flex items-center justify-center gap-2 group/btn
            ${isLuxury
              ? 'bg-white text-black hover:bg-blue-50'
              : 'bg-zinc-800 text-zinc-300 hover:bg-white hover:text-black'
            }`}
        >
          {isLuxury ? "Solicitar Acesso" : "Desbloquear Detalhes"}
          <ChevronRight size={14} className="group-hover/btn:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};

export default App;