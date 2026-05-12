import React, { useState, useEffect } from 'react';
import { HeroVariant } from '../types';

interface HeroProps {
  variant?: HeroVariant;
}

interface HeroContent {
  headline: string;
  subheadline: string;
  cta: string;
}

const heroContent: Record<HeroVariant, HeroContent> = {
  A: {
    headline: 'Свежие цветы. Доставка за 2 часа.',
    subheadline:
      'Букеты из живых цветов прямо с плантаций — от 1 500 рублей. Оформите заказ за 2 минуты, и курьер уже в пути.',
    cta: 'Выбрать букет →',
  },
  B: {
    headline: 'Подарите чувства, которые не забудут.',
    subheadline:
      'Каждый букет — это история. Мы собираем её вручную и доставляем вовремя — даже если вы вспомнили о празднике сегодня утром.',
    cta: 'Найти свой букет →',
  },
  C: {
    headline: 'Цветы, которые точно понравятся.',
    subheadline:
      'Гарантия свежести на 7 дней или вернём деньги. Доставка по городу — бесплатно от 3 000 рублей.',
    cta: 'Заказать сейчас →',
  },
};

interface TimeLeft {
  hours: number;
  minutes: number;
  seconds: number;
}

function getTimeUntilMidnight(): TimeLeft {
  const now = new Date();
  const midnight = new Date();
  midnight.setHours(22, 0, 0, 0);
  if (now >= midnight) {
    midnight.setDate(midnight.getDate() + 1);
  }
  const diff = Math.max(0, midnight.getTime() - now.getTime());
  return {
    hours: Math.floor(diff / 3_600_000),
    minutes: Math.floor((diff % 3_600_000) / 60_000),
    seconds: Math.floor((diff % 60_000) / 1000),
  };
}

const Hero: React.FC<HeroProps> = ({ variant = 'A' }) => {
  const content = heroContent[variant];
  const [timeLeft, setTimeLeft] = useState<TimeLeft>(getTimeUntilMidnight());

  useEffect(() => {
    const id = setInterval(() => setTimeLeft(getTimeUntilMidnight()), 1000);
    return () => clearInterval(id);
  }, []);

  const pad = (n: number) => String(n).padStart(2, '0');

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-rose-50 via-pink-50 to-rose-100"
    >
      {/* Background decorative circles */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-rose-200 rounded-full opacity-20 translate-x-1/3 -translate-y-1/3" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-pink-300 rounded-full opacity-15 -translate-x-1/3 translate-y-1/3" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Text block */}
          <div className="text-center lg:text-left">
            {/* Promo badge */}
            <div className="inline-flex items-center gap-2 bg-rose-600 text-white text-sm font-medium px-4 py-2 rounded-full mb-6 shadow-md">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              Бесплатная доставка сегодня до 22:00
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              {content.headline.split('.').map((part, i, arr) => (
                <span key={i}>
                  {part}
                  {i < arr.length - 1 && (
                    <>
                      .<br />
                    </>
                  )}
                </span>
              ))}
            </h1>

            <p className="text-lg sm:text-xl text-gray-600 mb-8 leading-relaxed max-w-xl mx-auto lg:mx-0">
              {content.subheadline}
            </p>

            {/* CTA + secondary button */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-8">
              <a
                href="#catalog"
                className="inline-block bg-rose-600 hover:bg-rose-700 text-white font-semibold text-lg px-8 py-4 rounded-2xl shadow-lg hover:shadow-rose-300 transition-all duration-200 hover:-translate-y-0.5"
              >
                {content.cta}
              </a>
              <a
                href="#order"
                className="inline-block bg-white hover:bg-gray-50 text-rose-600 font-semibold text-lg px-8 py-4 rounded-2xl shadow border border-rose-200 transition-all duration-200 hover:-translate-y-0.5"
              >
                Быстрый заказ
              </a>
            </div>

            {/* Trust badge */}
            <div className="flex flex-wrap items-center gap-3 justify-center lg:justify-start text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <span className="text-amber-400">★★★★★</span>
                <span className="font-medium text-gray-700">4.9</span>
              </span>
              <span className="text-gray-300">|</span>
              <span>2 840 заказов</span>
              <span className="text-gray-300">|</span>
              <span>7 дней гарантии свежести</span>
            </div>
          </div>

          {/* Image + timer block */}
          <div className="flex flex-col items-center gap-6">
            <div className="relative w-full max-w-md mx-auto">
              <div className="absolute inset-0 bg-rose-300 rounded-3xl rotate-3 opacity-30" />
              <img
                src="https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=600&h=600&fit=crop"
                alt="Свежий букет роз"
                className="relative z-10 w-full h-80 sm:h-96 object-cover rounded-3xl shadow-2xl"
                loading="eager"
              />
              <div className="absolute -bottom-4 -right-4 z-20 bg-white rounded-2xl shadow-xl px-4 py-3 flex items-center gap-2">
                <span className="text-2xl">🚚</span>
                <div>
                  <p className="text-xs text-gray-500">Доставка за</p>
                  <p className="text-sm font-bold text-rose-600">2 часа</p>
                </div>
              </div>
            </div>

            {/* Countdown timer */}
            <div className="bg-white rounded-2xl shadow-md px-6 py-4 w-full max-w-sm">
              <p className="text-center text-sm text-gray-500 mb-3">
                Акция «Бесплатная доставка» заканчивается через:
              </p>
              <div className="flex justify-center gap-3">
                {[
                  { val: pad(timeLeft.hours), label: 'часов' },
                  { val: pad(timeLeft.minutes), label: 'минут' },
                  { val: pad(timeLeft.seconds), label: 'секунд' },
                ].map(({ val, label }) => (
                  <div key={label} className="flex flex-col items-center">
                    <span className="bg-rose-600 text-white text-2xl font-bold w-14 h-14 rounded-xl flex items-center justify-center tabular-nums">
                      {val}
                    </span>
                    <span className="text-xs text-gray-400 mt-1">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;