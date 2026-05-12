export type ProductLabel = 'ХИТ' | 'НОВИНКА' | 'ПОПУЛЯРНОЕ';
export type ProductCategory = 'Романтика' | 'День рождения' | 'Свадьба' | 'Корпоратив' | 'Просто так';
export type ProductColor = 'Красный' | 'Розовый' | 'Белый' | 'Жёлтый' | 'Смешанный' | 'Фиолетовый';
export type ProductSize = 'Маленький' | 'Средний' | 'Большой';
export type HeroVariant = 'A' | 'B' | 'C';

export interface Product {
  id: number;
  name: string;
  label: ProductLabel;
  description: string;
  composition: string;
  price: number;
  category: ProductCategory;
  color: ProductColor;
  size: ProductSize;
  image: string;
}

export interface Review {
  id: number;
  name: string;
  date: string;
  rating: number;
  text: string;
  avatar: string;
  bouquet: string;
}

export interface OrderFormData {
  name: string;
  phone: string;
  address: string;
  date: string;
  time: string;
  wishes: string;
}

export interface FilterState {
  category: ProductCategory | 'Все';
  maxPrice: number;
  color: ProductColor | 'Все';
  size: ProductSize | 'Все';
}

export interface BenefitItem {
  icon: string;
  title: string;
  description: string;
}

export interface CounterItem {
  value: string;
  label: string;
  description: string;
}