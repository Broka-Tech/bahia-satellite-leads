import React from 'react';
import { FilterState } from '../types';
import { NEIGHBORHOODS } from '../constants';
import { Search, Filter, MapPin, Banknote, BedDouble, X, RotateCcw } from 'lucide-react';

interface FiltersProps {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  activeCount: number;
  className?: string;
  onClose?: () => void;
}

export const Filters: React.FC<FiltersProps> = ({ filters, setFilters, activeCount, className = "", onClose }) => {
  
  const handleProfileChange = (profile: FilterState['profile']) => {
    let range: [number, number] = [0, 5000000];
    
    switch (profile) {
      case 'economic': range = [0, 350000]; break;
      case 'standard': range = [350000, 900000]; break;
      case 'luxury': range = [900000, 2500000]; break;
      case 'ultra-luxury': range = [2500000, 15000000]; break;
    }

    setFilters(prev => ({ ...prev, profile, priceRange: range }));
  };

  const toggleNeighborhood = (name: string) => {
    setFilters(prev => {
      const current = prev.neighborhoods;
      if (current.includes(name)) {
        return { ...prev, neighborhoods: current.filter(n => n !== name) };
      } else {
        return { ...prev, neighborhoods: [...current, name] };
      }
    });
  };

  const handleBedroomChange = (num: number) => {
    setFilters(prev => ({
      ...prev,
      bedrooms: prev.bedrooms === num ? null : num // Toggle logic
    }));
  };

  // Reset Logic
  const handleClearFilters = () => {
    setFilters({
      priceRange: [0, 5000000],
      neighborhoods: [],
      profile: 'all',
      bedrooms: null
    });
  };

  // Check if any filter is active to conditionally show the Clear button
  const hasActiveFilters = 
    filters.profile !== 'all' || 
    filters.neighborhoods.length > 0 || 
    filters.bedrooms !== null || 
    filters.priceRange[0] !== 0 ||
    filters.priceRange[1] !== 5000000;

  return (
    <aside className={`flex flex-col h-full bg-[#09090b] ${className}`}>
      <div className="mb-6 flex items-center justify-between min-h-[32px]">
        <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 uppercase tracking-wider">
          <Filter size={14} className="text-primary" />
          Refinar Busca
        </h3>
        
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button 
              onClick={handleClearFilters}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider text-white bg-red-600 hover:bg-red-700 transition-colors shadow-md"
            >
              <RotateCcw size={12} />
              Limpar
            </button>
          )}
          
          {onClose && (
            <button onClick={onClose} className="lg:hidden p-1 text-zinc-400 hover:text-white transition-colors">
              <X size={20} />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-8 flex-1 overflow-y-auto scrollbar-thin pr-2">
        {/* Profile Selector */}
        <div>
          <label className="text-xs font-medium text-zinc-400 mb-3 block">
            Perfil do Investimento
          </label>
          <div className="grid grid-cols-2 gap-2">
            {['economic', 'standard', 'luxury', 'ultra-luxury'].map((p) => (
              <button
                key={p}
                onClick={() => handleProfileChange(p as any)}
                className={`px-3 py-2 rounded-md text-[11px] font-medium border transition-all capitalize
                  ${filters.profile === p 
                    ? 'bg-white text-black border-white shadow-sm' 
                    : 'bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'}`}
              >
                {p.replace('ultra-luxury', 'Ultra Luxo').replace('luxury', 'Alto Padrão').replace('standard', 'Médio').replace('economic', 'Entrada')}
              </button>
            ))}
          </div>
        </div>

        {/* Price Range */}
        <div>
          <label className="flex items-center gap-2 text-xs font-medium text-zinc-400 mb-3">
            <Banknote size={14} className="text-zinc-600" />
            Faixa de Valor Máximo
          </label>
          <input
            type="range"
            min="150000"
            max="5000000"
            step="50000"
            value={filters.priceRange[1]}
            onChange={(e) => setFilters(prev => ({ 
              ...prev, 
              priceRange: [prev.priceRange[0], parseInt(e.target.value)],
              profile: 'all' // Reset profile when manually adjusting slider
            }))}
            className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-white hover:accent-zinc-300"
          />
          <div className="flex justify-between mt-3 text-xs text-zinc-300 font-mono bg-zinc-900/50 p-2 rounded border border-zinc-800/50">
            <span>Até:</span>
            <span className="font-bold text-primary">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact' }).format(filters.priceRange[1])}</span>
          </div>
        </div>

        {/* Bedrooms Filter */}
        <div>
          <label className="flex items-center gap-2 text-xs font-medium text-zinc-400 mb-3">
            <BedDouble size={14} className="text-zinc-600" />
            Dormitórios
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((num) => (
              <button
                key={num}
                onClick={() => handleBedroomChange(num)}
                className={`flex-1 py-2 rounded-md text-xs font-bold border transition-all
                  ${filters.bedrooms === num
                    ? 'bg-white text-black border-white shadow-sm' 
                    : 'bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'
                  }`}
              >
                {num === 5 ? '5+' : num}
              </button>
            ))}
          </div>
        </div>

        {/* Neighborhoods */}
        <div className="flex-1 flex flex-col min-h-0">
          <label className="flex items-center gap-2 text-xs font-medium text-zinc-400 mb-3">
            <MapPin size={14} className="text-zinc-600" />
            Localização
          </label>
          <div className="relative mb-3">
            <Search size={14} className="absolute left-3 top-3 text-zinc-500" />
            <input 
              type="text" 
              placeholder="Filtrar bairros..." 
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:border-zinc-600 outline-none placeholder:text-zinc-600 transition-colors"
            />
          </div>
          <div className="space-y-1">
            {NEIGHBORHOODS.map((nb) => (
              <label key={nb.name} className="flex items-center gap-3 p-2 hover:bg-zinc-900/50 rounded-md cursor-pointer group transition-colors">
                <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors
                  ${filters.neighborhoods.includes(nb.name) ? 'bg-primary border-primary' : 'border-zinc-700 group-hover:border-zinc-500'}`}>
                  {filters.neighborhoods.includes(nb.name) && <div className="w-2 h-2 bg-white rounded-sm" />}
                </div>
                <input 
                  type="checkbox" 
                  className="hidden"
                  checked={filters.neighborhoods.includes(nb.name)}
                  onChange={() => toggleNeighborhood(nb.name)}
                />
                <div className="flex flex-col">
                  <span className={`text-xs transition-colors ${filters.neighborhoods.includes(nb.name) ? 'text-white font-medium' : 'text-zinc-400'}`}>
                    {nb.name}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-white/5 mt-auto">
        <div className="flex items-center justify-between text-zinc-500 text-xs">
          <span>Resultados:</span>
          <span className="text-white font-mono">{activeCount}</span>
        </div>
      </div>
    </aside>
  );
};