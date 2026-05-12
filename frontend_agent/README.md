## 📋 Что сделано

• **`types/index.ts`** — все TypeScript-интерфейсы проекта: Product, Review, OrderFormData, FilterState, HeroVariant. Единый источник типов для всех компонентов.

• **`data/products.ts`** — массив из 12 товаров с полными данными (название, метка, описание, состав, цена, категория, цвет, размер). Импортируется в Catalog.tsx.

• **`components/Hero.tsx`** — три варианта Hero (A/B/C) с переключением через props. Таймер обратного отсчёта, плашка доверия, CTA-кнопка с якорем на каталог.

• **`components/Catalog.tsx`** — сетка карточек с фильтрами по поводу/цене/цвету/размеру. Вся фильтрация через useState без перезагрузки. Карточка открывает модальное окно с деталями.

• **`components/Benefits.tsx`** — расширенный блок преимуществ с анимированными счётчиками (Intersection Observer) и иконками SVG.

• **`components/Reviews.tsx`** — карусель из 6 отзывов со звёздным рейтингом, фото-аватарами через placeholder, автопрокруткой.

• **`components/OrderForm.tsx`** — форма заказа с валидацией, localStorage для сохранения данных при обновлении, 6 полей, без регистрации.

• **`components/Footer.tsx`** — контакты, мессенджеры, адрес, соцсети, копирайт.

• **`App.tsx`** — корневой компонент, собирает все секции, sticky-навигация с плавной прокруткой по якорям, определяет вариант Hero.

• **Архитектура** — mobile-first, Tailwind CSS, компонентная структура, все данные отделены от UI, зависимости только сверху вниз (App → компоненты → data/types).

---

## `types/index.ts`

---

## `data/products.ts`

---

## `components/Hero.tsx`

---

## `components/Catalog.tsx`

```typescript
// src/components/Catalog.tsx

import React, { useState, useMemo, useCallback } from 'react';
import { Product, FilterState, ProductCategory, ProductColor, ProductSize } from '../types';
import { products } from '../data/products';

const CATEGORIES: Array<ProductCategory | 'Все'> = [
  'Все',
  'Романтика',
  'День рождения',
  'Свадьба',
  'Корпоратив',
  'Просто так',
];
const COLORS: Array<ProductColor | 'Все'> = [
  'Все',
  'Красный',
  'Розовый',
  'Белый',
  'Жёлтый',
  'Фиолетовый',
  'Смешанный',
];
const SIZES: Array<ProductSize | 'Все'> = ['Все', 'Маленький', 'Средний', 'Большой'];
const MAX_PRICE = 8000;

const labelStyles: Record<string, string> = {
  ХИТ: 'bg-rose-600 text-white',
  НОВИНКА: 'bg-emerald-500 text-white',
  ПОПУЛЯРНОЕ: 'bg-amber-500 text-white',
};

/* ──────────── Product Card ──────────── */
interface ProductCardProps {
  product: Product;
  onSelect: (p: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onSelect }) => (
  <article className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden flex flex-col group">
    <div className="relative overflow-hidden h-56">
      <img
        src={product.image}
        alt={product.name}
        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        loading="lazy"
      />
      <span
        className={`absolute top-3 left-3 text-xs font-bold px-2.5 py-1 rounded-full ${labelStyles[product.label]}`}
      >
        {product.label}
      </span>
    </div>

    <div className="p-4 flex flex-col flex-1">
      <h3 className="font-bold text-gray-900 text-lg mb-1">{product.name}</h3>
      <p className="text-gray-500 text-sm leading-relaxed line-clamp-2 mb-3 flex-1">
        {product.description}
      </p>
      <div className="flex items-center justify-between mt-auto">
        <span className="text-2xl font-bold text-rose-600">
          {product.price.toLocaleString('ru-RU')} ₽
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => onSelect(product)}
            className="text-sm text-gray-500 hover:text-rose-600 underline transition-colors"
          >
            Детали
          </button>
          <a
            href="#order"
            className="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-xl transition-colors"
          >
            Заказать
          </a>
        </div>
      </div>
    </div>
  </article>
);

/* ──────────── Modal ──────────── */
interface ModalProps {
  product: Product;
  onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ product, onClose }) => (
  <div
    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    onClick={onClose}
  >
    <div
      className="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden"
      onClick={(e) => e.stopPropagation()}
    >
      <img src={product.image} alt={product.name} className="w-full h-64 object-cover" />
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h2 className="text-2xl font-bold text-gray-900">{product.name}</h2>
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${labelStyles[product.label]}`}>
            {product.label}
          </span>
        </div>
        <p className="text-gray-600 mb-4 leading-relaxed">{product.description}</p>
        <div className="bg-rose-50 rounded-xl p-4 mb-6">
          <p className="text-sm font-semibold text-gray-700 mb-1">Состав:</p>
          <p className="text-sm text-gray-600">{product.composition}</p>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-3xl font-bold text-rose-600">
            {product.price.toLocaleString('ru-RU')} ₽
          </span>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Закрыть
            </button>
            <a
              href="#order"
              onClick={onClose}
              className="bg-rose-600 hover:bg-rose-700 text-white font-semibold px-6 py-2 rounded-xl transition-colors"
            >
              Заказать
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
);

/* ──────────── Catalog ──────────── */
const Catalog: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    category: 'Все',
    maxPrice: MAX_PRICE,
    color: 'Все',
    size: 'Все',
  });
  const [selected, setSelected] = useState<Product | null>(null);

  const filtered = useMemo(
    () =>
      products.filter(
        (p) =>
          (filters.category === 'Все' || p.category === filters.category) &&
          p.price <= filters.maxPrice &&
          (filters.color === 'Все' || p.color === filters.color) &&
          (filters.size === 'Все' || p.size === filters.size)
      ),
    [filters]
  );

  const setCategory = useCallback(
    (c: ProductCategory | 'Все') => setFilters((f) => ({ ...f, category: c })),
    []
  );

  const resetFilters = () =>
    setFilters({

---
## 📁 Созданные файлы
- [index.ts](index.ts)
- [products.ts](products.ts)
- [Hero.tsx](Hero.tsx)